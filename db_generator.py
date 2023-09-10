import random
import sqlite3
from cryptography.hazmat.primitives import serialization
import crypto

"""
Для демонстрации работы системы и для того, чтобы не заполнять базу данных в ручную каждый раз мы создали файл
генерации БД. Он заполняет базу данных случайными данными. Для запуска нужно выполнить функцию data_generation().
"""


def data_generation():
    # Подключаемся к базе данных
    conn = sqlite3.connect('voting_database.db')
    cursor = conn.cursor()

    # Случайные (или не очень) имена
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

    # Случайные (или не очень) фамилии
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

    # Список кандидатов (по условию их всего 2)
    candidates = [
        "Republicans",
        "Democrats"
    ]

    # Количество голосующих для генерации
    count_of_voters = 100

    # Генерируем случайные имена и фамилии (комбинируем в случайном порядке из двух списков выше)
    random_names = [(random.choice(names), random.choice(lastnames)) for _ in range(count_of_voters)]

    # Создание избирателей
    for first, last in random_names:
        # Полное имя - итог комбинации выше
        full_name = f"{first} {last}"

        # Случайный номер паспорта (6 цифр)
        passport = random.randint(100000, 999999)

        # Генерируем ключи
        """
        Каждый голосующий должен иметь публичный ключ (приглашение на выборы) и приватный ключ (некая ключ-карта для 
        подтверждения того, что он имеет право голосовать). Публичный ключ хранится в базе данных, а приватный ключ
        сохраняется в файле. 
        
        Мы используем их для реализации системы zero-knowledge proof (ZKP). Это система, которая позволяет доказать
        факт, не раскрывая при этом никакой другой информации. В нашем случае мы используем ее для того, чтобы
        доказать, что голосующий имеет право голосовать, не раскрывая при этом его личность. А также, что голосующий
        уже голосовал, чтобы не дать ему голосовать дважды.
        """
        public_key, private_key = crypto.generate_keys()
        pem = crypto.serialize_private_key(private_key)

        # Сохраняем приватный ключ в файл
        with open(f"user_keys/private_key_{passport}.pem", "wb") as f:
            f.write(pem)

        # Сохраняем данные голосующего в базу данных
        cursor.execute("INSERT INTO voters (id, name, public_key) VALUES (?, ?, ?)", (passport,
                                                                                      full_name,
                                                                                      crypto.serialize_public_key(
                                                                                          public_key)))

    # Создание кандидатов (из списка кандидатов выше)
    for candidate in candidates:
        cursor.execute("INSERT INTO candidates (name) VALUES (?)", (candidate,))

    # Создание участков
    # Количество генерируемых участков
    tally_centers_count = 5
    for i in range(tally_centers_count):
        # Генерируем ключи (для подписи и проверки голосов)
        public_key, private_key = crypto.generate_keys()

        # Генерируем название участка (просто порядковый номер в списке + 1 (так как нумерация с 0))
        name = f"Tally center №{i + 1}"

        # Сохраняем данные участка в базу данных
        cursor.execute("INSERT INTO tally_centers (name, public_key) VALUES (?, ?)",
                       (name, crypto.serialize_public_key(public_key)))

        # Переводим приватный ключ в формат PEM (для сохранения в файл - сериализация (см crypto)
        pem = crypto.serialize_private_key(private_key)
        # Сохраняем приватный ключ в файл
        with open(f"tally_keys/private_key_{i + 1}.pem", "wb") as f:
            f.write(pem)

    # Сохраняем изменения в БД и закрываем соединение
    conn.commit()
    conn.close()

    # Генерируем мастер-фразу для zkp и сохраняем в файл
    """
    Это просто случайный набор байтов, который мы в дальнейшем шифруем и расшифровываем для реализации
    ZKP (см crypto.py)
    """
    master_phrase = crypto.generate_phrase()
    with open("master_phrase.txt", "w") as f:
        f.write(master_phrase)
