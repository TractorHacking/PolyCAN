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

# To Do: Find the mean and variance of dT for a given pgn
def get_statistics(pgn, log):
    pass
#    return {"mean": mean, "variance": variance}

# To Do: Add a detail view for known packets
def detail_view(pgn, data):
    print(pgn)
    print(data)
    return

#This function allows the user to search all known pgns for a specific entry
def find_pgn():
    pgn = input("\nPlease enter PGN or 'q' to return to main menu: ")
    if pgn == 'q':
        return
    known = db.collection(u'known').where(u'pgn', u'==', pgn).get()
    list_known = [x for x in known]
    len_known = len(list_known)
    if len_known == 0:
        print('\nError: unknown PGN \'{}\'. Please try again.\n'.format(pgn))
        return find_pgn()
    print("\nFound %d known CAN bus IDs:" % len_known)
    for record in list_known:
        recdict = record.to_dict()
        print(u'{rid}:'.format(rid=record.id))
        print(u'\tPGN:\t{}'.format(recdict['pgn']))
        print(u'\tSource Address:\t{}'.format(recdict['source']))
        print(u'\tPriority:\t{}'.format(recdict['priority']))
        print(u'\tDescription:\t{}\n------------------'.format(recdict['description']))
    return find_pgn()

# This function gets the name of all logs in database
# It prompts the user to select one and returns a list containing [target_log, name] 
def prompt_log():
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
            return main_menu()
        print("")
        choice = int(input(input_prompt))
        if (choice == 0):
            return
        elif (choice > 0 and choice <= len(log_names)):
            target_log = db.collection(u'logs').document(log_names[choice-1]).collection(u'log').order_by("time").get()
            return [target_log, log_names[choice-1]]
        else:
            print("Error. Enter an integer between 0 and " + str(x))        

#This function takes the name of the log to be filtered and allows the user to select filter options
#It queries the database with the filter configuration and displays the filtered list using show_log
def filter_log(name):
    while(1):
        choice = input("\n1. By PGN\n2. Using Log Mask\n3. Remove Filter\n4. Main menu\n\n")
        if choice == "1":
            user_pgn = input("Enter a PGN: ")
            target_log = db.collection(u'logs').document(name).collection(u'log').where(u'pgn', u'==', int(user_pgn)).order_by(u'time').get()
            return show_log(target_log, name)
        elif choice == "2":
            mask_data = prompt_log()
            mask_log = db.collection(u'logs').document(mask_data[1]).collection(u'log').order_by(u'time').get()
            target_log = db.collection(u'logs').document(name).collection(u'log').order_by(u'time').get()
            return show_log(target_log, name)
        elif choice == "3":
            target_log = db.collection(u'logs').document(name).collection(u'log').order_by(u'time').get()
        elif choice == "4":
            return
        else:
            print("Error. Enter an integer between 1 and 5\n")

#This function gets known packet data and tags all the packets in the log
#It then tabulates the data and displays to the user
#This function then allows the user to choose analysis options
def show_log(docs, name):
    k = db.collection(u'known').get()
    known = {}
    for entry in k:
        e = entry.to_dict()
        known[int(e['pgn'])] = e['description']
    data = []
    x = 1
    for doc in docs:
        d = doc.to_dict()
        dlist = [d['time'], d['pgn'], d['priority'], d['source'], d['destination']]
        if d['pgn'] in known:
            dlist.append(known[d['pgn']])
        else:
            dlist.append("Unknown")
        dlist.append(d['data'])
        # Add packet to data
        data.append(dlist)

    #Print all data using tabluate
    print("")
    print(tabulate(data, headers=["time","pgn", "prty", "src", "dest", "description", "data" ], showindex = True, tablefmt = "pipe"))
    print("")

    while(1):
        choice2 = input("1. Filter\n2. Sort by PGN\n3. Get entry information\n4. Open another log\n5. Main menu\n\n")
        if choice2 == "1":
            return filter_log(name)
        elif choice2 == "2":
            #Fetch a log ordered by pgn
            target_log = db.collection(u'logs').document(name).collection(u'log').order_by(u'pgn').get()
            return show_log(target_log, name)
        elif choice2 == "3":
            choice2 = input("Enter entry number: ")
            detail_view(data[int(choice2)][1], data[int(choice2)][6])
        elif choice2 == "4":
            return find_log()
        elif choice2 == "5":
            return
        else:
            print("Error. Enter an integer between 1 and 5\n")

#This function just forwards the info from prompt_log to show_log
def find_log():
    log_info = prompt_log()
    show_log(log_info[0], log_info[1])
    return

#This function allows the user to add a csv log to the database
def import_log():
    batch = db.batch()
    path = input("\nEnter file path: ")
    if len(path) <= 4:
        print("Error, Invalid File Name")
        return
    x = 0
    try:
        with open("logs/"+path, newline='') as csvfile:
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
            print("Error. Enter an integer between 1 and 5")


# Main
print(
"   ___       __     ________   _  __\n"
"  / _ \___  / /_ __/ ___/ _ | / |/ /\n"
" / ___/ _ \/ / // / /__/ __ |/    / \n"
"/_/   \___/_/\_, /\___/_/ |_/_/|_/  \n"
"            /___/                   \n")

main_menu()
