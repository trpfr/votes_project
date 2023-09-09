# Интерфейс "третьих лиц"
from rich import print
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
import art
from interface import error, clear_console, to_vote, tally_votes, print_votes

# Подключаемся к базе данных, т.к. предполагаем, что третьи лица могут получить к ней прямой доступ
import sqlite3

conn = sqlite3.connect('voting_database.db')
cursor = conn.cursor()


def query(sql):
    try:
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error as e:
        # Кастинг ошибки в строку
        return error(str(e))


def menu():
    clear_console()
    # Создаем ASCII баннер поменьше
    ascii_banner_top = art.text2art("WELCOME", "slant")

    # Стилизуем каждую часть
    banner_content = Text.from_markup("[blue]" + ascii_banner_top + "[/blue]\n[red]to the third party interface[/red]")
    banner_panel = Panel(banner_content)

    # Выводим на экран
    print(Align.center(banner_panel, vertical="middle"))

    # Текст для панели
    panel_text = "In this section, you can write direct queries to the database. Please enter your query and wait " \
                 "for the database response."

    # Создаем панель с заголовком "SQL-Query"
    sql_panel = Panel(panel_text, title="SQL-Query", border_style="magenta")

    # Выводим панель на экран
    print(sql_panel)

    while True:
        # Выводим строку для ввода SQL-запроса
        sql_query = input("Enter your SQL query: ")
        print(query(sql_query))


menu()
