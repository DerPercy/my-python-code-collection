import quiffen
import csv

from datetime import datetime

qif = quiffen.Qif()

acc = quiffen.Account(name='Girokonto',account_type='Bank')

qif.add_account(acc)


with open('transactions.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=';', quotechar='"')
    for idx, row in enumerate(spamreader):
        if idx > 6 and row[1] != "":
            amount = float(row[7].replace('.','').replace(',','.'))
            date = datetime.strptime(row[1], '%d.%m.%Y')
            print( str(idx))
            print(', '.join(row))
            tr = quiffen.Transaction(
                date=date, 
                amount=amount,
                #to_account=
                payee= row[3],
                memo=row[4]
            )
            acc.add_transaction(tr, header='Bank')


#groceries = quiffen.Category(name='Groceries')

#essentials = quiffen.Category(name='Essentials')

#groceries.add_child(essentials)

#qif.add_category(groceries)


qif.to_qif(path="output.qif")