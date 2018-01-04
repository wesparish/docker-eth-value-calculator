#!/usr/bin/env python3

import json
import requests
import csv
import sys
from optparse import OptionParser
from flask import Flask, render_template, request, jsonify
from multiprocessing import Pool

app = Flask(__name__)

@app.route("/")
def hello():
  return render_template('index.html')

@app.route("/get-all-transactions/<address>", methods=['get', 'post'])
def get_transactions_table(address):
  print("/get-all-transactions endpoint called with address: %s" % (address))
  from_list = [s.strip() for s in request.form['fromList'].splitlines()]
  from_list = [s for s in from_list if s != '']
  print("from_list: %s" % (from_list))
  currency_type = request.form['currencyType']

  if not currency_type.lower() == "eth":
    return jsonify({'error': 'Unsupported currency type: %s, please check back later!' % (currency_type)})

  transactions = get_all_transactions(address, from_list)
  print("transactions returned: %s" % (transactions))
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

def get_single_transaction(transaction):
  print("Fetching transaction from server for block %s..." % transaction['blockNumber'])
  value_eth = float(transaction['value']) / 1000000000000000000.0
  value_usd = None
  while not value_usd:
    try:
      value_usd = value_eth * get_eth_price(transaction['timeStamp'])
    except Exception:
      print("Caught exception")
  return { 'block_number': transaction['blockNumber'],
           'timestamp': transaction['timeStamp'],
           'value_eth': value_eth,
           'value_usd': value_usd,
           'from': transaction['from'] }

def get_all_transactions(address, from_list):
  print("Fetching transactions for address: %s" % (address))
  transaction_list = get_etherscan_transactions(address)

  transaction_list = [transaction for transaction in transaction_list if transaction['from'] in from_list]
  
  return_list = []
  with Pool(processes=10) as pool:
    return_list = pool.map(get_single_transaction, transaction_list)

  for item in return_list:
    item.update( {"address":address} )

  return return_list

if options.server:
  app.run(debug=options.debug, host='0.0.0.0')
else:
  dump_csv_stdout(options.address)

