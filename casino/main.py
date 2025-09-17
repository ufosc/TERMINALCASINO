from casino.games.blackjack import play_blackjack
import pyfiglet
from colorama import Fore, Style, init
from InquirerPy import inquirer, get_style

# Initialize colorama
init(autoreset=True)


def show_welcome_screen():
    # Generate ASCII Art with pyfiglet
    text = "WELCOME TO THE PYTHON CASINO 🎲"
    # Choose a font style
    font = "standard"
    # Generate the ASCII art text
    ascii_art = pyfiglet.figlet_format(text, font=font)
    # Add color to the ASCII art text
    colored_ascii_art = f"{Fore.BLUE}{ascii_art}"
    # Print the colored ASCII art text
    print(colored_ascii_art)
    # Reset the color after printing
    print(Style.RESET_ALL)

    # Define a custom style for InquirerPy
    style = get_style(
        {
            "questionmark": "#ff8559 bold",
            "answer": "#ff8559 bold",
            "pointer": "#ff8559 bold",
            "highlighted": "fg:#000000 bg:#00bfff bold",
            "selected": "fg:#ff8559 bold",
        }
    )

    # Ask user with styled menu
    choice = inquirer.select(
        message="Please choose an option 🎰",
        choices=[
            "🃏  Play Blackjack",
            "🚪  Exit",
        ],
        style=style,
    ).execute()

    return choice


if __name__ == "__main__":
    choice = show_welcome_screen()

    if choice.startswith("🃏"):
        play_blackjack()
    elif choice.startswith("🚪"):
        print(
            Fore.RED
            + "Goodbye! Thanks for visiting the Python Casino 🎲"
            + Style.RESET_ALL
        )