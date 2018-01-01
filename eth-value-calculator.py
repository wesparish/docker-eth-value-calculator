#!/usr/bin/env python3

import json
import requests
import csv
import sys
from optparse import OptionParser
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route("/")
def hello():
  return render_template('index.html')

@app.route("/get-all-transactions/<address>")
def get_transactions_table(address):
  print("/get-all-transactions endpoint called with address: %s" % (address))
  transactions = get_all_transactions(address)
  print("transactions returned: %s" % (transactions))
#  return render_template('index.html', transactions=transactions)
  return jsonify(transactions)

parser = OptionParser()
parser.add_option("-a", "--address", dest="address",
                  help="ETH address")
parser.add_option("-d", "--debug", dest="debug", default=False,
                  help="Debug mode", action="store_true")
parser.add_option("-s", "--server", dest="server", default=False,
                  help="Run web server", action="store_true")
(options, args) = parser.parse_args()

def get_eth_price(timestamp):
  url = "https://min-api.cryptocompare.com/data/pricehistorical?fsym=ETH&tsyms=USD&ts=%s" % (timestamp)
  r = requests.get(url)
  r.raise_for_status()
  return r.json()['ETH']['USD']

def get_etherscan_transactions(address):
  url = "http://api.etherscan.io/api?module=account&action=txlist&address=%s&startblock=0&endblock=99999999&sort=asc" % (address)
  r = requests.get(url)
  r.raise_for_status()
  return r.json()['result']

def dump_csv_stdout(address):
  print("Please wait, fetching all transactions")
  all_transactions = get_all_transactions(address)
  print("all transactions = %s" % (all_transactions))

  csv_writer = csv.writer(sys.stdout)
  csv_writer.writerow([ "Block Number",
                        "Timestamp",
                        "Value ETH",
                        "Value USD" ])

  for transaction in all_transactions:
          csv_writer.writerow([ transaction['block_number'],
                                transaction['timestamp'],
                                transaction['value_eth'],
                                transaction['value_usd'] ])

def get_all_transactions(address):
  print("Fetching transactions for address: %s" % (address))
  transaction_list = get_etherscan_transactions(address)
  
  return_list = []

  for transaction in transaction_list:
    print("Fetching transaction from server...")
    # Filter for nanopool and ethermine, respectively
    if (transaction['from'] == '0x52bc44d5378309ee2abf1539bf71de1b7d7be3b5') or \
       (transaction['from'] == '0xEA674fdDe714fd979de3EdF0F56AA9716B898ec8'):
      value_eth = float(transaction['value']) / 1000000000000000000.0
      value_usd = value_eth * get_eth_price(transaction['timeStamp'])
      return_list.append( { 'address' : address, 
                            'block_number': transaction['blockNumber'],
                            'timestamp': transaction['timeStamp'],
                            'value_eth': value_eth,
                            'value_usd': value_usd } )

  return return_list

if options.server:
  app.run(debug=options.debug, host='0.0.0.0')
else:
  dump_csv_stdout(options.address)

