#!/usr/bin/env python3

import json
import requests
import csv
import sys
from optparse import OptionParser
from flask import Flask, render_template, request, jsonify
from multiprocessing import Pool
import xlsxwriter
import datetime
from dateutil import parser as dateparser
from lib.eth import Eth
from lib.ubiq import Ubiq
from lib.btc import Btc
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

app = Flask(__name__)

@app.route("/")
def index():
  return render_template('index.html')

@app.route("/get-all-transactions/<address>", methods=['get', 'post'])
def get_transactions_table(address):
  logging.info("/get-all-transactions endpoint called with address: %s" % (address))
  from_list = [s.strip() for s in request.form['fromList'].splitlines()]
  from_list = [s for s in from_list if s != '']
  logging.debug("from_list: %s" % (from_list))
  currency_type = request.form['currencyType']

  currency_processor = { 
    "eth": Eth(address),
    "ubiq": Ubiq(address),
    "btc": Btc(address)
  }.get(currency_type.lower(), None) 

  if not currency_processor:
    return jsonify({'error': 'Unsupported currency type: %s, please check back later!' % (currency_type)})

  start_date = dateparser.parse(request.form['startDate']).timestamp()
  end_date = dateparser.parse(request.form['endDate']).timestamp()

  transactions = currency_processor.get_all_transactions(from_list, start_date, end_date)
  # Create xlsx file
  filename = currency_processor.write_xslx(transactions)
  logging.info("transactions returned: %s" % (transactions))
  return jsonify({'transactions': transactions,
                  'xslx_filename' : 'xlsx_files/%s' % filename})

parser = OptionParser()
parser.add_option("-a", "--address", dest="address",
                  help="(Required) ETH address")
parser.add_option("-c", "--currency", dest="currency_type",
                  help="(Default: eth) Currency type (etc, ubiq, btc)")
parser.add_option("-f", "--start-date", dest="start_date",
                  help="Start Date (e.g. 2020-02-01)")
parser.add_option("-t", "--end-date", dest="end_date",
                  help="End Date (e.g. 2020-02-01)")
parser.add_option("-l", "--from-list", dest="from_list",
                  help="From List")
parser.add_option("-d", "--debug", dest="debug", default=False,
                  help="Debug mode", action="store_true")
parser.add_option("-s", "--server", dest="server", default=False,
                  help="Run web server", action="store_true")
(options, args) = parser.parse_args()

if not options.address:
  parser.print_help()
  exit(1)

address = options.address

currency_type = 'eth' if options.currency_type == None else options.currency_type

currency_processor = {
  "eth": Eth(address),
  "ubiq": Ubiq(address),
  "btc": Btc(address)
}.get(currency_type)

start_date = options.start_date if options.start_date else None
end_date = options.end_date if options.end_date else None
from_list = options.from_list if options.from_list else None

# convert start/end dates to unix timestamps
from dateutil import parser
start_date = parser.parse(start_date).timestamp() if start_date else None
end_date = parser.parse(end_date).timestamp() if end_date else None

print("start_date: %s, end_date: %s" % (start_date, end_date))

if options.server:
  app.run(debug=options.debug, host='0.0.0.0')
else:
  currency_processor.dump_csv_stdout(start_date=start_date, end_date=end_date, from_list=from_list)
