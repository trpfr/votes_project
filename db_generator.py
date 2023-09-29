import random
import sqlite3
import crypto

"""
For the demonstration of the system's operation and to avoid manually filling the database every time, I created a 
database generation file. It populates the database with random data. To start, you need to execute the 
data_generation() function.
"""


def data_generation():
    # Connecting to the database
    conn = sqlite3.connect('voting_database.db')
    cursor = conn.cursor()

    # Random names
    names = [
        "Adele",
        "Beyonce",
        "Celine",
        "Dua",
        "Ella",
        "Fergie",
        "Gwen",
        "Halsey",
        "Iggy",
        "JLo",
        "Katy",
        "Lady Gaga",
        "Madonna",
        "Nicki",
        "Olivia",
        "Pink"]

    # Random lastnames
    lastnames = [
        "Adkins",
        "Knowles",
        "Dion",
        "Lipa",
        "Fitzgerald",
        "Fergie",
        "Stefani",
        "Frangipane",
        "Azalea",
        "Lopez",
        "Perry",
        "Germanotta",
        "Ciccone",
        "Minaj",
        "Rodrigo",
        "Moore"
    ]

    # List of candidates (in this case only two)
    candidates = [
        "Republicans",
        "Democrats"
    ]

    # Count of voters
    count_of_voters = 100

    # Generating random names (combination of first and last names)
    random_names = [(random.choice(names), random.choice(lastnames)) for _ in range(count_of_voters)]

    # Creating voters
    for first, last in random_names:
        # Full name
        full_name = f"{first} {last}"

        # Random passport number
        passport = random.randint(100000, 999999)

        # Key generation
        """
        Each voter must have a public key (an invitation to vote) and a private key (a kind of key card to confirm 
        that they have the right to vote). The public key is stored in the database, while the private key is saved 
        in a file.

        I use them to implement the zero-knowledge proof (ZKP) system. This system allows proving a fact without 
        revealing any other information. In my case, I use it to prove that the voter has the right to vote without 
        revealing their identity. Also, to confirm that the voter has already voted, preventing them from voting 
        twice.
        """
        public_key, private_key = crypto.generate_keys()
        pem = crypto.serialize_private_key(private_key)

        """
        Saving the private key to a file 
        (just for demonstration, in real implementation it should be stored as private card
        """
        with open(f"user_keys/private_key_{passport}.pem", "wb") as f:
            f.write(pem)

        # Saving the voter to the database
        cursor.execute("INSERT INTO voters (id, name, public_key) VALUES (?, ?, ?)", (passport,
                                                                                      full_name,
                                                                                      crypto.serialize_public_key(
                                                                                          public_key)))

    # Creating candidates
    for candidate in candidates:
        cursor.execute("INSERT INTO candidates (name) VALUES (?)", (candidate,))

    # Creating voting centers
    # Count of voting centers
    tally_centers_count = 5
    for i in range(tally_centers_count):
        # Generating keys for each voting center (for encryption and decryption of votes)
        public_key, private_key = crypto.generate_keys()

        # Generating name for each voting center (for demonstration just Tally center № + number)
        name = f"Tally center №{i + 1}"

        # Saving voting center to the database
        cursor.execute("INSERT INTO tally_centers (name, public_key) VALUES (?, ?)",
                       (name, crypto.serialize_public_key(public_key)))

        # Saving private key to the file (serializing and saving to the file)
        pem = crypto.serialize_private_key(private_key)
        with open(f"tally_keys/private_key_{i + 1}.pem", "wb") as f:
            f.write(pem)

    # Committing changes and closing connection
    conn.commit()
    conn.close()

    # Generating master phrase
    """
    This is just a random set of bytes that I later encrypt and decrypt to implement ZKP (see crypto.py)
    """
    master_phrase = crypto.generate_phrase()
    with open("master_phrase.txt", "w") as f:
        f.write(master_phrase)
