from rich import print
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
import art
from interface import error, clear_console, get_voter, to_vote, list_of_tally_centers, list_of_candidates

"""
This module contains the interface for voter.
"""


def menu():
    """
    Function for displaying menu using rich and art libraries
    """
    # ASCII banner with greeting
    ascii_banner_top = art.text2art("WELCOME", "slant")

    banner_content = Text.from_markup("[blue]" + ascii_banner_top + "[/blue]\n[red]to the elections[/red]")
    banner_panel = Panel(banner_content)

    print(Align.center(banner_panel, vertical="middle"))

    # Ask user to enter passport number
    print(Text("Please, enter your passport number:", style="bold white"), end="")
    passport = input(" ")

    # Check if voter with such passport exists
    try:
        voter = get_voter(passport)[0]
    except:
        print(error("A citizen with such a passport number was not found!"))
        exit()

    clear_console()  # Next "page" of interface
    # Greeting header
    header_text = f"Passport number: {voter[0]}\nHi, {voter[1]}! Welcome to the elections. Please, choose your vote " \
                  f"center:\n"

    vote_centers = list_of_tally_centers()

    centers_text = "\n".join([f"{center[0]}. {center[1]}" for center in vote_centers])

    full_text = header_text + centers_text

    green_panel = Panel(full_text, border_style="green")

    # Display green panel with information and list of vote centers
    print(green_panel)

    # Ask user to enter number of vote center
    center_choice = input("Enter number of the center: ")

    # Check if user entered valid number
    if not center_choice.isdigit() or int(center_choice) not in range(1, len(vote_centers) + 1):
        print(error("Invalid center number!"))
        exit()

    clear_console()  # Load next "page" of interface
    header_text = f"{voter[1]}, please, choose your candidate:\n"

    candidates = list_of_candidates()

    candidates_text = "\n".join([f"{candidate[0]}. {candidate[1]}" for candidate in candidates])
    full_text = header_text + candidates_text
    green_panel = Panel(full_text, border_style="green")
    # Display green panel with information and list of candidates
    print(green_panel)

    # Ask user to enter number of candidate
    candidate_choice = input("Enter number of the candidate: ")

    # Check if user entered valid number
    if not candidate_choice.isdigit() or int(candidate_choice) not in range(1, len(candidates) + 1):
        print(error("Invalid candidate number!"))
        exit()

    # Ask user to enter path to private key
    private_key_path = input("Enter path to your private key: ")
    try:
        # Trying to read private key from file
        with open(private_key_path, "rb") as key_file:
            private_key = key_file.read()
    except:
        print(error("Invalid path to key or file was corrupted!"))
        exit()

    #  Trying to vote
    result = to_vote(voter[0], private_key, candidates[int(candidate_choice) - 1][0],
                     vote_centers[int(center_choice) - 1][0])

    # Error handling
    if result == 0:
        print(error("A citizen with such a passport number was not found!"))
        exit()

    if result == -1:
        print(error("Invalid private key!"))
        exit()

    if result == -2:
        print(error("Double voting is not allowed!"))
        exit()

    if result == -3:
        print(error("Invalid public key in database! DATABASE IS CORRUPTED!"))
        exit()

    if result == -4:
        print(error("Invalid ZKP! You used wrong private key!"))
        exit()

    if result == -5:
        print(error("Encrypting error! Invalid public key of tally center!"))
        exit()

    if result == -6:
        print(error("Results already counted. Voting is over!"))
        exit()

    clear_console()
    full_text = f"{voter[1]}, thank you for your vote!\n"

    green_panel = Panel(full_text, border_style="green")

    # Display green panel with thank you message and exit
    print(green_panel)
    exit()


if __name__ == "__main__":
    menu()
