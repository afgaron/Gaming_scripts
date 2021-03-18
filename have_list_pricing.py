# This work is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License. Original author is dude1818 on PucaTrade.com

########## Edit the following two variables with the name of your have list file and any number of thresholds you want ##########

file_in = "20210318-PucaTrade-PAPER-Have.csv"  # name of exported haves list
promo_threshold = {
    0: None,  # don't list bulk for sale
    100: 75,  # cards worth 100pp and above get 75% promo
    500: 105,  # etc.
    250: 95,  # cards worth 250pp and above get 95% promo
    1000: 115,
}

########## Don't mess with anything below this line ##########

file_out = file_in[:-4] + "_edited.csv"
promo_sorted = {}
for key in sorted(promo_threshold.keys()):
    promo_sorted[key] = promo_threshold[key]

with open(file_in, "r") as f_in:
    lines = f_in.readlines()

header = lines.pop(0)
header_list = header.strip().split(",")

with open(file_out, "w") as f_out:
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
