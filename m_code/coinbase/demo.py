import csv
import logging
import re

from datetime import datetime, timedelta
from handler.transaction_history import TransactionHistory
from handler.csv_processor import CSVProcessorV1, CSVProcessorV2

from context import myjinja2 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Customizing part
fiscalYear = 2024

processor = CSVProcessorV1()
transaction_history = processor.process_csv('example/transactions_2023.csv')

processor = CSVProcessorV2()
transaction_history = processor.process_csv('example/transactions_2024.csv',transaction_history)


#processor = CSVProcessorV1()

environment = myjinja2.get_environment()
template = environment.get_template("tax.jinja2")

#transaction_history = processor.process_csv('example/transactions.csv')

trans_report = transaction_history.get_report_for_year(fiscalYear)

content = template.render(
    transactions=trans_report["transactions"],
    coinstack_start=trans_report["coinstackStart"],
    coinstack_end=trans_report["coinstackEnd"],
    income_total=trans_report["incomeTotal"],
    paid_total=trans_report["paidTotal"],
    received_total=trans_report["receivedTotal"],
    fiscalYear=fiscalYear
)

with open("example/tax-report-"+str(fiscalYear)+".html", mode="w", encoding="utf-8") as file:
    file.write(content)





