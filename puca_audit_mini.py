"""
Download the executable version at 

This version excludes the histogram plotting option. The full one is available at https://drive.google.com/file/d/1TGGFf8OWZV6t-aCFm0c54Uw_SAXeO9N3/view?usp=sharing

This work is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License. Original author is dude1818 on PucaTrade.com (https://pucatrade.com/profiles/show/129317)
"""

from requests import Session
from pprint import pformat
from re import findall

# Global variables
root_url = "https://pucatrade.com"
login_url = root_url + "/login"


def get_query():
    """Determine what data to collect"""

    print("Choose what data to collect. Options:")
    print("    (T)ransactions (sends/receives, fees, etc.)")
    print("    (E)xport entire ledger")

    query = input("").upper()
    while query not in ("T", "E"):
        print("Please enter T or E")
        query = input("").upper()

    return query


def get_session():
    """Open the session on pucatrade.com"""

    # Necessary login information
    username = input("Email address: ")
    password = input("Password: ")

    # Check first page of ledger to get dates
    url = root_url + "/account/ledger/2012-01"
    payload = {"login": username, "password": password}

    with Session() as session:
        post = session.post(login_url, data=payload)
        r = session.get(url)

    return r, payload


def get_urls(r):
    """Get the list of urls comprising the ledger"""

    print("Checking dates...")
    urls = []
    for line in r.text.split('href="'):
        url = line.split('">')[0].split('" SELECTED>')[0]
        if "ledger/2" in url:
            urls.append(root_url + url)

    return urls


def get_transactions(urls, payload):
    """Go through each page of ledger and sum up entries"""

    transactions = {}
    type_flag = '<div class="label letter">TYPE</div>'
    points_flag = '<div class="label letter">POINTS</div>'

    with Session() as session:
        post = session.post(login_url, data=payload)
        for url in urls:
            r = session.get(url)
            trans_list = r.text.split(type_flag)[1:]
            print(
                f"    Adding %i transactions from %s"
                % (len(trans_list), url.split("/")[-1])
            )

            for transaction in trans_list:
                type = transaction.split('"value letter">')[1].split("</div>")[0]
                points = (
                    transaction.split("POINTS")[1]
                    .split('"value">')[1]
                    .split("</div>")[0]
                    .strip()
                )
                if "Gift" in points:
                    points = 0
                else:
                    points = int(points)

                if points > 0:
                    type += "_incoming"
                elif points < 0:
                    type += "_outgoing"

                if type in transactions.keys():
                    transactions[type] += points
                else:
                    transactions[type] = points

    return transactions


def get_transaction_stats(transactions, fout):
    """Calculate some interesting statistics"""

    for key in (
        "BONUS_incoming",
        "SUBSCRIPTION_incoming",
        "PUCASHIELD_outgoing",
        "WANT_outgoing",
        "PUCASHIELD_incoming",
        "WANT_incoming",
        "ADMIN_incoming",
        "DISPUTE_incoming",
        "ITEM_outgoing",
        "SWEEPSTAKES_outgoing",
        "TRANSFER_incoming",
        "TRANSFER_outgoing",
        "TRADE_incoming",
        "TRADE_outgoing",
    ):
        if key not in transactions.keys():
            transactions[key] = 0

    starting = transactions["BONUS_incoming"] + transactions["SUBSCRIPTION_incoming"]
    shield_fees = (
        transactions["PUCASHIELD_outgoing"] + transactions["PUCASHIELD_incoming"]
    )
    promo_fees = transactions["WANT_outgoing"] + transactions["WANT_incoming"]
    fees = shield_fees + promo_fees
    payouts = transactions["ADMIN_incoming"] + transactions["DISPUTE_incoming"]
    misc = (
        transactions["ITEM_outgoing"]
        + transactions["SWEEPSTAKES_outgoing"]
        + transactions["TRANSFER_incoming"]
        + transactions["TRANSFER_outgoing"]
    )
    all_outgoing = (
        transactions["TRADE_outgoing"]
        + transactions["TRANSFER_outgoing"]
        + transactions["ITEM_outgoing"]
        + transactions["SWEEPSTAKES_outgoing"]
    )

    print_transactions(
        f"Trade volume: %i sent and %i received"
        % (transactions["TRADE_incoming"], -1 * transactions["TRADE_outgoing"]),
        fout,
    )
    print_transactions(f"Amount spent on promotion fees: %i" % abs(promo_fees), fout)
    print_transactions(f"Amount spent on Pucashield: %i" % abs(shield_fees), fout)
    print_transactions(f"Amount paid back by Pucashield: %i" % payouts, fout)
    print_transactions(
        f"Fraction of outgoing points spent on fees: %i/%i = %.3f"
        % (abs(fees), abs(all_outgoing), 1.0 * fees / all_outgoing),
        fout,
    )


def print_transactions(text, fout):
    """Print to command line and append to file"""

    print(text)
    with open(fout, "a") as f:
        f.write(text + "\n")


def quote_if_has_comma(text):
    """Enclose a string in quotes if it contains a comma"""

    if "," in text:
        return '"%s"' % text
    else:
        return text


def get_name_and_id(s):
    """Extract user ID and user name from an href"""

    s2 = s.split("/show/")[1]
    # Now s2 looks like "12345'>John Doe</a>"
    s3 = s2.split("'>")
    id = int(s3[0])
    name = s3[1].split("</a>")[0]

    return quote_if_has_comma(name), id


class Transaction:
    sender_name = ""
    sender_id = -1
    receiver_name = ""
    receiver_id = -1
    type = ""
    notes = ""
    package_id = ""
    card_id = ""
    card_name = ""
    foil = False
    points = 0
    running_total = 0
    date = ""
    time = ""

    # Create a Transaction object from a transaction text block
    def __init__(self, ttb):
        keysplits = ttb.split('<div class="label')
        valuesplits = ttb.split('<div class="value')
        for iks, keysplit in enumerate(keysplits):
            valuesplit = valuesplits[iks]
            ka = keysplit.find(">") + 1
            kb = keysplit.find("</div>")
            key = keysplit[ka:kb].strip()
            va = valuesplit.find(">") + 1
            vb = valuesplit.find("</div>")
            value = valuesplit[va:vb].strip()

            if key == "SENDER":
                self.sender_name, self.sender_id = get_name_and_id(value)
            elif key == "TYPE":
                if value == "WANT":
                    self.type = "TRADE FEE"
                else:
                    self.type = value
            elif key == "NOTES":
                self.notes = value
            elif key == "POINTS":
                # Gift trades have an icon in place of the point value, which
                # shows up as:
                #   <span class="icon icon-gift ">Gift</span>
                # in the HTML. So before setting a point value, check if the
                # trade was a gift
                if "Gift" in value:
                    self.type = "GIFT"
                    self.points = 0
                else:
                    # Not a gift
                    self.points = int(value.replace(",", ""))
            elif key == "RUNNING":
                self.running_total = int(value.split(">")[-1].replace(",", ""))
            elif key == "RECEIVER":
                self.receiver_name, self.receiver_id = get_name_and_id(value)
            elif key == "DATE":
                s2 = value.split(" ")
                self.date = s2[0]
                self.time = s2[1]

        # Decide what to do with the information in the
        # "notes" field. This depends on the transaction type.
        if self.type == "TRADE":
            # Get the card name, card ID, package ID, and foil identifier
            numbers = findall(r"\d+", self.notes)
            self.package_id = numbers[0]
            self.card_id = numbers[2]
            self.foil_id = numbers[3] == 0
            self.card_name = quote_if_has_comma(
                self.notes.split("</a>")[-2].split(">")[-1]
            )

    # Return a string representation of this Transaction
    # suitable for a CSV file.
    def csv_row(self):
        return "%s,%s,%i,%i,%s,%i,%s,%i,%s,%s,%s,%s,%s\n" % (
            self.package_id,
            self.type,
            self.points,
            self.running_total,
            self.sender_name,
            self.sender_id,
            self.receiver_name,
            self.receiver_id,
            self.card_name,
            self.card_id,
            self.foil,
            self.date,
            self.time,
        )

    # Return a string representation of this Transaction
    # suitable for print statements
    def __repr__(self):
        if self.type == "TRADE":
            return (
                "Package %d:\n" % self.package_id
                + "  %s (%i) -> %s (%i)\n"
                % (
                    self.sender_name,
                    self.sender_id,
                    self.receiver_name,
                    self.receiver_id,
                )
                + "  %s for %i pp on %s at %s\n"
                % (self.card_name, self.points, self.date, self.time)
            )
        elif self.type == "PUCASHIELD":
            return "PUCASHIELD for %d\n" % self.points


def get_all_transactions(urls, payload, csvfilename):
    """Go through each page of ledger and sum up entries"""

    csv_header = "Package ID,Transaction Type,Points,Balance,Sender,Sender ID,Receiver,Receiver ID,Card name,Card ID,Foil,Date,Time\n"
    transaction_start_string = '<div class="column sender">'

    with open(csvfilename, "w") as f:
        f.write(csv_header)
        with Session() as session:
            post = session.post(login_url, data=payload)
            for url in urls:
                r = session.get(url)
                transaction_text_blocks = r.text.split(transaction_start_string)[2:]
                print(
                    f"    Adding %i transactions from %s"
                    % (len(transaction_text_blocks), url.split("/")[-1])
                )

                for ttb in transaction_text_blocks:
                    # Remove non-ASCII characters to prevent usernames
                    # with unusual characters from causing a crash later
                    f.write(
                        Transaction(
                            ttb.encode("ascii", "ignore").decode("ascii")
                        ).csv_row()
                    )


if __name__ == "__main__":

    query = get_query()

    response, payload = get_session()
    while "logged-out" in response.text:
        print("Invalid credentials")
        response, payload = get_session()

    urls = get_urls(response)

    if query == "T":
        transactions = get_transactions(urls, payload)
        fout = "puca_transactions.txt"

        with open(fout, "w") as f:
            f.write(pformat(transactions))
            f.write("\n\n")
            print("Transaction summary written to %s\n" % fout)

        get_transaction_stats(transactions, fout)

    elif query == "E":
        fout = "puca_ledger.csv"
        get_all_transactions(urls, payload, fout)
        print("Transaction summary written to %s\n" % fout)

    input("Press Enter to quit")
