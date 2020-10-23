import requests, pprint, sys

# Backwards compatibility between Python 2 and 3
if sys.version_info.major == 3:
    raw_input = input

# Global variables
root_url = 'https://pucatrade.com'
login_url = root_url + '/login'

def get_session():
    '''Open the session on pucatrade.com'''
    
    # Necessary login information
    username = raw_input('Email address: ')
    password = raw_input('Password: ')
    
    # Check first page of ledger to get dates
    ledger_url = root_url + '/account/ledger/2012-01'
    payload = {'login':username, 'password':password}
    
    with requests.Session() as session:
        post = session.post(login_url, data=payload)
        r = session.get(ledger_url)
    
    return r, payload

def get_urls(r):
    '''Get the list of urls comprising the ledger'''
    
    print('Checking dates...')
    ledger_urls = []
    for line in r.text.split('href="'):
        url = line.split('">')[0].split('" SELECTED>')[0]
        if 'ledger/2' in url:
            ledger_urls.append(root_url+url)
    
    return ledger_urls

def get_transactions(ledger_urls, payload):
    '''Go through each page of ledger and sum up entries'''
    
    transactions = {}
    type_flag = '<div class="label letter">TYPE</div>'
    points_flag = '<div class="label letter">POINTS</div>'
    
    with requests.Session() as session:
        post = session.post(login_url, data=payload)
        for ledger_url in ledger_urls:
            r = session.get(ledger_url)
            trans_list = r.text.split(type_flag)[1:]
            print('Adding %i transactions from %s' % (len(trans_list), ledger_url.split('/')[-1]))
            
            for transaction in trans_list:
                type = transaction.split('"value letter">')[1].split('</div>')[0]
                points = transaction.split('POINTS')[1].split('"value">')[1].split('</div>')[0].strip()
                if 'Gift' in points:
                    points = 0
                else:
                    points = int(points)
                if points>0:
                    type += '_incoming'
                elif points<0:
                    type += '_outgoing'
                if type in transactions.keys():
                    transactions[type] += points
                else:
                    transactions[type] = points
    
    return transactions

def get_stats(transactions, fout):
    '''Calculate some interesting statistics'''
    
    for key in ['BONUS_incoming', 'SUBSCRIPTION_incoming', 'PUCASHIELD_outgoing', 'WANT_outgoing', 'PUCASHIELD_incoming', 'WANT_incoming', 'ADMIN_incoming', 'DISPUTE_incoming', 'ITEM_outgoing', 'SWEEPSTAKES_outgoing', 'TRANSFER_incoming', 'TRANSFER_outgoing', 'TRADE_incoming', 'TRADE_outgoing']:
        if key not in transactions.keys():
            transactions[key] = 0

    starting = transactions['BONUS_incoming'] + transactions['SUBSCRIPTION_incoming']
    shield_fees = transactions['PUCASHIELD_outgoing'] + transactions['PUCASHIELD_incoming']
    promo_fees = transactions['WANT_outgoing'] + transactions['WANT_incoming']
    fees = shield_fees + promo_fees
    payouts = transactions['ADMIN_incoming'] + transactions['DISPUTE_incoming']
    misc = transactions['ITEM_outgoing'] + transactions['SWEEPSTAKES_outgoing'] + transactions['TRANSFER_incoming'] + transactions['TRANSFER_outgoing']
    all_outgoing = transactions['TRADE_outgoing'] + transactions['TRANSFER_outgoing'] + transactions['ITEM_outgoing'] + transactions['SWEEPSTAKES_outgoing']

    print_and_save('Trade volume: %i sent and %i received' % (transactions['TRADE_incoming'], -1*transactions['TRADE_outgoing']), fout)
    print_and_save('Amount spent on promotion fees: %i' % abs(promo_fees), fout)
    print_and_save('Amount spent on Pucashield: %i' % abs(shield_fees), fout)
    print_and_save('Amount paid back by Pucashield: %i' % payouts, fout)
    print_and_save('Fraction of outgoing points spent on fees: %i/%i = %.3f' % (abs(fees), abs(all_outgoing), 1.*fees/all_outgoing), fout)

    raw_input('Press Enter to quit')

def print_and_save(text, fout):
    '''Print to command line and append to file'''
    
    print(text)
    with open(fout, 'a') as f:
        f.write(text+'\n')

if __name__ == '__main__':
    
    response, payload = get_session()
    while 'logged-out' in response.text:
        print 'Invalid credentials'
        response, payload = get_session()
    
    urls = get_urls(response)
    transactions = get_transactions(urls[:2], payload)
    
    fout = 'puca_transactions.txt'
    with open(fout, 'w') as f:
        f.write(pprint.pformat(transactions))
        f.write('\n\n')
        print('Transaction summary written to %s' % fout)
    
    get_stats(transactions, fout)
