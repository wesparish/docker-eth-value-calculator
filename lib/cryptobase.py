from abc import ABC, abstractmethod
import csv
import sys
import xlsxwriter
import datetime
import logging
import time
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class CryptoBase(ABC):
  def __init__(self, address):
    self.address = address

  @abstractmethod
  def get_price_from_api(self, timestamp):
    pass
  
  @abstractmethod
  def get_transactions_from_api(self):
    pass
  
  @abstractmethod
  def get_single_transaction(self, transaction):
    pass
  
  @abstractmethod
  def get_all_transactions(self, from_list=None, start_date=None, end_date=None):
    pass

  def dump_csv_stdout(self, from_list=None, start_date=None, end_date=None):
    logging.info("Please wait, fetching all transactions")
    all_transactions = self.get_all_transactions(from_list, start_date, end_date)
    logging.info("all transactions = %s" % (all_transactions))
  
    csv_writer = csv.writer(sys.stdout)
    csv_writer.writerow([ "Block Number",
                          "Timestamp",
                          "Value Crypto",
                          "Value USD" ])
  
    for transaction in all_transactions:
            csv_writer.writerow([ transaction['block_number'],
                                  transaction['timestamp'],
                                  transaction['value_crypto'],
                                  transaction['value_usd'] ])
  
    self.write_xslx(all_transactions)
  
  def write_xslx(self, transaction_list):
    filename = "%s_%s.xlsx" % (self.address, int(time.time()))
    workbook = xlsxwriter.Workbook('static/xlsx_files/%s' % filename)
    worksheet1 = workbook.add_worksheet()
    bold = workbook.add_format({'bold': 1})
    date_format = workbook.add_format({'num_format': 'mm/dd/yy hh:mm:ss'})

    # Set col widths
    worksheet1.set_column('A:A', 16)
    worksheet1.set_column('B:C', 45)
    worksheet1.set_column('D:G', 16)

    # Create table
    worksheet1.add_table(0, 0, len(transaction_list), 6,
                           {'columns': [{'header': 'Block Number'},
                                        {'header': 'From'},
                                        {'header': 'Address'},
                                        {'header': 'Timestamp'},
                                        {'header': 'Date'},
                                        {'header': 'Value Crypto'},
                                        {'header': 'Value Usd'}]})

    data_row_start = 1
    for row_num, transaction in enumerate(transaction_list):
      worksheet1.write(data_row_start + row_num, 0, int(transaction['block_number']))
      worksheet1.write(data_row_start + row_num, 1, transaction['from'])
      worksheet1.write(data_row_start + row_num, 2, transaction['address'])
      worksheet1.write(data_row_start + row_num, 3, int(transaction['timestamp']))
      timestamp = datetime.datetime.fromtimestamp(float(transaction['timestamp']))
      worksheet1.write_datetime(data_row_start + row_num, 4, timestamp, date_format)
      worksheet1.write(data_row_start + row_num, 5, transaction['value_crypto'])
      worksheet1.write(data_row_start + row_num, 6, transaction['value_usd'])
    workbook.close()

    return filename

