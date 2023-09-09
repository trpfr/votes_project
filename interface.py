import base64
import json
import os
from rich import print
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
import platform
from collections import defaultdict

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import load_pem_public_key

import crypto
import sqlite3


def clear_console():
    system = platform.system()
    if system == "Windows":
        os.system('cls')
    else:
        os.system('clear')


def error(message):
    error_text = Text("⚠️ " + message, style="bold red")
    error_panel = Panel(error_text, title="Error", border_style="red")
    return error_panel


def list_of_tally_centers():
    conn = sqlite3.connect('voting_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tally_centers")
    tally_centers = cursor.fetchall()
    return tally_centers


def list_of_candidates():
    conn = sqlite3.connect('voting_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()
    return candidates


def get_voter(passport):
    conn = sqlite3.connect('voting_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM voters WHERE id=?", (passport,))
    voter = cursor.fetchone()
    return voter


def get_tally_center(tally_center_id):
    conn = sqlite3.connect('voting_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tally_centers WHERE id=?", (tally_center_id,))
    tally_center = cursor.fetchone()
    return tally_center


def to_vote(passport, private_key_unserialized, candidate_id, tally_center_id):
    conn = sqlite3.connect('voting_database.db')
    cursor = conn.cursor()
    # Проверяем, что голосование ещё не закончилось - нет результатов
    cursor.execute("SELECT COUNT(*) FROM tally_results")
    results = cursor.fetchall()[0]
    if not results:
        return -6
    # Проверяем паспорт в базе
    cursor.execute("SELECT * FROM voters WHERE id=?", (passport,))
    voter = cursor.fetchone()
    # Если такого паспорта нет, то возвращаем 0
    if not voter:
        return 0
    try:
        user_private_key = serialization.load_pem_private_key(
            private_key_unserialized,
            password=None,
            backend=default_backend()
        )
    except:
        return -1
    # Загружаем мастер-фразу из файла master_phrase.txt
    with open("master_phrase.txt", "r") as master_phrase_file:
        master_phrase = master_phrase_file.read()
    # Если человек голосовал - в базе данных ищем zkp
    if voter[3]:
        zkp = voter[3]
        # Дешифруем zkp
        decrypted_zkp = crypto.decrypt_vote(zkp, user_private_key)
        # Если расшифровали верно - подтверждаем, что человек проголосовал
        # Если расшифровали неверно - была попытка подделки записи, обнуляем zkp
        if decrypted_zkp == master_phrase:
            return -2
        else:
            cursor.execute("UPDATE voters SET zkp=? WHERE id=?", (None, passport))
            conn.commit()
    # Проверяем, верность ключа - шифруем и расшифровываем мастер-фразу, если получили то же самое - оба ключа верны
    try:
        user_public_key = load_pem_public_key(voter[2].encode('utf-8'))
    except:
        return -3
    zkp = crypto.encrypt_vote(master_phrase, user_public_key)
    if crypto.decrypt_vote(zkp, user_private_key) != master_phrase:
        return -4

    # Если все проверки пройдены, то голосуем
    # Получаем ID избирателя
    voter_id = voter[0]
    # Получаем public key избирательного участка
    cursor.execute("SELECT public_key FROM tally_centers WHERE id=?", (tally_center_id,))
    public_key = load_pem_public_key(cursor.fetchone()[0].encode('utf-8'))
    # Получаем зашифрованный голос
    encrypted_vote = crypto.encrypt_vote(candidate_id, public_key)
    if encrypted_vote is None:
        return -5
    # Записываем голос в базу
    cursor.execute("INSERT INTO votes (encrypted_vote, tally_center_id) VALUES (?, ?)",
                   (encrypted_vote, tally_center_id))
    # Записываем zkp в базу
    cursor.execute("UPDATE voters SET zkp=? WHERE id=?", (zkp, passport))
    conn.commit()
    # Сохраняем изменения
    conn.commit()
    conn.close()
    return True


# Функция подсчета голосов
def tally_votes(tally_center_id, tally_center_private_key):
    conn = sqlite3.connect('voting_database.db')
    cursor = conn.cursor()
    # Проверка, существует ли такой участок
    cursor.execute("SELECT * FROM tally_centers WHERE id=?", (tally_center_id,))
    tally_center = cursor.fetchone()
    if not tally_center:
        print("No such tally center")
        return 0
    try:
        private_key = serialization.load_pem_private_key(
            tally_center_private_key,
            password=None,
            backend=default_backend()
        )
    except:
        return -1

    # Извлечение зашифрованных голосов
    cursor.execute("SELECT encrypted_vote FROM votes WHERE tally_center_id=?", (tally_center_id,))
    encrypted_votes = cursor.fetchall()

    # Дешифрование голосов и подсчет результатов
    results = defaultdict(int)
    for encrypted_vote_data in encrypted_votes:
        decrypted_vote = crypto.decrypt_vote(encrypted_vote_data[0], private_key)
        if decrypted_vote is None:
            return -2
        results[decrypted_vote] += 1

    results_str = json.dumps(results)
    # Запись результатов в таблицу результатов и подписи, подтверждающей, что результаты верны
    cursor.execute("INSERT INTO tally_results (tally_center_id, result, signature) VALUES (?, ?, ?)",
                   (tally_center_id, results_str, crypto.sign_results(results_str, private_key)))

    conn.commit()
    conn.close()
    return 1


# Функция проверки результатов
def check_votes():
    conn = sqlite3.connect('voting_database.db')
    cursor = conn.cursor()

    final_results = []

    cursor.execute("SELECT * FROM tally_centers")
    tally_centers = cursor.fetchall()

    for tally_center in tally_centers:
        center_id = tally_center[0]
        center_name = tally_center[1]

        cursor.execute("SELECT * FROM tally_results WHERE tally_center_id=? ORDER BY tally_center_id ASC", (center_id,))
        tally_results = cursor.fetchall()[0]
        if not tally_results:
            return 0

        public_key = load_pem_public_key(tally_center[2].encode('utf-8'))
        if not crypto.verify_signature(tally_results[2], tally_results[3], public_key):
            return -1

        results = json.loads(tally_results[2])
        center_results = []
        for candidate_id, votes_count in results.items():
            candidate_name = cursor.execute("SELECT name FROM candidates WHERE id=? ORDER BY id ASC", (candidate_id,)).fetchone()[0]
            center_results.append((candidate_id, candidate_name, votes_count))

        final_results.append((center_id, center_name, center_results))

    conn.close()
    return final_results


# Функция вывода таблицы голосов из tally_results
def print_votes():
    # Получение результатов голосования
    results = check_votes()
    # Если получили ошибку (если тип результатов не список) - просто возвращаем ошибку
    if not isinstance(results, list):
        return results
    # Словарь для хранения общего количества голосов для каждого кандидата
    total_votes = defaultdict(int)

    for center in results:
        center_id, center_name, center_results = center
        print("{}".format(center_name))
        for candidate in center_results:
            candidate_id, candidate_name, votes = candidate
            print("{}: {}".format(candidate_name, votes))
            total_votes[candidate_name] += votes
        print("")  # Пустая строка для разделения результатов разных центров

    # Вывод общего количества голосов
    print("Total votes:")
    for candidate_name, votes in total_votes.items():
        print("{}: {}".format(candidate_name, votes))

