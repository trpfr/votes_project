import json
import os
from rich import print
from rich.panel import Panel
from rich.text import Text
from collections import defaultdict
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_public_key
import crypto
import sqlite3

"""
Main module. Contains all the main functions that are used for voting.
"""


def execute_query(query, params=()):
    """
    Executes SQL query and returns the result. This function is used to simplify the code.
    """
    with sqlite3.connect("voting_database.db") as conn:
        cursor = conn.cursor()  # Create cursor - object that allows us to execute queries
        cursor.execute(query, params)  # Execute query with parameters
        result = cursor.fetchall()  # Get the result
        conn.commit()  # Commit changes (if there are any)
    return result


def clear_console():
    """
    Function for clearing the console. Made for beauty.
    Work for Unix, Mac and Windows
    """
    system = os.name
    if system == 'posix':
        os.system('clear')  # For Unix and Mac
    elif system == 'nt':
        os.system('cls')  # For Windows
    else:
        print("\n" * 100)  # For others systems (just print 100 new lines)


def error(message):
    """
    Function for formatting error message. Returns formatted error message with red border and
    error emoji. Made with rich library.
    """
    error_text = Text("⚠️ " + message, style="bold red")
    error_panel = Panel(error_text, title="Error", border_style="red")
    return error_panel


"""
The following functions are used to get data from the database. They are used to simplify the code.
"""


def list_of_tally_centers():
    """Getter for list of all tally centers."""
    return execute_query("SELECT * FROM tally_centers")


def list_of_candidates():
    """Getter for list of all candidates."""
    return execute_query("SELECT * FROM candidates")


def get_voter(passport):
    """Getter for voter by passport ID."""
    return execute_query("SELECT * FROM voters WHERE id=?", (passport,))


def get_tally_center(tally_center_id):
    """Getter for tally center by ID."""
    return execute_query("SELECT * FROM tally_centers WHERE id=?", (tally_center_id,))


def to_vote(passport, private_key_serialized, candidate_id, tally_center_id):
    """
    Function for voting. This function is called when user wants to vote.
    Return codes:
    1/True - success
    0 - no such passport in database
    -1 - private key in wrong format
    -2 - double voting
    -3 - wrong public key of voter
    -4 - wrong private key of voter
    -5 - wrong public key of tally center
    -6 - voting is over
    """
    # Check if voting is over
    results = execute_query("SELECT COUNT(*) FROM tally_results")[0][0]
    if results != 0:
        """
        If there are any results in tally_results table, it means that voting is over.
        """
        return -6
    # Check if voter exists
    try:
        voter = get_voter(passport)[0]
    except:
        # If there is no such passport in database
        return 0
    try:
        """
        Try to load private key. If it fails - return -1. It can happen if user gave wrong private key and tries to vote
        with it. So he didn't take someone else's key or something like that, but tries to use something completely
        different (like discount card instead of private card).
                
        Here the system does "deserialization" of the key - we transform it from string to object that can be used for
        decryption. So if the key is wrong, it won't be able to be deserialized and we will get an error.
        """
        user_private_key = serialization.load_pem_private_key(
            private_key_serialized,
            password=None,
            backend=default_backend()
        )
    except:
        # If private key is in wrong format
        return -1

    # Load master phrase from file
    """As mentioned earlier, to implement ZKP (to verify that a user has the right to vote and doesn't vote twice, 
    without revealing their choice), I use a master phrase. I encrypt it using the private key and place it in the 
    database when voting. Accordingly, if the master phrase is in the database, it means the user has already voted.

    To check that a user can vote, I simply "run" the master phrase back and forth. First, I encrypt it with the public 
    key, then decrypt it with the private key. If I get the same phrase at the output, it means the user truly has the 
    right to vote."""
    with open("master_phrase.txt", "r") as master_phrase_file:
        master_phrase = master_phrase_file.read()
    # Find ZKP record in database. If it exists - user has already voted
    if voter[3]:
        zkp = voter[3]
        # Try to decrypt ZKP
        decrypted_zkp = crypto.decrypt_vote(zkp, user_private_key)
        """
        If decrypted ZKP is equal to master phrase, it means that ZKP was real. If it's not - it means that ZKP was
        fake. In this case we should replace ZKP with None (because it's fake) and continue voting.
        """

        if decrypted_zkp == master_phrase:
            return -2  # If ZKP record was real - return -2 (double voting)
        else:
            # If ZKP was fake - replace it with None
            execute_query("UPDATE voters SET zkp=? WHERE id=?", (None, passport))
    """
    If we are here, it means that user has not voted yet. So we should check if he can vote. To do this, we will try to
    encrypt master phrase with public key and then decrypt it with private key. If we get the same phrase - user can
    vote, if not - he can't.
    """
    try:
        # Public key from DB
        user_public_key = load_pem_public_key(voter[2].encode('utf-8'))
    except:
        return -3  # Wrong public key of voter in DB (it's mean that DB was changed illegally)
    zkp = crypto.encrypt_vote(master_phrase, user_public_key)  # Encrypt master phrase with public key
    if crypto.decrypt_vote(zkp, user_private_key) != master_phrase:
        return -4  # If decrypted ZKP is not equal to master phrase - user can't vote

    # If we are here, it means that user can vote.
    public_key = load_pem_public_key(
        execute_query("SELECT public_key FROM tally_centers WHERE id=?", (tally_center_id,))[0][0].encode('utf-8'))

    # Encrypt vote (candidate ID) with public key of tally center
    encrypted_vote = crypto.encrypt_vote(candidate_id, public_key)
    if encrypted_vote is None:
        # Wrong public key of tally center
        return -5
    # Commit encrypted vote to database
    execute_query("INSERT INTO votes (encrypted_vote, tally_center_id) VALUES (?, ?)",
                  (encrypted_vote, tally_center_id))
    # Commit ZKP to database (to prevent double voting)
    execute_query("UPDATE voters SET zkp=? WHERE id=?", (zkp, passport))
    return True


# Function for counting votes
def tally_votes(tally_center_id, tally_center_private_key):
    """
    Function for counting votes. Takes tally center ID and tally center private key. This function will process all
    votes that were made on this tally center and decrypt them using tally center private key. Then it will count
    results and write them to tally_results table in DB.
    """
    # Check if tally center exists
    tally_center = get_tally_center(tally_center_id)[0]
    if not tally_center:
        # Return 0 if tally center doesn't exist
        return 0
    try:
        # Try to load private key. If it fails - return -1 - wrong private key
        private_key = serialization.load_pem_private_key(
            tally_center_private_key,
            password=None,
            backend=default_backend()
        )
    except:
        return -1

    # Get all encrypted votes from database for this tally center
    encrypted_votes = execute_query("SELECT encrypted_vote FROM votes WHERE tally_center_id=?", (tally_center_id,))

    # Decrypt all votes and count results
    # results - dictionary for counting results. Key - candidate ID, value - number of votes for this candidate
    results = defaultdict(int)  # int - default value for dictionary (starts from 0)
    for encrypted_vote_data in encrypted_votes:
        # Trying to decrypt all votes
        decrypted_vote = crypto.decrypt_vote(encrypted_vote_data[0], private_key)
        if decrypted_vote is None:
            # If decryption failed - wrong private key or corrupted vote
            return -2
        """
        If we are here - decryption was successful. Add 1 to the number of votes for this candidate.
        """
        results[decrypted_vote] += 1

    """
    Because results are a complex structure - dictionary, not just, for example, a number, we cannot write the results
    directly to the database. First, we must convert them into something more understandable for SQLLite, for example,
    in JSON format. To do this, we use the json library.
    """
    results_str = json.dumps(results)
    """
    Because we will store the results in unencrypted form (candidate ID and number of votes for him), the attacker can
    easily hack them by simply writing his own results. Of course, we do not want this, for this we sign the results
    using the private key of the tally center. To do this, we use the sign_results function from the crypto file. This
    function returns a signature in base64 format. We write the results and the signature to the database. (see the
    crypto.py file)
    """
    execute_query("INSERT INTO tally_results (tally_center_id, result, signature) VALUES (?, ?, ?)",
                  (tally_center_id, results_str, crypto.sign_results(results_str, private_key)))
    return True


# Function for checking votes
def check_votes():
    """
    This function immediately performs several roles: first, it returns us the results of the vote in a convenient
    form for each tally center. It also checks the signatures of the tally centers and returns the result of the check,
    thus preventing changes to the voting results in the database. In fact, this function is the implementation of the
    6th item from the technical task.
    """
    final_results = []  # List for final results
    for tally_center in list_of_tally_centers():
        """
        Do it for each tally center. Store his id and name in variables center_id and center_name respectively.
        """
        center_id = tally_center[0]
        center_name = tally_center[1]

        #  Get results from database
        try:
            tally_results = \
                execute_query("SELECT * FROM tally_results WHERE tally_center_id=?",
                              (center_id,))[
                    0]
        except:
            # If there are no results for this tally center - return 0. It means that voting is not finished yet
            return 0

        #  Get public key of tally center from database
        public_key = load_pem_public_key(tally_center[2].encode('utf-8'))
        if not crypto.verify_signature(tally_results[2], tally_results[3], public_key):
            # If signature is not valid - return -1 (voting results are corrupted or wrong public key)
            return -1

        # Convert results from JSON to dictionary
        results = json.loads(tally_results[2])
        #  List for results of each tally center
        center_results = []
        for candidate_id, votes_count in results.items():
            # Get name of candidate by his ID
            candidate_name = \
                execute_query("SELECT name FROM candidates WHERE id=?", (candidate_id,))[0][0]
            # Add results for this candidate to the list (id, name, votes count)
            center_results.append((candidate_id, candidate_name, votes_count))
        #  Add results for this tally center to the final list (id, name, results)
        final_results.append((center_id, center_name, center_results))
    return final_results


# Function for printing results (for simulation)
def print_votes():
    # Check and get results
    results = check_votes()
    # If results are not a list - return them (because results are not a list if it's error)
    if not isinstance(results, list):
        return results
    # Dictionary for counting total votes for each candidate
    total_votes = defaultdict(int)

    for center_id, center_name, center_results in results:
        """
        Print results for each candidate in each tally center.
        """
        print("{}".format(center_name))  # Name of center
        for candidate_id, candidate_name, votes in center_results:
            # Name of candidate: number of votes for him
            print("{}: {}".format(candidate_name, votes))
            # Add votes to total votes
            total_votes[candidate_name] += votes
        print("")  # Just new line

    # Print total votes
    print("Total votes:")
    for candidate_name, votes in total_votes.items():
        # Name of candidate: number of votes for him
        print("{}: {}".format(candidate_name, votes))
