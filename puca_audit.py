from requests import Session
from pprint import pformat
import matplotlib.pyplot as plt

# Global variables
root_url = "https://pucatrade.com"
login_url = root_url + "/login"


def get_query():
    """Determine what data to collect"""

    print("Choose what data to collect. Options:")
    print("    (T)ransactions (sends/receives, fees, etc.)")
    print("    (D)istribution of card values sent/received")

    query = input("").upper()
    while query not in ("T", "D"):
        print("Please enter T or D")
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
                points = int(
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


def get_values(urls, payload):
    """Go through each page of ledger and collect value of each card"""

    sending, receiving = [], []
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

                if type == "TRADE":
                    points = (
                        transaction.split("POINTS")[1]
                        .split('"value">')[1]
                        .split("</div>")[0]
                        .strip()
                    )

                    if "Gift" in points:
                        continue
                    else:
                        points = int(points)

                    if points > 0:
                        sending.append(points)
                    else:
                        receiving.append(-1 * points)

    return sending, receiving


def make_histogram(sending, receiving):
    """Plot a histogram of card values. Require matplotlib"""

    n, bins, patches = plt.hist(sending+receiving, bins=25, log=True)
    plt.clf()

    # Transparent histograms with solid edges
    plt.hist(sending, bins=bins, log=True, edgecolor="None", alpha=0.5, color="b", label="Sent")
    plt.hist(sending, bins=bins, log=True, lw=1, facecolor="None", edgecolor="k")

    plt.hist(receiving, bins=bins, log=True, edgecolor="None", alpha=0.5, color="r", label="Received")
    plt.hist(receiving, bins=bins, log=True, lw=1, facecolor="None", edgecolor="k")

    plt.legend()
    plt.xlabel("Card value")
    plt.ylabel("Count")
    plt.title("Distribution of card values traded")
    plt.tight_layout()
    
    plt.show()


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

    elif query == "D":
        sending, receiving = get_values(urls, payload)
        fout = "puca_transaction_values.txt"

        with open(fout, "w") as f:
            f.write("sending = " + str(sending) + "\n\n")
            f.write("receiving = " + str(receiving) + "\n\n")
            print("Transaction summary written to %s\n" % fout)

        make_histogram(sending, receiving)

    input("Press Enter to quit")
