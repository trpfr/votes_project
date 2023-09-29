# Файл настроек БД
import sqlite3

"""I could have physically created the Database myself once, but it's not very convenient, so I decided to create it 
programmatically. For this, I wrote a separate function that will create the DB according to the table schema if it 
hasn't been created yet. In my project, I use SQLite because it doesn't require installation and is convenient for 
small projects. In reality, the differences when working on other systems will be minor; for clarity, it's easier to 
use SQLite. Unlike most other databases, this one doesn't require complex setup and installation and stores data in a 
file, which I connect to in this function."""


def db_setup():
    # Connect to database
    conn = sqlite3.connect('voting_database.db')
    cursor = conn.cursor()

    # Create tables
    """
    Table schema (voters):

    id - a unique identifier of the voter (in my case - passport number).
    
    name - the name of the voter.
    
    public_key - the public key of the voter (for ZKP encryption). We can consider this as an "invitation ticket" for the 
    elections. When I make my choice, using the private key (we can say it's a kind of key-card for voting), 
    I encrypt the ZKP (I encrypt a certain phrase (set of characters) to prove that I voted without revealing my vote).
    
    zkp - zero-knowledge proof, a proof that the voter must provide to ensure their vote is accepted (to confirm the 
    officialness of the key). This field will only be filled after the vote has been cast, so I can always confirm that I 
    voted without revealing my choice. If there's an attempt to forge my vote, the zkp won't work because it can't be 
    decrypted using my public key.
    """
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS voters (
        id INTEGER PRIMARY KEY,  
        name TEXT NOT NULL,
        public_key TEXT NOT NULL UNIQUE,
        zkp TEXT
    )
    ''')

    """
    Table schema (votes):

    id - a unique identifier of the vote.
    
    encrypted_vote - the vote encrypted using the public key of the tally center.
    
    tally_center_id - the identifier of the vote counting center. According to the conditions, I use them to ensure 
    sufficient anonymity of the voters. This way, they can vote at one of the centers of their choice, and each center 
    has its public and private keys, which are used to encrypt the votes.
    """

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY,
        encrypted_vote TEXT NOT NULL,
        tally_center_id INTEGER NOT NULL
    )
    ''')

    """
    Table schema (candidates):
    id - a unique identifier of the candidate.
    name - name of the candidate.
    """
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
    ''')

    """
    Table schema (tally_centers):
    id - a unique identifier of the vote counting center.
    name - the name of the vote counting center.
    public_key - the public key of the vote counting center (for encrypting votes).
    """
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tally_centers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        public_key TEXT NOT NULL
    )
    ''')

    """
    Table schema (tally_results):
    id - a unique identifier of the result.
    tally_center_id - the identifier of the vote counting center that counted the votes.
    result - the result of the vote count.
    signature - the signature of the vote counting center that counted the votes - to confirm that the votes weren't
    forged.
    """
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tally_results (
        id INTEGER PRIMARY KEY,
        tally_center_id INTEGER NOT NULL,
        result TEXT NOT NULL,
        signature TEXT NOT NULL
    )
    ''')

    # Save (commit) the changes
    conn.commit()
    conn.close()
