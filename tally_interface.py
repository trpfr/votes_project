from rich import print
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.table import Table
from rich.console import Console

import art

import interface


def display_results(final_results):
    console = Console()

    # Заголовочная панель
    console.print("[bold blue]Voting results[/bold blue]\n")

    # Создаем и выводим таблицы для каждого tally_center
    for center in final_results:
        center_id, center_name, center_results = center

        table = Table(title=center_name)
        table.add_column("Candidate Name", justify="left", style="cyan", no_wrap=True)
        table.add_column("Votes", justify="right", style="magenta")

        for candidate in center_results:
            candidate_id, candidate_name, votes_count = candidate
            table.add_row(candidate_name, str(votes_count))

        console.print(table)
        console.print("\n")

    # Создаем таблицу для общих результатов
    total_table = Table(title="Total Results", style="green")
    total_table.title_style = "green"
    total_table.add_column("Candidate Name", justify="left", style="cyan", no_wrap=True)
    total_table.add_column("Votes", justify="right", style="magenta")

    # Считаем общие голоса для каждого кандидата
    total_votes = {}
    for center in final_results:
        _, _, center_results = center
        for candidate in center_results:
            candidate_id, candidate_name, votes_count = candidate
            if candidate_name in total_votes:
                total_votes[candidate_name] += votes_count
            else:
                total_votes[candidate_name] = votes_count

    for candidate_name, votes_count in total_votes.items():
        total_table.add_row(candidate_name, str(votes_count))

    console.print(total_table)


def menu():
    # Создаем ASCII баннер поменьше
    ascii_banner_top = art.text2art("WELCOME", "slant")

    # Стилизуем каждую часть
    banner_content = Text.from_markup("[blue]" + ascii_banner_top + "[/blue]\n[red]to tally interface[/red]")
    banner_panel = Panel(banner_content)

    # Выводим на экран
    print(Align.center(banner_panel, vertical="middle"))

    # Просим ввести id центра
    print(Text("Please, enter your tally center id:", style="bold white"), end="")
    tally_center_id = input(" ")

    # Проверяем id центра
    tally_center = interface.get_tally_center(tally_center_id)
    if not tally_center:
        print(interface.error("A tally center with such a id was not found!"))
        exit()

    interface.clear_console()
    # Текст с айди и приветствием
    header_text = f"ID of Tally Center: {tally_center[0]}\nThere is {tally_center[1]}! Please, choose what you want to do:\n"


    # Список пунктов меню
    menu_items = ["Count votes", "Get results"]

    # Генерируем текст меню
    menu_text = "\n".join([f"{index + 1}. {item}" for index, item in enumerate(menu_items)])

    # Объединяем все тексты
    full_text = header_text + menu_text

    # Создаем панель для меню
    menu_panel = Panel(full_text, title="Menu", border_style="blue")

    # Выводим меню на экран
    print(menu_panel)

    # Выводим строку для ввода номера пункта меню
    menu_choice = input("Enter menu item number: ")

    # Проверяем, что введено число и оно в диапазоне
    if not menu_choice.isdigit() or int(menu_choice) not in range(1, len(menu_items) + 1):
        print(interface.error("Invalid menu item number!"))
        exit()

    if menu_choice == "1":
        interface.clear_console()
        # Просим ввести путь до приватного ключа
        private_key_path = input("Enter path to your private key: ")
        try:
            with open(private_key_path, "rb") as key_file:
                private_key = key_file.read()
        except:
            print(interface.error("Invalid path to key or file was corrupted!"))
            exit()

        result = interface.tally_votes(tally_center_id, private_key)
        if result == 0:
            print(interface.error("No such tally center with this id!"))
            exit()
        if result == -1:
            print(interface.error("Invalid private key!"))
            exit()
        if result == -2:
            print(interface.error("Decryption error! There is problems with private key or results was corrupted!"))
            exit()
        print(Text("Votes successfully counted! ", style="bold white"))
        menu()
    if menu_choice == "2":
        interface.clear_console()
        result = interface.check_votes()
        if result == 0:
            print(interface.error("Voting is not over! Not all tally centers have counted votes!"))
            exit()
        if result == -1:
            print(interface.error("DATA CORRUPTION DETECTED! THERE IS WRONG SIGNATURE OR RESULTS IN DATABASE!"))
        display_results(result)

menu()

