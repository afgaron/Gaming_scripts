import requests
from pprint import pprint

# Necessary login information
username = 'example@pucatrade.com'
password = 'password123'

# Check first page of ledger to get dates
root_url = 'https://pucatrade.com'
login_url = root_url + '/login'
ledger_url = root_url + '/account/ledger/2012-01'
payload = {'login':username, 'password':password}

print('Checking dates...')
with requests.Session() as session:
    post = session.post(login_url, data=payload)
    r = session.get(ledger_url)

ledger_urls = []
for line in r.text.split('href="'):
	url = line.split('">')[0].split('" SELECTED>')[0]
	if 'ledger/2' in url:
		ledger_urls.append(root_url+url)

# Go through each page of ledger and sum up entries
transactions = {}
type_flag = '<div class="label letter">TYPE</div>'
points_flag = '<div class="label letter">POINTS</div>'

with requests.Session() as session:
	post = session.post(login_url, data=payload)
	for ledger_url in ledger_urls:
		print('Adding transactions from ' + ledger_url.split('/')[-1])
		r = session.get(ledger_url)
		for transaction in r.text.split(type_flag)[1:]:
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

pprint(transactions)

# Calculate some interesting statistics
for key in ['BONUS_incoming', 'SUBSCRIPTION_incoming', 'PUCASHIELD_outgoing', 'WANT_outgoing', 'PUCASHIELD_incoming', 'WANT_incoming', 'ADMIN_incoming', 'DISPUTE_incoming', 'ITEM_outgoing', 'SWEEPSTAKES_outgoing', 'TRANSFER_incoming', 'TRANSFER_outgoing', 'TRADE_incoming', 'TRADE_outgoing']:
	if key not in transactions.keys():
		transactions[key] = 0

starting = transactions['BONUS_incoming'] + transactions['SUBSCRIPTION_incoming']
fees = transactions['PUCASHIELD_outgoing'] + transactions['WANT_outgoing'] + transactions['PUCASHIELD_incoming'] + transactions['WANT_incoming']
payouts = transactions['ADMIN_incoming'] + transactions['DISPUTE_incoming']
misc = transactions['ITEM_outgoing'] + transactions['SWEEPSTAKES_outgoing'] + transactions['TRANSFER_incoming'] + transactions['TRANSFER_outgoing']
lost_to_fees = 1. * fees / (starting + transactions['TRADE_incoming'] + transactions['TRANSFER_incoming'])

print('Trade volume: %i sent and %i received' % (transactions['TRADE_incoming'], -1*transactions['TRADE_outgoing']))
print('Amount spent on fees: %i (%.1f percent of total points received)' % (-1*fees, -100*lost_to_fees))
print('Amount paid back by Pucashield: %i' % payouts)

input('Press Enter to quit')
