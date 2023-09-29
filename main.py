from database import db_setup
from db_generator import data_generation
import shutil
import os

from simulator import voting_simulation

"""
Main file. It resets the database and all private keys, as well as sets up the database and generates data. After that,
the voting simulation starts. To disable any of the steps, you can simply comment out the necessary command (for
example, to not simulate voting, for a real one)
"""


def new_data():
    # Remove database file if exists
    if os.path.exists("voting_database.db"):
        os.remove("voting_database.db")
    # Remove user keys folder if exists
    if os.path.exists("user_keys"):
        shutil.rmtree("user_keys")
    # Create user keys folder
    os.mkdir("user_keys")
    # Remove tally keys folder if exists
    if os.path.exists("tally_keys"):
        shutil.rmtree("tally_keys")
    # Create tally keys folder
    os.mkdir("tally_keys")
    # Create and setup database
    db_setup()


# Reset database and keys
new_data()

# Generate data
data_generation()

# Simulate voting
voting_simulation()
