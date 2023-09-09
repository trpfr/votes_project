import sqlite3


def db_setup():
    conn = sqlite3.connect('voting_database.db')
    cursor = conn.cursor()

	# TODO: ZKP для проверки, что человек голосовал
    # TODO: vote_token заменить на публичный и приватный ключ (приватные только у самих пользователей)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS voters (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        public_key TEXT NOT NULL UNIQUE,
        zkp TEXT
    )
    ''')

    # TODO: ZKP!!!!
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY,
        encrypted_vote TEXT NOT NULL,
        tally_center_id INTEGER NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tally_centers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        public_key TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tally_results (
        id INTEGER PRIMARY KEY,
        tally_center_id INTEGER NOT NULL,
        result TEXT NOT NULL,
        signature TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()
