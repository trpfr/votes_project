import random
import sqlite3

from cryptography.hazmat.primitives import serialization

import crypto


def data_generation():
    conn = sqlite3.connect('voting_database.db')
    cursor = conn.cursor()

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

    candidates = [
        "Republicans",
        "Democrats"
    ]

    # Create voter's names
    count_of_voters = 100

    # Randomly generate names
    random_names = [(random.choice(names), random.choice(lastnames)) for _ in range(count_of_voters)]

    # Create voters
    for first, last in random_names:
        full_name = f"{first} {last}"

        # Случайный номер паспорта
        passport = random.randint(100000, 999999)

        # Генерируем ключи
        public_key, private_key = crypto.generate_keys()
        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Save private key to file
        with open(f"user_keys/private_key_{passport}.pem", "wb") as f:
            f.write(pem)

        cursor.execute("INSERT INTO voters (id, name, public_key) VALUES (?, ?, ?)", (passport,
                                                                                      full_name,
                                                                                      crypto.serialize_public_key(public_key)))


    # Create candidates
    for candidate in candidates:
        cursor.execute("INSERT INTO candidates (name) VALUES (?)", (candidate,))

    # Create tally centers
    tally_centers_count = 5
    for i in range(tally_centers_count):
        # Generate keys
        public_key, private_key = crypto.generate_keys()

        # Generate name
        name = f"Tally center №{i + 1}"

        cursor.execute("INSERT INTO tally_centers (name, public_key) VALUES (?, ?)",
                       (name, crypto.serialize_public_key(public_key)))

        pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        # Save private key to file
        with open(f"tally_keys/private_key_{i + 1}.pem", "wb") as f:
            f.write(pem)

    conn.commit()
    conn.close()

    # Генерируем мастер-фразу для zkp и сохраняем в файл
    master_phrase = crypto.generate_phrase()
    with open("master_phrase.txt", "w") as f:
        f.write(master_phrase)
