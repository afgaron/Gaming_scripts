# This work is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License. Original author is dude1818 on PucaTrade.com

########## Edit the following two variables with the name of your have list file and any number of thresholds you want ##########

file_in = '20200923-PucaTrade-PAPER-Have.csv'	# name of exported haves list
promo_threshold = { 0:		    None,	# don't list bulk for sale
                    100:		75,		# cards worth 100pp and above get 75% promo
                    300:		90, 	# cards worth 400pp and above get 100% promo
                    600:		100,
                    1200:       120}	# etc

########## Don't mess with anything below this line ##########

file_out = file_in[:-4]+'_edited.csv'
keys = promo_threshold.keys()
keys.sort()

with open(file_in, 'r') as f_in:
	lines = f_in.readlines()

header = lines.pop(0)
header_list = header.strip().split(',')

with open(file_out, 'w') as f_out:
	print >> f_out, header[:-1]
	
	for line in lines:
		line_split = line.strip().split(',')
		index_price = float(line_split[-2])
		new_promo = None
		for ix in range(len(keys)):
			if keys[ix]<=index_price and (ix+1==len(keys) or index_price<keys[ix+1]):
				new_promo = promo_threshold[keys[ix]]
				break
		
		new_line =  ','.join(line_split[:-3])
		if new_promo is None:
			new_line += ',0,,'
		else:
			new_line += ',1,,' + str(int(new_promo))
		
		print >> f_out, new_line
