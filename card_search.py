import json
import os
import re
import string
from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import requests
from bs4 import BeautifulSoup

# Global variables
decks_dir = "deck_lists"
decks_file = "deck_urls.txt"
frame_file = "card_frames.json"

plt.ion()


def get_query() -> str:
    """Prompt the user for what function to run"""

    print("Options:")
    print("    (E)nter TappedOut deck urls")
    print("    (D)ownload deck lists")
    print("    (S)earch for cards")
    print("    (P)lot color distribution")
    print("    (Q)uit")
    print("")

    query = input("").upper()
    while query not in ("E", "D", "S", "P", "Q", ""):
        print("Please enter E, D, S, P, or Q")
        query = input("").upper()

    return query


def get_deck_names() -> None:
    """Prompt the user for one or more TappedOut deck urls"""

    print("\n(R)eplace or (A)ppend to list of decks?")

    mode = input().upper()
    while mode not in ("A", "R"):
        print("Please enter A or R")
        mode = input("").upper()

    mode = "w" if mode == "R" else "a"

    with open(decks_file, mode) as f:
        print("Add deck names one per line")

        s = input("")
        while s:
            f.write(s.strip() + "\n")
            s = input("")


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
        deck_list = parse_deck_list(deck)
        with open(os.path.join(output_dir, deck + ".txt"), "w") as f:
            for card in deck_list:
                f.write(card.strip("1 ") + "\n")

    print("")


def parse_deck_list(deck: str) -> list[str]:
    """Given a TappedOut deck name, download and parse the deck list"""

    response = requests.get("https://tappedout.net/mtg-decks/" + deck)

    start = r'<input type="hidden" name="c" value="'
    end = r'">'
    match = re.search(f"{start}(.*?){end}", response.text)

    if match:
        raw_string = match.group(1)
        return BeautifulSoup(raw_string, features="html.parser").get_text().split("||")
    else:
        print(f"    Error: Failed to retrieve deck list for {deck}")
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
    card = input("")
    while len(card):
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
        card = input("")


def get_card_dict(deck_names: Union[str, list[str]]) -> dict[str, int]:
    """Combine deck lists and extract number of copies of each card"""

    deck_dict = get_deck_dict(deck_names)

    card_dict = {}
    for deck in deck_dict:
        for card in deck_dict[deck]:
            if card in card_dict:
                card_dict[card] += 1
            else:
                card_dict[card] = 1

    print(
        f"    Deck list(s) contained {sum(card_dict.values())} total cards",
        f"({len(card_dict)} unique cards)",
    )
    return card_dict


def get_frame_dict(card_dict: dict) -> dict[str, dict[str, int]]:
    """Given a dict with card names as keys, get their frames from ScryFall"""

    print("    Getting frame codes from ScryFall; progress:")

    frame_dict = {
        "W": {},
        "U": {},
        "B": {},
        "R": {},
        "G": {},
        "Z": {},
        "C": {},
        "L": {},
    }

    n = 0
    for card in card_dict:
        if not n % 100:
            print(f"        {n}/{len(card_dict)}")

        response = requests.get(
            "https://api.scryfall.com/cards/named?exact=" + card
        ).json()

        # Combine cards with multiple faces (DFCs, split cards, adventures, etc)
        if "card_faces" in response:
            response["type_line"] = response["card_faces"][0]["type_line"]
            if "colors" not in response:
                response["colors"] = []
                for face in response["card_faces"]:
                    response["colors"] += face["colors"]

        if "Land" in response["type_line"]:
            frame = "L"
        elif len(response["colors"]) == 0:
            frame = "C"
        elif len(response["colors"]) > 1:
            frame = "Z"
        else:
            frame = response["colors"][0]

        frame_dict[frame][card] = card_dict[card]
        n += 1

    print(f"        {n}/{len(card_dict)}")

    with open(frame_file, "w") as f:
        json.dump(frame_dict, f)

    return frame_dict


def make_plot(
    min_count: int = 1, include_lands: bool = False, load_from_file: bool = True
) -> None:
    """Plot the overall color distribution of the decks in the deck_names file.
    min_count: sets the minimum threshold for a card to be included in the plot (default: 1)
    include_lands: sets whether lands should be included in the plot (default: False)
    load_from_file: load the frame dictionary from a json file versus querying ScryFall (default: True)
    """

    deck_names = load_deck_names()
    card_dict = get_card_dict(deck_names)

    if load_from_file:
        try:
            with open(frame_file, "r") as f:
                frame_dict = json.load(f)
            _ = 1 / len(frame_dict)
        except (FileNotFoundError, DivideByZeroError):
            print("    Need to query ScryFall for frames first!")
    else:
        frame_dict = get_frame_dict(card_dict)

    print("    Preparing bar graph")

    cmap = {
        "W": "snow",
        "U": "blue",
        "B": "black",
        "R": "red",
        "G": "green",
        "Z": "gold",
        "C": "silver",
        "L": "peru",
    }

    names, colors, edges, counts = (
        np.array([]),
        np.array([]),
        np.array([]),
        np.array([]),
    )

    for frame in cmap:
        if (frame != "L" or include_lands) and frame_dict[frame] != {}:
            temp = np.array(list(frame_dict[frame].items()))
            names = np.append(names, temp.T[0])
            colors = np.append(colors, [cmap[frame]] * len(temp))
            edges = np.append(
                edges, ["black" if frame == "W" else cmap[frame]] * len(temp)
            )
            counts = np.append(counts, temp.T[1].astype(int))

    names = names[counts >= min_count]
    colors = colors[counts >= min_count]
    edges = edges[counts >= min_count]
    counts = counts[counts >= min_count]

    sorting = np.argsort(names)
    names = names[sorting]
    colors = colors[sorting]
    edges = edges[sorting]
    counts = counts[sorting]

    x = range(len(names))
    plt.bar(x, counts, color=colors, edgecolor=edges)
    plt.xticks(x, names, rotation=90)
    plt.xlim(-0.5, len(x) - 0.5)
    plt.tight_layout()


if __name__ == "__main__":
    query = get_query()
    while query not in ("Q", ""):
        if query == "E":
            get_deck_names()
        elif query == "D":
            try:
                get_deck_lists()
            except FileNotFoundError:
                print("    Need to enter deck names first!")
        elif query == "S":
            try:
                search_for_cards()
            except FileNotFoundError:
                print("    Need to download deck lists first!")
        elif query == "P":
            min_count = input("    Enter minimum card count (default: 1): ")
            include_lands = input("    Include lands? (y)es/(N)o: ")
            load_from_file = input("    Load frames from file? (Y)es/(n)o: ")
            try:
                make_plot(
                    int(min_count or 1),
                    include_lands.upper() == "Y",
                    load_from_file.upper() != "N",
                )
            except FileNotFoundError:
                print("    Need to download deck lists first!")
        query = get_query()
