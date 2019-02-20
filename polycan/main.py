from polycan.log_handler import *
from polycan.log import *
from polycan.firebase_interface import *
import collections
import sys

def main_menu():
    known = get_known()
    uploaded_logs = {}
    current_log = None
    pd.option_context('display.max_rows', None, 'display.max_columns', None)
    while(1):
        print("\nMain Menu\n 1. Find Log\n 2. Find PGN\n 3. Import Log\n 4. Cooaaauuuuoompare Logs\n 5. Exit\n")
        choice = input('')
        if (choice == "1"):
            current_log = find_log(uploaded_logs)
            #current_log.columns = ['time', 'pgn', 'priority','source','destination', 'data']
            #current_log.insert(5, 'description', ["Unknown" if not log['pgn'][x] in known \
            #    else known[log['pgn'][x]].description for x in range(len(log))])
            log_menu(current_log, known)
        elif (choice == "2"):
            detail_view(known)
        elif (choice == "3"):
            import_log()
        elif (choice == "4"):
            helper = "ok"
            compare_log(uploaded_logs, known, helper)
        elif (choice == "import"):
            import_known("_idinfo/")
        elif (choice == "5"):
            sys.exit()
        else:
            print("Error. Enter an integer between 1 and 5")
        current_log = None
#main_menu()
def main():
    main_menu()
