from .cryptobase import CryptoBase
import requests
from multiprocessing import Pool
import sys
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class Ubiq(CryptoBase):
  def __init__(self, address):
    super(Ubiq, self).__init__(address)

  def get_single_transaction(self, transaction):
    logging.info("Fetching transaction from server for block %s..." % transaction['blockNumber'])
    value_crypto = float(transaction['value'])
    value_usd = None
    tries = 0
    while not value_usd and tries < 10:
      try:
        value_usd = value_crypto * self.get_price_from_api(transaction['timeStamp'])
      except Exception as ex:
        logging.error("Caught exception: %s" % (ex))
        tries += 1
    return { 'block_number': transaction['blockNumber'],
             'timestamp': transaction['timeStamp'],
             'value_crypto': value_crypto,
             'value_usd': value_usd,
             'from': transaction['from'] }

  def get_all_transactions(self, from_list=None, start_date=None, end_date=None):
    logging.info("Fetching transactions for address: %s" % (self.address))
    transaction_list = self.get_transactions_from_api()

    if from_list:
      # Lowercase from_list
      from_list = [address.lower() for address in from_list]
      transaction_list = [transaction for transaction in transaction_list if transaction['from'].lower() in from_list]

    if start_date:
      transaction_list = [transaction for transaction in transaction_list if float(transaction['timeStamp']) > start_date]

    if end_date:
      transaction_list = [transaction for transaction in transaction_list if float(transaction['timeStamp']) < end_date]

    return_list = []
    with Pool(processes=10) as pool:
      return_list = pool.map(self.get_single_transaction, transaction_list)

    for item in return_list:
      item.update( {"address":self.address} )

    return return_list

  def get_price_from_api(self, timestamp):
    url = "https://min-api.cryptocompare.com/data/pricehistorical?fsym=UBQ&tsyms=USD&ts=%s" % (timestamp)
    r = requests.get(url)
    r.raise_for_status()
    return r.json()['UBQ']['USD']

  def get_transactions_from_api(self):
    url = "https://ubiqexplorer.com/api/Account/%s?includeTop1000Transactions=true" % (self.address)
    r = requests.get(url)
    r.raise_for_status()
    retval = [{"blockNumber":transaction['blockNumber'],
               "from": transaction['from'],
               "address": transaction['to'],
               "timeStamp": transaction['timestamp'],
               "value": transaction['value']}
                 for transaction in r.json()['transactions']]

    return retval

