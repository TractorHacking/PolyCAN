from polycan.log_handler import *

# Initialize Globals 
current_log = []
log_cache = []

def filter_menu():
    while(1):
        choice = input("\nFilter Menu:\n 1. By PGN\n 2. Using Log Mask\n 3. Remove Filter\n 4. Main menu\n\n")
        if choice == "1":
            user_pgn = input("Enter a PGN: ")
            return filter_log('pgn', user_pgn)
        elif choice == "2":
            mask_data = prompt_log()
            mask_log = db.collection(u'logs').document(mask_data[1]).collection(u'log').order_by(u'time').get()
            target_log = db.collection(u'logs').document(name).collection(u'log').order_by(u'time').get()
            return show_log(target_log, name)
        elif choice == "3":
            return filter_log('none')
        elif choice == "4":
            return
        else:
            print("Error. Enter an integer between 1 and 5\n") 


def sort_menu():
    print("Sort Menu\n")
    return

# This function is a submenu for log options
def log_menu():
    while(1):
        choice2 = input("\nLog Menu\n 1. Filter Log\n 2. Sort Log\n 3. Analyze Data\n 4. Open another log\n 5. Main menu\n\n")
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
            detail_view(int(choice2))
        elif choice2 == "4":
            switch_log()
        elif choice2 == "5":
            return
        else:
            print("Error. Enter an integer between 1 and 5\n")

def main_menu():
    while(1):
        print("\nMain Menu\n 1. Find Log\n 2. Find PGN\n 3. Import Log\n 4. Exit\n")
        choice = input('')
        if (choice == "1"):
            switch_log()
            log_menu()
        elif (choice == "2"):
            detail_view()
        elif (choice == "3"):
            import_log()
        elif (choice == "4"):
            sys.exit()
        else:
            print("Error. Enter an integer between 1 and 5")

    

def main():

    main_menu()
