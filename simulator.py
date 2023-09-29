from interface import execute_query, to_vote, tally_votes, print_votes, error, list_of_tally_centers, list_of_candidates
import random


"""
Module for voting simulation.
It is used to demonstrate the functionality of our system, as well as to fill the database with test data.
"""


def voting_simulation():
    #  Get all voters, tally centers and candidates from database
    voters = execute_query("SELECT * FROM voters")
    tally_centers = list_of_tally_centers()
    candidates = list_of_candidates()

    # Voting for random candidate in random tally center for each voter
    for voter in voters:
        candidate = random.choice(candidates)
        tally_center = random.choice(tally_centers)
        # Load private key from user_keys/private_key_<id>.pem
        try:
            with open("user_keys/private_key_" + str(voter[0]) + ".pem", "rb") as key_file:
                voter_private_key = key_file.read()
        except:
            # If file was not found or corrupted, print error and continue
            print(error("Invalid path to key or file was corrupted!"))
            continue
        # Vote using to_vote function
        result = to_vote(voter[0], voter_private_key, candidate[0], tally_center[0])
        if result > 0:
            print("Voter #", voter[0], " voted")  # Print success message
        # Error handling
        elif result == 0:
            print(error("Voter #" + voter[0] + " could not vote - no such passport"))
        elif result == -1:
            print(error("Voter #" + voter[0] + " could not vote - wrong private key"))
        elif result == -2:
            print(error("Voter #" + voter[0] + " could not vote - double voting"))
        elif result == -3:
            print(error("Voter #" + voter[0] + " could not vote - wrong public key"))
        elif result == -4:
            print(error("Voter #" + voter[0] + " could not vote - wrong zkp. Bad private key"))
        elif result == -5:
            print(error("Voter #" + voter[0] + " could not vote - wrong tally center public key"))
        elif result == -6:
            print(error("Voter #" + voter[0] + " could not vote - voting already ended"))

    # Run tallying for each tally center
    for tally_center in tally_centers:
        # Load private key from tally_keys/private_key_<id>.pem
        try:
            with open("tally_keys/private_key_" + str(tally_center[0]) + ".pem", "rb") as key_file:
                tally_center_private_key = key_file.read()
        except:
            # If file was not found or corrupted, print error and continue
            print(error("Invalid path to key or file was corrupted!"))
            continue
        # Calculate votes using tally_votes function
        result = tally_votes(tally_center[0], tally_center_private_key)
        # Error handling
        if result == 0:
            print(error("Tally center #" + tally_center[0] + " not found!"))
        elif result == -1:
            print(error("Tally center #" + tally_center[0] + " has wrong private key!"))
        elif result == -2:
            print(error("Tally center #" + tally_center[0] + " has bad public key!"))

    # Voting ended, print results
    print("\nVotes tallied")
    print("\nResults:")

    # Use print_votes function to print results or error handling
    results = print_votes()

    # Error handling
    if results == 0:
        print(error("Voting was not completed. Not all centers tallied votes."))
    if results == -1:
        print(error("DATA CORRUPTION DETECTED! THERE IS WRONG SIGNATURE OR RESULTS IN DATABASE!"))
