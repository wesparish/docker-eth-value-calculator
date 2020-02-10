from .cryptobase import CryptoBase
import requests
from multiprocessing import Pool
import sys
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class Btc(CryptoBase):
  def __init__(self, address):
    super(Btc, self).__init__(address)

  def get_single_transaction(self, transaction):
    logging.info("Fetching transaction from server for block %s..." % transaction['blockNumber'])
    value_crypto = float(transaction['value']) / 1000000000000000000.0
    value_usd = None
    while not value_usd:
      try:
        value_usd = value_crypto * self.get_price_from_api(transaction['timeStamp'])
      except Exception:
        logging.error("Caught exception")
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
    url = "https://min-api.cryptocompare.com/data/pricehistorical?fsym=BTC&tsyms=USD&ts=%s" % (timestamp)
    r = requests.get(url)
    r.raise_for_status()
    return r.json()['BTC']['USD']

  '''
  curl -d '{"addr":"bc1qdr0g7sxlw72fgu64j97f7lgzphn6288xffw6k2"}' https://www.blockonomics.co/api/searchhistory
  {
    "pending": [],
    "history": [
      {
        "time": 1581041825,
        "addr": [
          "bc1qdr0g7sxlw72fgu64j97f7lgzphn6288xffw6k2"
        ],
        "value": 1378429,
        "txid": "159175e3bab364451ff68f82e4c369df5914477118410bdbd6529d7ab1cdef91"
      },
  '''
  def get_transactions_from_api(self):
    url = "https://www.blockonomics.co/api/searchhistory"
    r = requests.post(url, data='{"addr": "%s"}' % self.address)
    r.raise_for_status()
    results = [ {'from': None,
                 'address': x['addr'][0],
                 'timeStamp': x['time'],
                 'value': x['value'] / 1000000000.00,
                 'blockNumber': 0,
                 } for x in r.json()['history'] ]
    logging.info("get_transactions_from_api() results: %s" % results)

    return results

