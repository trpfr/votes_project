# Интерфейс "третьих лиц"
from rich import print
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
import art
from interface import error, clear_console

"""
Этот файл реализует интерфейс для третьих лиц. (Последний пункт ТЗ). По факту, это просто интерфейс для написания
SQL-запросов к базе данных, для того, чтобы не использовать отдельную программу для этого. В нем мы можем совершить 
любые действия с БД для проверки программы.
"""

# Подключаемся к базе данных, т.к. предполагаем, что третьи лица могут получить к ней прямой доступ
import sqlite3

conn = sqlite3.connect('voting_database.db')
cursor = conn.cursor()


def query(sql):
    """
    Функция для выполнения запроса к базе данных. Возвращает результат запроса, в случае ошибки возвращает её в
    форматированном для ошибки виде (см. функцию error в interface.py
    """
    try:
        # Пытаемся выполнить запрос
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error as e:
        # Кастинг ("перевод") ошибки в строку и возврат её в виде ошибки
        return error(str(e))


def menu():
    """
    Функция для вывода меню интерфейса. Сделана исключительно для красоты и удобства, поэтому подробности работы
    не будут описаны.
    """
    clear_console()  # Очищаем консоль
    # Создаем ASCII баннер
    ascii_banner_top = art.text2art("WELCOME", "slant")

    # Создаем подпись к баннеру
    banner_content = Text.from_markup("[blue]" + ascii_banner_top + "[/blue]\n[red]to the third party interface[/red]")
    banner_panel = Panel(banner_content)

    # Выводим на экран
    print(Align.center(banner_panel, vertical="middle"))

    # Текст для панели - инструкция
    panel_text = "In this section, you can write direct queries to the database. Please enter your query and wait " \
                 "for the database response."

    # Создаем панель с заголовком "SQL-Query"
    sql_panel = Panel(panel_text, title="SQL-Query", border_style="magenta")

    # Выводим панель на экран
    print(sql_panel)

    while True:
        # Выводим строку для ввода SQL-запроса
        sql_query = input("Enter your SQL query: ")
        # Печатаем результат запроса
        print(query(sql_query))
        # Повторяем всё до бесконечности


"""
Точка входа в программу. Если файл запускается напрямую, то вызывается функция menu(), которая выводит меню, в 
случае же импорта этого файла, функция не вызывается.
Это общепринятое правило в Python, для запуска скриптов.
"""
if __name__ == '__main__':
    menu()
