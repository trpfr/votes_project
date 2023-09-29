from rich import print
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.table import Table
from rich.console import Console
import art
from interface import error, clear_console, tally_votes, check_votes, get_tally_center

"""
Interface for tally center
"""


def display_results(final_results):
    """
    Display results of voting as a table using rich and art libraries
    """
    console = Console()

    console.print("[bold blue]Voting results[/bold blue]\n")

    # Create table for each tally center
    for center_id, center_name, center_results in final_results:
        table = Table(title=center_name)
        table.add_column("Candidate Name", justify="left", style="cyan", no_wrap=True)
        table.add_column("Votes", justify="right", style="magenta")

        # Add rows to the table
        for candidate_id, candidate_name, votes_count in center_results:
            table.add_row(candidate_name, str(votes_count))

        # Print table
        console.print(table)
        # Just new line
        console.print("\n")

    # Create table for total results
    total_table = Table(title="Total Results", style="green")
    total_table.title_style = "green"
    total_table.add_column("Candidate Name", justify="left", style="cyan", no_wrap=True)
    total_table.add_column("Votes", justify="right", style="magenta")

    # Calculate total votes
    total_votes = {}
    for _, _, center_results in final_results:
        # Because we need only center results here, we can use _ instead of center_id and center_name
        for candidate_id, candidate_name, votes_count in center_results:
            if candidate_name in total_votes:
                # If candidate is already in the dictionary, add votes
                total_votes[candidate_name] += votes_count
            else:
                # If candidate is not in the dictionary, create new key and add votes
                total_votes[candidate_name] = votes_count

    for candidate_name, votes_count in total_votes.items():
        # Add rows to the table for each candidate
        total_table.add_row(candidate_name, str(votes_count))

    # Print total table
    console.print(total_table)


def menu():
    """
    Function for displaying menu using rich and art libraries
    """
    # ASCII banner with help of art library
    ascii_banner_top = art.text2art("WELCOME", "slant")

    banner_content = Text.from_markup("[blue]" + ascii_banner_top + "[/blue]\n[red]to tally interface[/red]")
    banner_panel = Panel(banner_content)

    print(Align.center(banner_panel, vertical="middle"))

    # Ask user to enter tally center id
    print(Text("Please, enter your tally center id:", style="bold white"), end="")
    tally_center_id = input(" ")

    # Check if tally center with such id exists
    tally_center = get_tally_center(tally_center_id)[0]
    if not tally_center:
        print(error("A tally center with such a id was not found!"))
        exit()

    # Clear console for next "page" of interface
    clear_console()
    # Just header with greeting
    header_text = f"ID of Tally Center: {tally_center[0]}\nThere is {tally_center[1]}! Please, choose what you want " \
                  f"to do:\n"

    # List of menu items
    menu_items = ["Count votes", "Get results"]

    # Generate text for menu
    menu_text = "\n".join([f"{index + 1}. {item}" for index, item in enumerate(menu_items)])

    # Union header and menu text
    full_text = header_text + menu_text

    # Create panel with menu
    menu_panel = Panel(full_text, title="Menu", border_style="blue")

    # Print panel
    print(menu_panel)

    # Ask user to enter menu item number
    menu_choice = input("Enter menu item number: ")

    # Check if user entered valid menu item number
    if not menu_choice.isdigit() or int(menu_choice) not in range(1, len(menu_items) + 1):
        print(error("Invalid menu item number!"))
        exit()

    if menu_choice == "1":
        # First menu item - count votes
        clear_console()  # "Next page"
        private_key_path = input("Enter path to your private key: ")
        # Try to read private key from file
        try:
            with open(private_key_path, "rb") as key_file:
                private_key = key_file.read()
        except:
            print(error("Invalid path to key or file was corrupted!"))
            exit()

        # Try to count votes for this tally center
        result = tally_votes(tally_center_id, private_key)

        # Error handling
        if result == 0:
            print(error("No such tally center with this id!"))
            exit()
        if result == -1:
            print(error("Invalid private key!"))
            exit()
        if result == -2:
            print(error("Decryption error! There is problems with private key or results was corrupted!"))
            exit()

        # If everything is ok, print success message and return to menu
        print(Text("Votes successfully counted! ", style="bold white"))
        menu()

    if menu_choice == "2":
        # Second menu item - get results
        clear_console()  # "Next page"
        result = check_votes()  # Check and get results
        if result == 0:
            #  Voting is not over
            print(error("Voting is not over! Not all tally centers have counted votes!"))
            exit()
        if result == -1:
            #  Data corruption (wrong signature or results in database)
            print(error("DATA CORRUPTION DETECTED! THERE IS WRONG SIGNATURE OR RESULTS IN DATABASE!"))

        # If everything is ok, display results
        display_results(result)


if __name__ == "__main__":
    # Вызываем функцию меню
    menu()
