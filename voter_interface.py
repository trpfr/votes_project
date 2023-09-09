from rich import print
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
import art
from interface import error, clear_console, get_voter, to_vote, list_of_tally_centers, list_of_candidates

"""
В этом файле реализован интерфейс избирателя.
"""


def menu():
    """
    Функция для вывода меню избирателя. Использует библиотеки rich и art для красивого вывода текста.
    Подробности их работы не будем рассматривать, так как это не является требованием данного задания.
    """
    # Создаем ASCII баннер
    ascii_banner_top = art.text2art("WELCOME", "slant")

    # Создаем подпись к баннеру
    banner_content = Text.from_markup("[blue]" + ascii_banner_top + "[/blue]\n[red]to the elections[/red]")
    banner_panel = Panel(banner_content)

    # Выводим на экран
    print(Align.center(banner_panel, vertical="middle"))

    # Выводим сообщение для ввода номера паспорта
    print(Text("Please, enter your passport number:", style="bold white"), end="")
    passport = input(" ")

    # Проверяем паспорт
    voter = get_voter(passport)  # Получаем голосующего по паспорту
    if not voter:
        # Если голосующего нет, выводим ошибку, что голосующий с таким паспортом не найден и выходим
        print(error("A citizen with such a passport number was not found!"))
        exit()

    clear_console()  # Очищаем консоль для загрузки "следующего экрана"
    # Текст с паспортом и приветствием
    header_text = f"Passport number: {voter[0]}\nHi, {voter[1]}! Welcome to the elections. Please, choose your vote " \
                  f"center:\n"

    # Получаем список центров
    vote_centers = list_of_tally_centers()

    # Генерируем список центров для вывода на экран
    centers_text = "\n".join([f"{center[0]}. {center[1]}" for center in vote_centers])

    # Объединяем все тексты
    full_text = header_text + centers_text

    # Создаем зеленую рамку
    green_panel = Panel(full_text, border_style="green")

    # Выводим на экран
    print(green_panel)

    # Выводим строку для ввода номера центра
    center_choice = input("Enter number of the center: ")

    # Проверяем, что введено число и оно в диапазоне
    if not center_choice.isdigit() or int(center_choice) not in range(1, len(vote_centers) + 1):
        # Если введено не число или оно не в диапазоне, выводим ошибку и выходим
        print(error("Invalid center number!"))
        exit()

    clear_console()  # Очищаем консоль для загрузки "следующего экрана"
    # Выводим список кандидатов
    # Текст с информацией
    header_text = f"{voter[1]}, please, choose your candidate:\n"

    # Получаем список кандидатов
    candidates = list_of_candidates()

    # Генерируем список кандидатов для вывода на экран
    candidates_text = "\n".join([f"{candidate[0]}. {candidate[1]}" for candidate in candidates])
    # Объединяем все тексты
    full_text = header_text + candidates_text
    # Создаем зеленую рамку
    green_panel = Panel(full_text, border_style="green")
    # Выводим на экран
    print(green_panel)

    # Выводим строку для ввода номера кандидата
    candidate_choice = input("Enter number of the candidate: ")

    # Проверяем, что введено число и оно в диапазоне
    if not candidate_choice.isdigit() or int(candidate_choice) not in range(1, len(candidates) + 1):
        # Если введено не число или оно не в диапазоне, выводим ошибку и выходим
        print(error("Invalid candidate number!"))
        exit()

    # Просим ввести путь до приватного ключа голосующего
    private_key_path = input("Enter path to your private key: ")
    try:
        # Пробуем открыть файл с приватным ключом
        with open(private_key_path, "rb") as key_file:
            private_key = key_file.read()
    except:
        # Если не получилось, выводим ошибку и выходим
        print(error("Invalid path to key or file was corrupted!"))
        exit()

    # Голосуем с помощью функции to_vote (передаем номер паспорта, приватный ключ, номер кандидата и номер центра)
    result = to_vote(voter[0], private_key, candidates[int(candidate_choice) - 1][0],
                     vote_centers[int(center_choice) - 1][0])

    # Обработка ошибок
    if result == 0:
        # Пользователь с таким паспортом не найден
        print(error("A citizen with such a passport number was not found!"))
        exit()

    if result == -1:
        # Неверный приватный ключ
        print(error("Invalid private key!"))
        exit()

    if result == -2:
        # Попытка повторного голосования
        print(error("Double voting is not allowed!"))
        exit()

    if result == -3:
        # Неверный публичный ключ в базе данных (база данных была повреждена)
        print(error("Invalid public key in database! DATABASE IS CORRUPTED!"))
        exit()

    if result == -4:
        # Неверный ZKP (а значит неверный приватный ключ пользователя)
        print(error("Invalid ZKP! You used wrong private key!"))
        exit()

    if result == -5:
        # Неверный публичный ключ центра и как следствие ошибка во время шифрования голоса
        print(error("Encrypting error! Invalid public key of tally center!"))
        exit()

    if result == -6:
        # Голосование уже было закончено и голоса посчитаны, соответственно голосовать уже нельзя
        print(error("Results already counted. Voting is over!"))
        exit()

    clear_console()  # Очищаем консоль для загрузки "следующего экрана"
    full_text = f"{voter[1]}, thank you for your vote!\n"

    # Создаем зеленую рамку
    green_panel = Panel(full_text, border_style="green")

    # Выводим на экран благодарность за голосование и завершаем работу программы
    print(green_panel)
    exit()


"""
Входная точка программы. Запускает интерфейс избирателя, в случае, если файл запущен напрямую. В противном случае
ничего не делает. Это общепринятый способ запуска программ в Python.
"""
if __name__ == "__main__":
    menu()
