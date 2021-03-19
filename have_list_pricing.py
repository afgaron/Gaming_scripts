'''
This work is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License. Original author is dude1818 on PucaTrade.com (https://pucatrade.com/profiles/show/129317)
'''

import tkinter as tk
from tkinter import filedialog as fd

# GUI to enter promo values
class GUI(tk.Tk):
    def __init__(self, filename, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("PucaTrade Marketplace Pricer")
        #self.filename = fd.askopenfilename()
        self.filename = filename
        self.button_add = None
        self.button_quit = None
        self.prices = []
        self.promos = []
        self.row_count = 0
        self.add_row()

    def add_row(self):
        if self.button_add is not None:
            self.button_add.grid_forget()
        if self.button_quit is not None:
            self.button_quit.grid_forget()
        self.prices.append(tk.Entry())
        self.prices[-1].grid(row=self.row_count, column=0)
        self.promos.append(tk.Entry())
        self.promos[-1].grid(row=self.row_count, column=1)
        self.button_add = tk.Button(text="Add another row", command=self.add_row)
        self.button_add.grid(
            row=self.row_count + 1, column=0, columnspan=2, sticky=tk.W + tk.E
        )
        self.button_quit = tk.Button(
            text="Apply and close", command=self.apply_and_close
        )
        self.button_quit.grid(
            row=self.row_count + 2, column=0, columnspan=2, sticky=tk.W + tk.E
        )
        self.row_count += 1

    def apply_and_close(self):
        prices = [price.get() for price in self.prices]
        promos = [promo.get() for promo in self.promos]
        # add validation
        #edit_file(self.filename, dict(zip(prices, promos)))
        print(self.filename, dict(zip(prices, promos)))
        self.quit()
        #self.destroy()


def edit_file(filename_in, promo_dict):

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
                new_line += f",{status},0,,0"
            else:
                new_line += f",{status},1,,{new_promo}"

            print(new_line, file=f_out)

if __name__ == "__main__":

    filename = fd.askopenfilename()
    
    root = GUI(filename)
    root.mainloop()
