from polycan.log_handler import *
from polycan.log import *
from polycan.firebase_interface import *
import collections
import sys

def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

def main_menu():
    known = get_known()
    uploaded_logs = {}
    current_log = None
    #pd.option_context('display.max_rows', None, 'display.max_columns', None)
    while(1):
        print("\nMain Menu\n 1. Find Log\n 2. Find PGN\n 3. Import Log\n 4. Cooaaauuuuoompare Logs\n 5. Exit\n")
        choice = input('')
        if (choice == "1"):
            log_name = find_log()
            if log_name in uploaded_logs:
                log_menu(uploaded_logs[log_name], known, uploaded_logs)
            else:
                log = get_log(log_name)
                uploaded_logs[log_name] = log
                log_menu(log, known, uploaded_logs)
        elif (choice == "2"):
            get_pgn(known)
        elif (choice == "4"):
            print("okok")
            helper = "ok"
            compare_logs(uploaded_logs, known, helper)
            
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
