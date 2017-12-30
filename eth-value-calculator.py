#!/usr/bin/env python3

import json
import requests
import csv
import sys
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-a", "--address", dest="address",
                  help="ETH address", metavar="ADDRESS")
(options, args) = parser.parse_args()

address = options.address

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

transaction_list = get_etherscan_transactions(address)

csv_writer = csv.writer(sys.stdout)
csv_writer.writerow([ "Block Number",
                      "Timestamp",
                      "Value ETH",
                      "Value USD" ])
for transaction in transaction_list:
  # Filter for nanopool and ethermine, respectively
  if (transaction['from'] == '0x52bc44d5378309ee2abf1539bf71de1b7d7be3b5') or \
     (transaction['from'] == '0xEA674fdDe714fd979de3EdF0F56AA9716B898ec8'):
    value_eth = float(transaction['value']) / 1000000000000000000.0
    value_usd = value_eth * get_eth_price(transaction['timeStamp'])
    csv_writer.writerow([ transaction['blockNumber'],
                          transaction['timeStamp'],
                          value_eth,
                          value_usd ])

