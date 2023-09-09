from database import db_setup
from db_generator import data_generation
import shutil
import os
from simulator import voting_simulation

"""
Главный файл запуска. В нем происходит "обнуление" бд и всех приватных ключей, а также настройка бд и генерация
данных. После этого запускается симуляция голосования. Для отключения любого из шагов можно просто закомментировать
нужную команду (например, чтобы не симулировать голосование, а провести настоящее)
"""


def new_data():
    # Удаляем файл базы данных, если он существует
    if os.path.exists("voting_database.db"):
        os.remove("voting_database.db")
    # Удаляем папку пользовательских ключей и все файлы в ней, если она существует
    if os.path.exists("user_keys"):
        shutil.rmtree("user_keys")
    # Создаем папку пользовательских ключей
    os.mkdir("user_keys")
    # Удаляем папку ключей центров подсчета голосов и все файлы в ней, если она существует
    if os.path.exists("tally_keys"):
        shutil.rmtree("tally_keys")
    # Создаем папку ключей центров подсчета голосов
    os.mkdir("tally_keys")
    # Создаем и настраиваем базу данных
    db_setup()


# Обнуляем все данные
new_data()

# Заполняем БД сгенерированными данными
data_generation()

# Симулируем голосование
voting_simulation()
