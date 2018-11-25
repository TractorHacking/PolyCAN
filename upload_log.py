from tqdm import tqdm
import csv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

 #   for row in reader:
 #       print(row['first_name'], row['last_name'])

name = "test555"
#log = [{'time' : 0.001, 'pgn' : '0C000006', 'data' : 'test123' },
#       {'time' : 0.002, 'pgn' : '4206969', 'data' : '1337'}]

# Use a service account
cred = credentials.Certificate('secret.json')
firebase_admin.initialize_app(cred)

# Get Database
db = firestore.client()

doc_ref = db.collection(u'logs').document(u'5055E').collection(name)
x = 1

with open('Tractor.csv', newline='') as csvfile:
    log = csv.DictReader(csvfile)
    for line in tqdm(log):
        line_ref = doc_ref.document("Packet " + str(x))
        line_ref.set({
                u'time': line['Time'],
                u'pgn': line['ID'],
                u'data': line['Data']
                })
        x += 1

print("Uploaded", x-1, "lines.")
