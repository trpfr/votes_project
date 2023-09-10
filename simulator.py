from interface import execute_query, to_vote, tally_votes, print_votes, error, list_of_tally_centers, list_of_candidates
import random


"""
Файл, в котором реализована симуляция голосования. Она выполнена для демонстрации работоспособности нашей системы, 
а также для заполнения базы данных тестовыми данными.
"""


def voting_simulation():
    """
    Здесь реализована одна единственная функция - симуляция голосования.
    """
    #  Получаем из базы данных список избирателей, кандидатов и избирательных участков
    voters = execute_query("SELECT * FROM voters")
    tally_centers = list_of_tally_centers()
    candidates = list_of_candidates()

    # Голосуем за рандомного кандидата в рандомном избирательном участке
    for voter in voters:
        # Проходим по всем голосующим.
        # Получаем рандомного кандидата с помощью random.choice (выбирает рандомный элемент из списка)
        candidate = random.choice(candidates)
        # Получаем рандомный избирательный участок (аналогично предыдущему)
        tally_center = random.choice(tally_centers)
        # Загружаем приватный ключ голосующего из файла по шаблону user_keys/private_key_<id>.pem
        try:
            with open("user_keys/private_key_" + str(voter[0]) + ".pem", "rb") as key_file:
                voter_private_key = key_file.read()
        except:
            # Если не получилось загрузить ключ, то выводим ошибку и переходим к следующему голосующему
            print(error("Invalid path to key or file was corrupted!"))
            continue
        # Голосуем (вызываем функцию to_vote из interface.py)
        result = to_vote(voter[0], voter_private_key, candidate[0], tally_center[0])
        if result > 0:
            print("Voter #", voter[0], " voted")  # Выводим сообщение о том, что голосование прошло успешно
        # Обрабатываем ошибки
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

    # Запускаем подсчет голосов в избирательных участках
    for tally_center in tally_centers:
        """
        Проходим по всем избирательным участкам.Загружаем приватный ключ избирательного участка из файла по шаблону 
        private_key_<id избирательного участка>.pem
        """
        try:
            with open("tally_keys/private_key_" + str(tally_center[0]) + ".pem", "rb") as key_file:
                tally_center_private_key = key_file.read()
        except:
            # Если не получилось загрузить ключ, то выводим ошибку и переходим к следующему избирательному участку
            print(error("Invalid path to key or file was corrupted!"))
            continue
        # Вызываем функцию tally_votes из interface.py - подсчитываем голоса
        result = tally_votes(tally_center[0], tally_center_private_key)
        # Обрабатываем ошибки
        if result == 0:
            print(error("Tally center #" + tally_center[0] + " not found!"))
        elif result == -1:
            print(error("Tally center #" + tally_center[0] + " has wrong private key!"))
        elif result == -2:
            print(error("Tally center #" + tally_center[0] + " has bad public key!"))

    # Все голоса подсчитаны, выводим результаты
    print("\nVotes tallied")
    print("\nResults:")

    # Вызываем функцию print_votes из interface.py - выводим результаты голосования
    results = print_votes()

    # Обрабатываем ошибки
    if results == 0:
        print(error("Voting was not completed. Not all centers tallied votes."))
    if results == -1:
        print(error("DATA CORRUPTION DETECTED! THERE IS WRONG SIGNATURE OR RESULTS IN DATABASE!"))
