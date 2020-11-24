'''Plots a histogram of the frequency of cards in a supplied text file, e.g. a deck list. Second and third arguments are optional and control the minimum frequency to appear in the plot (default 1) and whether or not to include lands (default False).'''

import numpy as np
import requests, sys
import matplotlib.pyplot as plt
plt.ion()

def read_cards(filename):
	
	print 'Getting card list from', filename

	with open(filename, 'r') as f:
		lines = f.readlines()

	counts, cards = [], []
	for line in lines:
		if line.strip() is not '':
			counts.append(int(line.split('x', 1)[0]))
			cards.append(line.split('x', 1)[1].split('(')[0].split('*')[0].split('/')[0].strip())

	counts = np.array(counts)
	cards = np.array(cards)

	card_dict = {}
	for card, count in zip(cards, counts):
		if card in card_dict:
			card_dict[card] += count
		else:
			card_dict[card] = count
	
	print '    Card list contained %i total cards, with %i unique names' % (sum(counts), len(card_dict))
	return card_dict

def get_frames(card_dict=None, filename=None):
	
	if card_dict is None:
		if filename is None:
			card_dict = read_cards()
		else:
			card_dict = read_cards(filename)
	
	print 'Getting frame codes from ScryFall; progress:'
	
	frame_dict = {'W':{}, 'U':{}, 'B':{}, 'R':{}, 'G':{}, 'Z':{}, 'C':{}, 'L':{}}
	
	n = 0
	for card in card_dict:
		if not n%100:
			print '    %i/%i' % (n, len(card_dict))
		
		r = requests.get('https://api.scryfall.com/cards/named?exact=' + card)
		if 'Land' in r.json()['type_line']:
			frame = 'L'
		elif len(r.json()['color_identity']) < 1:
			frame = 'C'
		elif len(r.json()['color_identity']) > 1:
			frame = 'Z'
		else:
			frame = r.json()['color_identity'][0]
		
		frame_dict[frame][card] = card_dict[card]
		n+=1
	
	print '    %i/%i' % (n, len(card_dict))
	return frame_dict

def make_plot(min_count=1, include_lands=False, frame_dict=None, filename=None):
	
	if frame_dict is None:
		frame_dict = get_frames(filename=filename)
	
	print 'Preparing bar graph'
	
	cmap = {'W':'snow', 'U':'blue', 'B':'black', 'R':'red', 'G':'green', 'Z':'gold', 'C':'silver', 'L':'peru'}
	
	names, colors, edges, counts = np.array([]), np.array([]), np.array([]), np.array([])
	for frame in cmap:
		if (frame!='L' or include_lands) and frame_dict[frame]!={}: 
			temp = np.array(frame_dict[frame].items())
			names = np.append(names, temp.T[0])
			colors = np.append(colors, [cmap[frame]]*len(temp))
			edges = np.append(edges, ['black' if frame=='W' else cmap[frame]]*len(temp))
			counts = np.append(counts, temp.T[1].astype(int))
	
	names = names[counts>=min_count]
	colors = colors[counts>=min_count]
	edges = edges[counts>=min_count]
	counts = counts[counts>=min_count]
	
	sorting = np.argsort(names)
	names = names[sorting]
	colors = colors[sorting]
	edges = edges[sorting]
	counts = counts[sorting]
	
	x = range(len(names))
	plt.bar(x, counts, color=colors, edgecolor=edges)
	plt.xticks(x, names, rotation=90)
	plt.xlim(-.5, len(x)-.5)
	plt.tight_layout()

if __name__ == '__main__':

    assert len(sys.argv)>=2, 'No file name provided'
    filename = sys.argv[1]
    
    if len(sys.argv)>=4:
        min_count = int(sys.argv[2])
        include_lands = bool(sys.argv[3])
    else:
        min_count = 1
        include_lands = False
    
    card_dict = read_cards(filename)
    frame_dict = get_frames(card_dict, filename)
    make_plot(min_count=min_count, include_lands=include_lands, frame_dict=frame_dict, filename=filename)
    
    val = None
    while val is None:
        val = raw_input('')
