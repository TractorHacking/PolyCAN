from polycan.log_handler import *
from polycan.log import *
from polycan.firebase_interface import *
#from keras.models import Sequential
#from keras.layers import Dense
import collections
import sys
def log_menu(log, known):
    while(1):
        print("Log Menu")
        print("0. Display Log")
        print("1. Filter Log")
        print("2. Sort Log")
        print("3. Analyze Data")
        print("4. Return")
        choice = input("")
        try:
            option = int(choice)
        except:
            print("Please enter an integer for menu entry")
            continue
        if option == 0:
            log.display(known)
        if option == 1:
            filter_menu(log, known)
        elif option == 2:
            sort_menu(log, known)
        elif option == 3:
            detail_view(known,log)
        elif option == 4:
            return
        else:
            print("Please enter an integer for menu entry")
#def analyze_log(log, model):

def main_menu():
    known = get_known()
    uploaded_logs = []
    current_log = None
    while(1):
        print("\nMain Menu\n 1. Find Log\n 2. Find PGN\n 3. Import Log 4. Analyze Logs\
            \n 5. Exit\n")
        choice = input('')
        if (choice == "1"):
            current_log = find_log(uploaded_logs)
            log_menu(current_log, known)
        elif (choice == "2"):
            detail_view(known)
        elif (choice == "3"):
            import_log()
        #elif (choice == "4"):
        #    analyze_log(current_log, model)
        elif (choice == "5"):
            sys.exit()
        else:
            print("Error. Enter an integer between 1 and 5")
        current_log = None

def main():
    main_menu()
