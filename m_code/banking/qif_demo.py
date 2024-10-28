import quiffen
import csv

from datetime import datetime

qif = quiffen.Qif()

acc = quiffen.Account(name='Girokonto',account_type='Bank')

qif.add_account(acc)


with open('transactions.csv', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for idx, row in enumerate(spamreader):
        if idx > 4 and row[1] != "":
            if row[2] == "Vorgemerkt":
                continue
            print(row[2])
            amount = float(row[8].replace('.','').replace(',','.'))
            date = datetime.strptime(row[1], '%d.%m.%y')
            print( str(idx))
            print(', '.join(row))
            memo = row[5]
            payee = ""
            # Zahlungsempfänger
            if row[6] == "Eingang":
                payee = row[3]
            elif row[6] == "Ausgang":
                payee = row[4]
            else:
                print("Unbekannter Transaktionstyp:"+row[6])
            tr = quiffen.Transaction(
                date=date, 
                amount=amount,
                #to_account=
                payee= payee,
                memo=memo,
            )
            acc.add_transaction(tr, header='Bank')


#groceries = quiffen.Category(name='Groceries')

#essentials = quiffen.Category(name='Essentials')

#groceries.add_child(essentials)

#qif.add_category(groceries)


qif.to_qif(path="output.qif")