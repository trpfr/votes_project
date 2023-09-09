from rich import print
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
import art
import interface

# Создаем ASCII баннер поменьше
ascii_banner_top = art.text2art("WELCOME", "slant")

# Стилизуем каждую часть
banner_content = Text.from_markup("[blue]" + ascii_banner_top + "[/blue]\n[red]to the elections[/red]")
banner_panel = Panel(banner_content)

# Выводим на экран
print(Align.center(banner_panel, vertical="middle"))

# Выводим сообщение для ввода номера паспорта
print(Text("Please, enter your passport number:", style="bold white"), end="")
passport = input(" ")

# Проверяем паспорт
voter = interface.get_voter(passport)
if not voter:
    print(interface.error("A citizen with such a passport number was not found!"))
    exit()

interface.clear_console()
# Текст с паспортом и приветствием
header_text = f"Passport number: {voter[0]}\nHi, {voter[1]}! Welcome to the elections. Please, choose your vote center:\n"

vote_centers = interface.list_of_tally_centers()

# Генерируем список центров
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
    print(error("Invalid center number!"))
    exit()

interface.clear_console()
# Выводим список кандидатов
# Текст с информацией
header_text = f"{voter[1]}, please, choose your candidate:\n"
# Получаем список кандидатов
candidates = interface.list_of_candidates()
# Выводим список кандидатов
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
    print(interface.error("Invalid candidate number!"))
    exit()
# Просим ввести путь до приватного ключа
private_key_path = input("Enter path to your private key: ")
try:
    with open(private_key_path, "rb") as key_file:
        private_key = key_file.read()
except:
    print(interface.error("Invalid path to key or file was corrupted!"))
    exit()

# Голосуем
result = interface.to_vote(voter[0], private_key, candidates[int(candidate_choice) - 1][0],
                           vote_centers[int(center_choice) - 1][0])
if result == 0:
    print(interface.error("A citizen with such a passport number was not found!"))
    exit()
if result == -1:
    print(interface.error("Invalid private key!"))
    exit()
if result == -2:
    print(interface.error("Double voting is not allowed!"))
    exit()
if result == -3:
    print(interface.error("Invalid public key in database! DATABASE IS CORRUPTED!"))
    exit()
if result == -4:
    print(interface.error("Invalid ZKP! You used wrong private key!"))
    exit()
if result == -5:
    print(interface.error("Encrypting error! Invalid public key of tally center!"))
    exit()
if result == -6:
    print(interface.error("Results already counted. Voting is over!"))
    exit()
interface.clear_console()
full_text = f"{voter[1]}, thank you for your vote!\n"
# Создаем зеленую рамку
green_panel = Panel(full_text, border_style="green")
# Выводим на экран
print(green_panel)
exit()
