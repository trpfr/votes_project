## Author
Evgeny Piratinsky

## Project Description

This is my college project, which demonstrates how cryptographic practices can be applied to a voting system.
The system assumes we have voters and centers responsible for counting votes. Using multiple counting centers ensures voter anonymity and prevents collusion among centers to manipulate vote results. Voters can only choose between two candidates. To avoid political discussions, let's assume we're simulating the US political system where the only candidates are Democrats and Republicans. In our project, we store the keys of voting centers and voters as regular files within the system. In reality, such data would be stored as key-cards and election invitations.

## The voting system must have the following properties:
### 1. Only authorized voters can vote
Implemented using ZKP with a private-public key pair (RSA encryption). We encrypt a "master phrase" using the public key (election invitation) and decode it using the private key (key-card for voting). This ensures only authorized voters in the database with valid public keys can vote.

### 2. No one can vote more than once
Also implemented using ZKP with RSA encryption. If someone has already voted, the encrypted master phrase is stored in the database, preventing them from voting again.

### 3. No interested party can determine how someone else voted
Implemented using RSA encryption. Each vote is encrypted using the public key of the voting center and can only be decrypted with the corresponding private key. The database only stores the selected candidate, not the voter's identity. To ensure encrypted votes look different, we use OAEP, adding random data to the encrypted information.

### 4. No one can duplicate another's vote
Due to the implementation of point 2, no one can vote on behalf of someone else.

### 5. The final result will be calculated correctly
All the above functions ensure accurate vote counting. Each counting center has its private key, unknown to others. Votes are decrypted using this key for counting.

### 6. All interested parties can verify that the result was calculated correctly
Implemented using digital signatures (RSA encryption). This cryptographic mechanism allows creating a "signature" for data using a private key. Anyone with the corresponding public key can verify the data's integrity and sender's authenticity.

### 7. The protocol will work even in the presence of adversaries
All the above functions ensure the system's robustness against third-party interference. For verification convenience, an interface thirdparty.py has been implemented, which includes SQL queries to the database (in case of a breach).

## File Descriptions
### 1. interface.py
Main functions for program operation.

#### 1.1. execute_query()
Executes SQL query and returns the result.

#### 1.2. clear_console()
Aesthetic function to clear the console.

#### 1.3. error(message)
Formats error messages. Takes an error text and returns a rich-panel displaying the error.

#### 1.4. list_of_tally_centers()
Returns a list of all voting centers.

#### 1.5. list_of_candidates()
Returns a list of all candidates.

#### 1.6. get_voter(passport)
Fetches a voter using their passport number.

#### 1.7. get_tally_center(tally_center_id)
Fetches a voting center using its ID.

#### 1.8. to_vote(passport, private_key_serialized, candidate_id, tally_center_id)
Function for voting. Takes the voter's passport number, serialized private key, candidate ID, and voting center ID.

#### 1.9. tally_votes(tally_center_id, tally_center_private_key)
Function for vote tallying. Takes voting center ID and its private key. Conducts necessary checks, counts votes, records results in the "tally_results" table, and signs the results using a digital signature.

#### 1.10. check_votes()
This function serves multiple purposes: it displays voting results in a user-friendly format and verifies center signatures, ensuring vote results in the database remain unaltered.

#### 1.11. print_votes()
Displays voting results in the console in plain text (for simulation purposes).

### 2. database.py
SQLite DB settings file. Contains a single function, db_setup(), to create database tables according to schemas.

### 3. db_generator.py
Generates data in the database. Contains the data_generation() function, which populates the database with random and preset data.

### 4. crypto.py
Functions for cryptography.

#### 4.1. generate_phrase()
Generates a master phrase for ZKP implementation. It's a unique 32-byte random sequence.

#### 4.2. generate_keys()
Generates public and private keys. Returns both keys.

#### 4.3. serialize_private_key(private_key)
Serializes the private key. Returns a byte stream.

#### 4.4. serialize_public_key(public_key)
Serializes the public key similarly.

#### 4.5. sign_results(results, private_key)
Digitally signs voting results using the private key of the counting centers. Returns the signature in base64 format.

#### 4.6. verify_signature(results, signature, public_key)
Verifies the signature. Returns True if genuine, and False if altered.

#### 4.7. encrypt_vote(vote, public_key)
Encrypts the vote. Returns the encrypted vote in base64 format.

#### 4.8. decrypt_vote(encrypted_vote, private_key)
Decrypts the vote.

### 5. simulation.py
Implements the voting simulation. Contains the voting_simulation() function, which sequentially goes through all voting stages.

### 6. main.py
Implements the program's main logic. Deletes the current database, removes current private keys, recreates the database, populates it with random data, and then conducts a voting simulation.

### 7. voter_interface.py
Voter interface. A console application with a simple graphic interface to cast votes. Contains the menu() function for information display, input, and processing.

### 8. tally_interface.py
Interface for vote counting centers. A console application to count votes and display results.

#### 8.1 display_results(final_results)
Displays voting results for each center and overall results in a table format.

#### 8.2 menu()
Main interface function for information display, input, and processing.

### 9. thirdparty.py
"Third-party" file. A console application to directly query the database and receive responses.

#### 9.1 query(sql)
Queries the database, returns the result or a formatted error message.

#### 9.2 menu()
Main interface function for information display, input, and processing.