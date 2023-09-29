# Интерфейс "третьих лиц"
from rich import print
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
import art
from interface import error, clear_console

"""
This module contains the interface for third parties (Bad boys). 
It's just query interface (like attacker hacked the database)
"""

# Import SQLLite module and connect to DB (like attacker have direct access to the database)
import sqlite3

conn = sqlite3.connect('voting_database.db')
cursor = conn.cursor()


def query(sql):
    """
    Just execute SQL query and return result
    """
    try:
        # Try to execute SQL query
        cursor.execute(sql)
        return cursor.fetchall()
    except sqlite3.Error as e:
        # Cast error to string and return it
        return error(str(e))


def menu():
    """
    Function for displaying menu using rich and art libraries
    """
    clear_console()
    # ASCII banner with greeting
    ascii_banner_top = art.text2art("WELCOME", "slant")

    banner_content = Text.from_markup("[blue]" + ascii_banner_top + "[/blue]\n[red]to the third party interface[/red]")
    banner_panel = Panel(banner_content)

    print(Align.center(banner_panel, vertical="middle"))

    # Information about this interface in panel
    panel_text = "In this section, you can write direct queries to the database. Please enter your query and wait " \
                 "for the database response."

    # Create panel with information
    sql_panel = Panel(panel_text, title="SQL-Query", border_style="magenta")

    # Print it
    print(sql_panel)

    while True:
        # Ask user to enter SQL query
        sql_query = input("Enter your SQL query: ")
        # Execute query and print result
        print(query(sql_query))
        # Repeat until universe collapse


if __name__ == '__main__':
    menu()
