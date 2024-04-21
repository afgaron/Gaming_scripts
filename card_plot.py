import json
from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import requests

from card_search import get_deck_dict, load_deck_names

# Global variables
frame_file = "card_frames.json"

plt.ion()


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
        except (FileNotFoundError, ZeroDivisionError):
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
    min_count = input("Enter minimum card count (default: 1): ")
    include_lands = input("Include lands? (y)es/(N)o: ")
    load_from_file = input("Load frames from file? (Y)es/(n)o: ")
    try:
        make_plot(
            int(min_count or 1),
            include_lands.upper() == "Y",
            load_from_file.upper() != "N",
        )
    except FileNotFoundError:
        print("Need to download deck lists first!")
    while True:
        input("Press enter to tighten plot")
        plt.tight_layout()
