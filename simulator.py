import interface
import sqlite3
import random


def voting_simulation():
    conn = sqlite3.connect('voting_database.db')
    cursor = conn.cursor()

    # Получаем список голосующих
    cursor.execute("SELECT * FROM voters")
    voters = cursor.fetchall()

    # Получаем список избирательных участков
    cursor.execute("SELECT * FROM tally_centers")
    tally_centers = cursor.fetchall()

    # Получаем список кандидатов
    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()

    # Голосуем за рандомного кандидата в рандомном избирательном участке
    for voter in voters:
        # Получаем рандомного кандидата
        candidate = random.choice(candidates)
        # Получаем рандомный избирательный участок
        tally_center = random.choice(tally_centers)
        # Загружаем приватный ключ голосующего из файла по шаблону user_keys/private_key_<id>.pem
        with open("user_keys/private_key_" + str(voter[0]) + ".pem", "rb") as key_file:
            voter_private_key = key_file.read()
        # Голосуем
        result = interface.to_vote(voter[0], voter_private_key, candidate[0], tally_center[0])
        if result > 0:
            print("Voter #", voter[0], " voted")
        elif result == 0:
            print("Voter #", voter[0], " could not vote - no such passport")
        elif result == -1:
            print("Voter #", voter[0], " could not vote - wrong private key")
        elif result == -2:
            print("Voter #", voter[0], " could not vote - double voting")
        elif result == -3:
            print("Voter #", voter[0], " could not vote - wrong public key")
        elif result == -4:
            print("Voter #", voter[0], " could not vote - wrong zkp. Bad private key")
    # Подсчитываем голоса
    for tally_center in tally_centers:
        # Загружаем приватный ключ избирательного участка из файла по шаблону private_key_<id избирательного
        # участка>.pem
        with open("tally_keys/private_key_" + str(tally_center[0]) + ".pem", "rb") as key_file:
            tally_center_private_key = key_file.read()
        if interface.tally_votes(tally_center[0], tally_center_private_key) == -1:
            print("Tally center #", tally_center[0], " has wrong private key!")
    print("\nVotes tallied")
    print("\nResults:")
    results = interface.print_votes()
    if results == 0:
        print("Voting was not completed. Not all centers tallied votes.")
    if results == -1:
        print("DATA CORRUPTION DETECTED! THERE IS WRONG SIGNATURE OR RESULTS IN DATABASE!")
    conn.close()
