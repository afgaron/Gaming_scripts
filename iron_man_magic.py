'''Build your deck using the every Magic card ever printed. No repeats except basic lands.
Requires an internet connection to run, and scikit-image and matplotlib to display card images.'''

import urllib2, os
import numpy as np

basic_land_prob = 0.3
gatherer = 'http://gatherer.wizards.com/Pages/Card/Details.aspx?action=random'
drawn_already = []

def draw(n):
	'''Draws n cards with a %i%% chance of being a basic land''' % int(100*basic_land_prob)
	
	rand_vals = np.random.random(n)
	for i in rand_vals:
		response = urllib2.urlopen(gatherer)
		html = response.read()
		cardname = html.split('<title>')[1].split('Gatherer')[0].split('(')[0].strip()
		
		if i < basic_land_prob:
			if i <= 0.2*basic_land_prob:
				cardname = 'Plains'
			elif 0.2*basic_land_prob <= i < 0.4*basic_land_prob:
				cardname = 'Island'
			elif 0.4*basic_land_prob <= i < 0.6*basic_land_prob:
				cardname = 'Swamp'
			elif 0.6*basic_land_prob <= i < 0.8*basic_land_prob:
				cardname = 'Mountain'
			elif 0.8*basic_land_prob <= i:
				cardname = 'Forest'
			print ' %s' % cardname
			if display:
				show(cardname)
			
		elif cardname not in drawn_already:
			if cardname not in ['Plains', 'Island', 'Swamp', 'Mountain', 'Forest', 'Wastes', \
								'Snow-Covered Plains', 'Snow-Covered Island', 'Snow-Covered Swamp', \
								'Snow-Covered Mountain', 'Snow-Covered Forest']:
				drawn_already.append(cardname)
			print ' %s' % cardname
			if display:
				show(cardname)
		
		else:
			draw(1)

def show(cardname):
	'''Get the scan off magiccards.info and print to screen'''
	
	search = 'http://magiccards.info/query?q=!' + cardname.replace(' ', '+')
	response = urllib2.urlopen(search)
	html = response.read()
	imgurl = html.split('div class="card-image"')[1].split('src="')[1].split('" />')[0]
	img = io.imread(imgurl)
	plt.figure()
	plt.imshow(img)

if __name__ == '__main__':
	
	try:
		display = False
		val = None
		while val not in ['y', 'Y', 'n', 'N']:
			val = raw_input('Display images (y/n)? ')
			if val in ['y', 'Y']:
				from skimage import io
				import matplotlib.pyplot as plt
				plt.ion()
				display = True
		
		while True:
			try:
				val = raw_input('How many cards to draw (leave blank to clear screen): ')
				if val == '':
					os.system('cls' if os.name == 'nt' else 'clear')
				else:
					assert int(val)>0
					draw(int(val))
			except (AssertionError, ValueError):
				print ' Not a valid number'
				pass
	
	except BaseException as e:
		print e
