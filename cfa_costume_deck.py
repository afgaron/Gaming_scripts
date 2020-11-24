'''Simulates the costume deck for Costume Fairy Adventures, drawing without replacement until the deck is empty and then resetting. Doesn't track cards in play, however, so there will be a slight desync after shuffling.'''

import numpy as np

def draw(deck, n):
    '''Draws n cards from the costume deck without replacement; automatically shuffles when drawing from empty deck'''
    
    if n <= len(deck):
    
        rand_vals = np.random.random(n)
        rand_ints = set((rand_vals*len(deck)).astype(int))
        while len(rand_ints) != n:
            rand_val = np.random.random(1)
            rand_int = int(rand_val*len(deck))
            rand_ints.add(rand_int)
        
        for n, ix in enumerate(rand_ints):
            drawn = deck[ix-n]
            deck = np.delete(deck, ix-n)
            print(' %s' % drawn)
    
    else:
        
        excess = n - len(deck)
        deck = draw(deck, len(deck))
        print(' Reached end of deck; shuffling\n')
        deck = shuffle()
        deck = draw(deck, excess)
    
    return deck

def shuffle():
    '''"Shuffle" the costume deck by setting it equal to all costumes'''
    
    return np.array(["8-Bit Dress", "Admiral's Coat", "Alchemist's Frock", "Angelic Dress", "Artist's Smock", "Aviator Jacket", "Ball Gown", "Bandages", "Battle Kit", "Bee Suit", "Black Sweater", "Bow Tie", "Bunny Hat", "Camo Fatigues", "Cape & Tights", "Cardboard Robot", "Cat Hoodie", "Chef's Smock", "Clockwork Couture", "Clown Suit", "Cowgirl Outfit", "Crinoline Dress", "Cunning Disguise", "Dancer's Shawl", "Death Metal Regalia", "Deely-Boppers", "Deerstalker Cap", "Devil Corset", "Doctor's Coat", "Equestrian Outfit", "Evil Overlord Armour", "Feather Robe", "Figure Skates", "Firefighter's Uniform", "Flower Suit", "Fool's Motley", "Football Uniform", "Fur Loincloth", "Gambler's Duds", "Ghost Sheet", "Gothic Dress", "Greasy Coveralls", "Green Tunic", "Grim Reaper Robe", "Hockey Mask", "Holy Robes", "Horned Cowl", "Judge's Robes", "Karate Gi", "Kung Fu Jacket", "Lab Coat", "Leather Jerkin", "Magical Girl Dress", "Maid's Uniform", "Marching Band Uniform", "Mascot Suit", "MIB Suit", "Mushroom Hat", "Mysterious Cloak", "Nun's Habit", "Old Fedora", "Pajamas", "Pirate Costume", "Plate Mail", "Platypus Suit", "Polyester Suit", "Pop Idol Outfit", "Pot Lid Armour", "Princess Dress", "Protagonist's Garb", "Reporter's Outfit", "Robe & Wizard Hat", "Ruffled Tunic", "School Uniform", "Seamstress Outfit", "Shinobi Shozoku", "Shopkeeper's Apron", "Silk Topper", "Skateboard", "Sorceress' Gown", "Space-Age Armour", "Space Suit", "Spirit of Fall Dress", "Spirit of Spring Dress", "Spirit of Summer Dress", "Spirit of Winter Dress", "Squid Hat", "Star Captain's Uniform", "Star Soldier's Suit", "Straw Hat & Overalls", "Stripey Scarf", "Stylish Tux", "Survival Gear", "Swashbuckler's Coat", "Tacky Business Suit", "Tattered Cloak", "Teacher's Outfit", "Tie-Dyed Shirt", "Tin Soldier Outfit", "Tramp's Rags", "Trenchcoat & Katana", "Valkyrie Armour", "Vampire Makeup", "Viking Hat", "Wedding Dress", "White Greasepaint", "Witch's Hat", "Zombie Rags"])

def show(i):
    '''Print the drawn card to screen; not implemented yet'''
    
    img = io.imread(img_dir)
    plt.figure()
    plt.imshow(img)

if __name__ == '__main__':
    
    display = False
    val = None
    #while val not in ['y', 'Y', 'n', 'N']:
    #    val = raw_input('Display images (y/n)? ')
    #    if val in ['y', 'Y']:
    #        from skimage import io
    #        import matplotlib.pyplot as plt
    #        plt.ion()
    #        display = True
    
    print('Costume deck simulator for Costume Fairy Adventures')
    print('Enter any number to draw that many cards from the deck, or type "shuffle" to shuffle the discard pile back into the deck.')
    
    deck = shuffle()
    while True:
        try:
            val = raw_input('How many cards: ')
            if 'shuffle' in val.lower():
                deck = shuffle()
                print(' Shuffled deck')
            else:
                assert int(val)>0
                deck = draw(deck, int(val))
                print('')
        except (AssertionError, ValueError):
            print(' Not a valid number')
            pass
