from database import db_setup
from db_generator import data_generation
import shutil
import os

from simulator import voting_simulation

# Удаляем файл базы данных, если он существует
if os.path.exists("voting_database.db"):
    os.remove("voting_database.db")
if os.path.exists("user_keys"):
    # Удаляем папку пользовательских ключей и все файлы в ней
    shutil.rmtree("user_keys")
os.mkdir("user_keys")
if os.path.exists("tally_keys"):
    shutil.rmtree("tally_keys")
os.mkdir("tally_keys")
# Создаем базу данных
db_setup()
# Генерируем данные
data_generation()
# Симулируем голосование
voting_simulation()
