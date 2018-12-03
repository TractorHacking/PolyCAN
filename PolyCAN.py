from tqdm import tqdm
from tabulate import tabulate
import csv
import sys
import collections
import firebase_admin
from firebase_admin import credentials
from firebase_admin  import firestore
import google.cloud.exceptions

input_prompt = ""

# Use a service account
cred = credentials.Certificate('secret.json')
firebase_admin.initialize_app(cred)

# Get Database
db = firestore.client()
name = 'Example'

# To Do: Add a detail view for known packets
def detail_view(entry):
    print("Feature not yet implemented\n")
    return

# To Do: Add a search by pgn functionality
def find_pgn():
    print("Feature not yet implemented\n")
    return

# To Do: Find the mean and variance of dT for a given pgn
def get_statistics(pgn, log):
    pass
#    return {"mean": mean, "variance": variance}

# To Do: Compare logs 
def compare_logs(log1, log2):
    pass



def show_log(docs, name):
    k = db.collection(u'known').get()
    known = {}
    for entry in k:
#This can be uncommented once all entrys in the known table contain a pgn and desription.
#        e = entry.to_dict()
#        known[e['pgn']] = e['description']
        pass
    data = []
    x = 1
    for doc in docs:
        d = doc.to_dict()
        dlist = [d['time'], d['pgn'], d['priority'], d['source'], d['destination']]
        if d['pgn'] in known:
            dlist.append(known[d['pgn']]['description'])
        else:
            dlist.append("Unknown")
        dlist.append(d['data'])
        # Add packet to data
        data.append(dlist)
    #Print all data using tabluate
    print("")
    print(tabulate(data, headers=["time","pgn", "prty", "src", "dest", "description", "data" ], showindex = True, tablefmt = "pipe"))
    print("")
    return

    while(1):
        cmd = input("PolyCAN> ")
        if (cmd == 'quit'):
            main_menu()
        elif (cmd == 'help'):
            print("\nType a pgn to get more information about the data it contains\nType 'quit' to return to the main menu\n")
        elif cmd in known:
            print(known)
        else:
            print("Error, PGN not found.\n")
       
def find_log():
    while(1):
        logs = db.collection(u'logs').get()
        x = 1
        log_names = []

        print("\n0. Main Menu")
        for log in logs:
            log_names.append(log.id)
            print("{num}. {name}".format(num=x, name=log.id))
            x+=1
        if len(log_names) == 0:
            print("No logs found. Press 3 to import a log file.")
            main_menu()
        print("")
        choice = int(input(input_prompt))
        if (choice == "0"):
            return
        elif (choice > 0 and choice <= len(log_names)):
            target_log = db.collection(u'logs').document(log_names[choice-1]).collection(u'log').order_by("time").get()
            show_log(target_log, name=log_names[choice-1])
            return
        else:
            print("Error. Enter an integer between 0 and " + str(x))        
       
def import_log():
    batch = db.batch()
    path = input("\nEnter file path: ")
    if len(path) <= 4:
        print("Error, Invalid File Name")
        return
    x = 0
    try:
        with open(path, newline='') as csvfile:
            log = csv.DictReader(csvfile)
            doc_ref = db.collection(u'logs').document(path[:-4]).collection('log')
            db.collection(u'logs').document(path[:-4]).set({u'model': '5055E'})
            print("\nUploading " + path[:-4] + "...") 
            for line in tqdm(log):
                line_ref = doc_ref.document(line['time'])
                batch.set(line_ref,{ u'pgn': int(line['pgn'], 16),
                                     u'destination': int(line['destination'], 16),
                                     u'source': int(line['source'], 16),
                                     u'priority': int(line['source'], 16),
                                     u'time': float(line['time']),
                                     u'data': line['data']
                                     })
                x += 1
                if x % 500 == 0:
                    batch.commit()
            print("Uploaded", x-2, "lines.")
    except FileNotFoundError:
        print("Error. File not found.")
        

def main_menu():
    while(1):
        print("\n1. Find Log\n2. Find PGN\n3. Import Log\n4. Exit\n")
        choice = input(input_prompt)
        if (choice == "1"):
            find_log()
        elif (choice == "2"):
            find_pgn()
        elif (choice == "3"):
            import_log()
        elif (choice == "4"):
            sys.exit()
        else:
            print("Error. Enter an integer between 1 and 3")

print(
"   ___       __     ________   _  __\n"
"  / _ \___  / /_ __/ ___/ _ | / |/ /\n"
" / ___/ _ \/ / // / /__/ __ |/    / \n"
"/_/   \___/_/\_, /\___/_/ |_/_/|_/  \n"
"            /___/                   \n")

main_menu()
