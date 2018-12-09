from polycan import input_prompt
from .log_handler import *

# Initialize Globals 
current_log = []
log_cache = []

def filter_menu():
    print("Filter Menu\n")
    return

def sort_menu():
    print("Sort Menu\n")
    return

# This function is a submenu for log options
def log_menu():
    while(1):
        choice2 = input("1. Filter Log\n2. Sort Log\n3. Analyze Data\n4. Open another log\n5. Main menu\n\n")
        if choice2 == "1":
            filter_menu()
        elif choice2 == "2":
            sort_menu()
            '''
         #Fetch a log ordered by pgn
            target_log = db.collection(u'logs').document(name).collection(u'log').order_by(u'pgn').get()
            show_log(target_log, name)
            '''
        elif choice2 == "3":
            choice2 = input("Enter entry number: ")
            detail_view(data[int(choice2)][1], data[int(choice2)][6])
        elif choice2 == "4":
            switch_log()
        elif choice2 == "5":
            return
        else:
            print("Error. Enter an integer between 1 and 5\n")

def main_menu():
    while(1):
        print("\n1. Find Log\n2. Find PGN\n3. Import Log\n4. Exit\n")
        choice = input(input_prompt)
        if (choice == "1"):
            switch_log()
            log_menu()
        elif (choice == "2"):
            find_pgn()
        elif (choice == "3"):
            import_log()
        elif (choice == "4"):
            sys.exit()
        else:
            print("Error. Enter an integer between 1 and 5")

    

def main():
    print(
        "   ___       __     ________   _  __\n"
        "  / _ \___  / /_ __/ ___/ _ | / |/ /\n"
        " / ___/ _ \/ / // / /__/ __ |/    / \n"
        "/_/   \___/_/\_, /\___/_/ |_/_/|_/  \n"
        "            /___/                   \n")

    main_menu()
