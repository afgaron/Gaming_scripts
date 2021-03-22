"""
Download the executable version at https://www.dropbox.com/s/6ftmlh0q26dqjfb/have_list_pricing.exe?dl=1

This work is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License. Original author is dude1818 on PucaTrade.com (https://pucatrade.com/profiles/show/129317)
"""

import tkinter as tk
from tkinter import Tk, Button, Entry, Frame, Label
from tkinter import filedialog as fd

# GUI to enter promo values
class GUI(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)

        self.root = root
        self.parent = parent
        self.button_add = None
        self.button_quit = None
        self.prices = []
        self.promos = []
        self.row_count = 1
        self.root.title("PucaTrade Marketplace Pricer")
        self.filename = fd.askopenfilename()

        # This refreshes the window so we can enter data
        self.root.overrideredirect(True)
        self.root.overrideredirect(False)

        self.reg = self.root.register(self.callback)
        self.message(
            f"In the left column, enter index price thresholds. In the right column,\n"
            f"enter promo percent values that you want to apply to cards above that\n"
            f"threshold. Leave the promo field blank to mark those cards Not For Sale."
        )
        self.add_row()

    def message(self, msg):
        """Add an infomative message at the top of the window"""
        self.label = Label(text=msg)
        self.label.grid(row=0, column=0, columnspan=2, sticky=tk.W + tk.E)

    def add_row(self):
        """Remove the existing buttons, add a row of Entries, and put the buttons back at the bottom"""
        if self.button_add is not None:
            self.button_add.grid_forget()
        if self.button_quit is not None:
            self.button_quit.grid_forget()

        self.prices.append(Entry(state=tk.NORMAL))
        self.prices[-1].grid(row=self.row_count, column=0)
        self.prices[-1].config(validate="key", validatecommand=(self.reg, "%P"))
        self.promos.append(Entry(state=tk.NORMAL))
        self.promos[-1].grid(row=self.row_count, column=1)
        self.promos[-1].config(validate="key", validatecommand=(self.reg, "%P"))

        self.button_add = Button(text="Add another row", command=self.add_row)
        self.button_add.grid(
            row=self.row_count + 1, column=0, columnspan=2, sticky=tk.W + tk.E
        )
        self.button_quit = Button(text="Apply and close", command=self.apply_and_close)
        self.button_quit.grid(
            row=self.row_count + 2, column=0, columnspan=2, sticky=tk.W + tk.E
        )

        self.row_count += 1

    def apply_and_close(self):
        """Extract the data entered into all the Entries and pass it as a dict to the pricing function"""
        prices = [make_int(price.get()) for price in self.prices]
        promos = [make_int(promo.get()) for promo in self.promos]

        try:
            # numpy would make this easier but increases size of .exe by 20x
            sum([price for price, promo in zip(prices, promos) if promo is not None])
            if len([price for price in prices if price is not None]):
                edit_file(
                    self.filename,
                    [price for price in prices if price is not None],
                    [
                        promo
                        for price, promo in zip(prices, promos)
                        if price is not None
                    ],
                )
            self.root.quit()

        except TypeError:
            self.message("\nEnter a price minimum for each promo value!\n")

    def callback(self, val):
        """Validate that entered data can be coerced to int"""
        try:
            make_int(val)
            return True
        except ValueError:
            return False


def make_int(val):
    """Coerces str to int, and empty strings become None"""
    try:
        return int(val)
    except ValueError:
        if val != "":
            raise


def edit_file(filename_in, prices, promos):

    promo_dict = dict(zip(prices, promos))
    if 0 not in promo_dict.keys():
        promo_dict[0] = None

    filename_out = filename_in[:-4] + "_edited.csv"
    promo_sorted = {}
    for key in sorted(promo_dict.keys()):
        promo_sorted[key] = promo_dict[key]

    with open(filename_in, "r") as f_in:
        lines = f_in.readlines()

    header = lines.pop(0)
    header_list = header.strip().split(",")

    with open(filename_out, "w") as f_out:
        print(header[:-1], file=f_out)

        for line in lines:

            line_split = line.strip().split(",")
            index_price = int(line_split[-2])
            new_line = ",".join(line_split[:-4])
            status = line_split[-4]

            for key in promo_sorted.keys():
                if key <= index_price:
                    new_promo = promo_sorted[key]
                else:
                    break

            if status == "NOT FOR TRADE" or new_promo is None:
                new_line += f",{status},0,{index_price},0"
            else:
                new_line += f",{status},1,{index_price},{new_promo}"

            print(new_line, file=f_out)


if __name__ == "__main__":

    root = Tk()
    gui = GUI(root)
    root.mainloop()
