import ast
import requests


# Get source code of Planesculptors' set page
planesculptors_url = "https://www.planesculptors.net/set/namekkos#cards"
response = requests.get(planesculptors_url)
page_text = response.text

# Extract list of cards
card_text = page_text.split("var cardData = ")[1].split("$(function(){")[0].strip()[:-1]

# Convert to valid Python literal
headers = [
    "cardId:",
    "sequenceNumber:",
    "shape:",
    "name:",
    "manaCost:",
    "cmc:",
    "colors:",
    "types:",
    "artUrl:",
    "url:",
    "rulesText:",
    "flavorText:",
    "rarity:",
    "rarityName:",
    "ptString:",
    "illustrator:",
    "name2:",
    "manaCost2:",
    "types2:",
    "rulesText2:",
    "flavorText2:",
    "ptString2:",
    "illustrator2:",
    "setVersionLink:",
    "bbCode:",
]
for header in headers:
    card_text = card_text.replace(header, f'"{header[:-1]}":')

card_list = ast.literal_eval(card_text)

# Extract just the card image url
card_dict = {}
for card in card_list:
    card_dict[card["name"]] = card["artUrl"]

# Write cards to file
with open("namekkos.txt", "w") as f:
    f.write("name#image_url\n")
    for card, url in card_dict.items():
        f.write(f"{card}#{url}\n")
