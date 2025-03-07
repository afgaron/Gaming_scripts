import os
import re
import string
import time
from typing import Union

import requests
from bs4 import BeautifulSoup

# Global variables
decks_dir = "deck_lists"
decks_file = "deck_urls.txt"
tappedout = "https://tappedout.net/"


def get_query() -> str:
    """Prompt the user for what function to run"""

    print("Options:")
    print("    (E)nter TappedOut deck urls")
    print("    (D)ownload deck lists")
    print("    (P)arse deck lists")
    print("    (S)earch for cards")
    print("    (G)ame Changer counts")
    print("    (Q)uit")
    print("")

    options = ("E", "D", "P", "S", "G", "Q")
    while (query := input().upper()) not in (*options, ""):
        print(f"Please enter one of {', '.join(options)}")

    return query


def get_deck_names() -> None:
    """Prompt the user for one or more TappedOut deck urls"""

    print("\n(R)eplace or (A)ppend to list of decks?")

    while (mode := input().upper()) not in ("A", "R"):
        print("Please enter A or R")

    with open(decks_file, "w" if mode == "R" else "a") as f:
        print("Add deck names one per line")

        while s := input():
            f.write(s.strip() + "\n")


def load_deck_names(filename: str = decks_file) -> list[str]:
    """Load deck names from file"""

    deck_names = []

    with open(filename, "r") as f:
        for line in f:
            deck_names.append(line.strip())

    return deck_names


def get_deck_lists(output_dir: str = decks_dir) -> None:
    """Download the deck lists from TappedOut"""

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    deck_names = load_deck_names()

    for deck in deck_names:
        print("    Getting deck list for", deck)
        output = os.path.join(output_dir, deck + ".html")
        html = get_html_from_url(tappedout + "mtg-decks/" + deck)
        with open(output, "w", encoding="utf-8") as f:
            f.write(html)
        time.sleep(4)

    print("")


def parse_deck_lists(output_dir: str = decks_dir) -> None:
    """Parse the deck lists from TappedOut"""

    deck_names = load_deck_names()

    for deck in deck_names:
        print("    Parsing deck list for", deck)
        input = os.path.join(output_dir, deck + ".html")
        output = os.path.join(output_dir, deck + ".txt")
        html = get_html_from_file(input)
        deck_list = parse_deck_list(html)
        with open(output, "w", encoding="utf-8") as f:
            for card in deck_list:
                f.write(card.strip("1 ") + "\n")

    print("")


def get_html_from_url(url: str) -> str:
    """Given a TappedOut deck name, download the HTML from the web"""

    response = requests.get(url)
    return response.text


def get_html_from_file(filepath: str) -> str:
    """Given a TappedOut deck name, load the HTML from a file"""

    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read()
    return text


def parse_deck_list(html: str) -> list[str]:
    """Given an HTML string, parse the deck list"""

    start = r'<input type="hidden" name="c" value="'
    end = r'">'

    if match := re.search(f"{start}(.*?){end}", html):
        raw_string = match.group(1)
        return BeautifulSoup(raw_string, features="html.parser").get_text().split("||")
    else:
        print("    Error: Failed to parse deck list")
        return []


def get_deck_dict(deck_names: Union[str, list[str]]) -> dict[str, list[str]]:
    """Extract deck lists from list of deck names and return them as a dictionary"""

    if type(deck_names) == str:
        deck_names = [deck_names]

    deck_dict = {}
    for deck in deck_names:
        with open(os.path.join(decks_dir, deck + ".txt"), "r") as f:
            deck_list = f.read().strip().lower().split("\n")
            deck_dict[deck] = deck_list

    return deck_dict


def search_for_cards() -> None:
    """Search deck lists for all instances of user supplied card name"""

    deck_names = load_deck_names()
    deck_dict = get_deck_dict(deck_names)

    print("Enter full card name:")
    while card := input():
        hits = []
        for deck in deck_dict:
            if card.lower() in deck_dict[deck]:
                hits.append(deck)

        if len(hits):
            print(f"\n{string.capwords(card)} was found in the following decks:")
            print(hits)
        else:
            print(f"\n{string.capwords(card)} was not found in any decks")

        print("\nEnter another full card name, or leave blank to exit:")


def game_changers() -> None:
    """Count the number of Game Changers in each deck list"""

    gc_file = "gamechangers.txt"
    with open(gc_file, "r") as f:
        lines = f.readlines()

    gc_set = set()
    for line in lines:
        gc_set.add(line.strip().lower())

    deck_names = load_deck_names()
    deck_dict = get_deck_dict(deck_names)

    gc_counts = {}
    for name, decklist in deck_dict.items():
        gc_counts[name] = len(gc_set.intersection(decklist))

    print("Number of Game Changers in each deck:")
    for name, gc_count in gc_counts.items():
        print(f"    {name}: {gc_count}")

    print("")


if __name__ == "__main__":
    while (query := get_query()) not in ("Q", ""):
        if query == "E":
            get_deck_names()
        elif query == "D":
            try:
                get_deck_lists()
            except FileNotFoundError:
                print("    Need to enter deck names first!")
        elif query == "P":
            try:
                parse_deck_lists()
            except FileNotFoundError:
                print("    Need to download deck lists first!")
        elif query == "S":
            try:
                search_for_cards()
            except FileNotFoundError:
                print("    Need to parse deck lists first!")
        elif query == "G":
            try:
                game_changers()
            except FileNotFoundError:
                print("    Need to parse deck lists first!")
