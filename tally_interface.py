from rich import print
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.table import Table
from rich.console import Console
import art
from interface import error, clear_console, tally_votes, check_votes, get_tally_center

"""
Это файл для интерфейса избирательного участка.
"""


def display_results(final_results):
    """
    В отдельную функцию вынесли вывод результатов. Для того чтобы интерфейс был более читаемым - используем
    различные библиотеки "красоты" текста: rich, art для всех интерфейсов. Конкретная данная функция, в дополнение
    к этому выводит результаты в виде таблицы с помощью библиотеки rich. Не будем останавливаться на подробностях
    работы с библиотекой rich, так как это не является требованием данного задания и используется для красоты =)
    """
    console = Console()

    # Заголовочная панель
    console.print("[bold blue]Voting results[/bold blue]\n")

    # Создаем и выводим таблицы для каждого tally_center
    for center_id, center_name, center_results in final_results:
        # Проходим по каждому центру.
        # Настройки таблицы. Заголовок - название центра, затем две колонки: имя кандидата и количество голосов
        table = Table(title=center_name)
        table.add_column("Candidate Name", justify="left", style="cyan", no_wrap=True)
        table.add_column("Votes", justify="right", style="magenta")

        # Добавляем строки в таблицу
        for candidate_id, candidate_name, votes_count in center_results:
            table.add_row(candidate_name, str(votes_count))

        # Выводим таблицу на экран
        console.print(table)
        # Добавляем пустую строку для красоты
        console.print("\n")

    # Создаем таблицу для общих результатов (по всем центрам)
    total_table = Table(title="Total Results", style="green")  # Заголовок - "Total Results", стиль таблицы- зеленый
    total_table.title_style = "green"  # Стиль заголовка - зеленый
    total_table.add_column("Candidate Name", justify="left", style="cyan", no_wrap=True)  # Колонка - имя кандидата
    total_table.add_column("Votes", justify="right", style="magenta")  # Колонка - количество голосов

    # Считаем общие голоса для каждого кандидата
    total_votes = {}  # Словарь для хранения общих голосов
    for _, _, center_results in final_results:
        # Проходим по каждому центру.
        # В center хранится кортеж (id, name, results). Нам нужен только results, первые два отмечаем прочерками
        for candidate_id, candidate_name, votes_count in center_results:
            # Проходим по каждому кандидату в центре
            if candidate_name in total_votes:
                # Если кандидат уже есть в словаре, то добавляем голоса
                total_votes[candidate_name] += votes_count
            else:
                # Если кандидата нет в словаре, то создаем его и записываем голоса
                total_votes[candidate_name] = votes_count

    for candidate_name, votes_count in total_votes.items():
        # Проходим по каждому кандидату в словаре и добавляем строку в таблицу общих результатов
        total_table.add_row(candidate_name, str(votes_count))

    # Выводим таблицу общих результатов
    console.print(total_table)


def menu():
    """
    Функция для вывода меню и обработки выбора пользователя. Сделана для лучшей читаемости данных и красоты =)
    Как говорилось ранее, для красоты используем библиотеку rich. В данной функции используется библиотека art для
    создания ASCII баннера (рисунок символами). На подробностях графического оформления, опять же, останавливаться не
    будем, так как это не является требованием данного задания и используется только для красоты =)
    """
    # Создаем ASCII баннер с помощью библиотеки art
    ascii_banner_top = art.text2art("WELCOME", "slant")

    # Добавляем текст к баннеру
    banner_content = Text.from_markup("[blue]" + ascii_banner_top + "[/blue]\n[red]to tally interface[/red]")
    banner_panel = Panel(banner_content)

    # Выводим на экран
    print(Align.center(banner_panel, vertical="middle"))

    # Просим ввести id центра
    print(Text("Please, enter your tally center id:", style="bold white"), end="")
    tally_center_id = input(" ")

    # Проверяем id центра - пытаемся получить его по id из базы данных. Если не получается, то выводим ошибку и выходим
    tally_center = get_tally_center(tally_center_id)[0]
    if not tally_center:
        print(error("A tally center with such a id was not found!"))
        exit()

    clear_console()  # Очищаем консоль, чтобы отобразить следующую "страницу" интерфейса
    # Текст с ID центра и приветствием
    header_text = f"ID of Tally Center: {tally_center[0]}\nThere is {tally_center[1]}! Please, choose what you want " \
                  f"to do:\n"

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
        print(error("Invalid menu item number!"))  # Выводим ошибку и выходим, если нет
        exit()

    if menu_choice == "1":
        # Обработка первого пункта меню - подсчет голосов
        clear_console()  # Очищаем консоль, чтобы отобразить следующую "страницу" интерфейса
        # Просим ввести путь до приватного ключа
        private_key_path = input("Enter path to your private key: ")
        # Пробуем прочитать файл с приватным ключом
        try:
            with open(private_key_path, "rb") as key_file:
                private_key = key_file.read()
        except:
            # Если не получается, то выводим ошибку и выходим
            print(error("Invalid path to key or file was corrupted!"))
            exit()

        # Пытаемся подсчитать голоса выбранного центра с помощью приватного ключа
        result = tally_votes(tally_center_id, private_key)

        # Обрабатываем ошибки
        if result == 0:
            print(error("No such tally center with this id!"))
            exit()
        if result == -1:
            print(error("Invalid private key!"))
            exit()
        if result == -2:
            print(error("Decryption error! There is problems with private key or results was corrupted!"))
            exit()

        # Если все хорошо, то выводим сообщение об успешном подсчете голосов и возвращаемся в меню
        print(Text("Votes successfully counted! ", style="bold white"))
        menu()

    if menu_choice == "2":
        # Обработка второго пункта меню - получение результатов и вывод их на экран
        clear_console()  # Очищаем консоль, чтобы отобразить следующую "страницу" интерфейса
        result = check_votes()  # Получаем результаты и проверяем их на подлинность
        if result == 0:
            #  Голосование ещё не было завершено - не у всех центров подсчитаны голоса
            print(error("Voting is not over! Not all tally centers have counted votes!"))
            exit()
        if result == -1:
            #  Кто-то пытался изменить результаты голосования в БД или же изменил подпись на неверную
            print(error("DATA CORRUPTION DETECTED! THERE IS WRONG SIGNATURE OR RESULTS IN DATABASE!"))

        # Вызываем функцию для вывода результатов на экран
        display_results(result)


"""
Точка входа в программу. Проверяем, что файл запущен напрямую, а не импортирован как модуль. Если запущен напрямую,
то вызываем функцию меню. Это общепринятый стандарт для Python.
"""
if __name__ == "__main__":
    # Вызываем функцию меню
    menu()
