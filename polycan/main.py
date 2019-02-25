from polycan.file_interface import *
from polycan.menu import *
from polycan.log_handler import *
from polycan.log import *
from polycan.sql_interface import *
import polycan.keyreader as kr
import collections
import sys, os
import termios, fcntl
import select

global using_database

splash = ("   ___       __     ________   _  __\n"
          +"  / _ \___  / /_ __/ ___/ _ | / |/ /\n"
          +" / ___/ _ \/ / // / /__/ __ |/    / \n"
          +"/_/   \___/_/\_, /\___/_/ |_/_/|_/  \n"
          +"            /___/                   \n")

def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

def clear_screen():
    sp.call('clear',shell=True)
    print(splash)
    return

def login_menu():
    global using_database
    using_databse = False
    login_text = ["Login","Continue as Guest", "Quit"]
    while (1):
        line_select = launch_menu(login_text)
        if line_select == 0:
            clear_screen()
            username = input("Enter Username: ")
            password = input("Enter Password: ")
            try: 
                init_db(password)
                using_database = True
            except:
                using_database = False
                print("Error, invalid login (Press any key to continue)...")
                input('')
            if (using_database):
                break
        elif line_select == 1:
            using_database = False
            break
        elif line_select == 2:
            print("Goodbye\n")
            sys.exit()

def user_menu():
    items = ["Import Log", "Go Back"]
    choice = launch_menu(items)
    if (choice == 0):
        import_logs()
    else:
        return

def main_menu():
    global using_database
 
    uploaded_logs = {}
    current_log = None
    #pd.option_context('display.max_rows', None, 'display.max_columns', None)
    while(1):
        if (using_database):
            option_four = "Account Settings"
        else:
            option_four = "Login"
        main_text = ["Open Log", "Capture Log", "Compare Logs", "Lookup PGN", option_four, "Exit"]
        if(using_database):
            known = get_known()
        else:
            known = []
        
        choice = launch_menu(main_text)
        if (choice == 0):
            if (using_database):
                choice = launch_menu(["From Database", "From File"])
                if (choice == 0):
                    log_name = find_log()
                    log = get_log(log_name, known)
                    log_menu(log, known)
                    continue
            log = open_log()
            if (log.empty): 
                continue
            log_menu(log, known)
        elif (choice == 1):
            capture_log()
        elif (choice == 2):
            helper = "ok"
            compare_logs(uploaded_logs, known, helper)
        elif (choice == 3):
            get_pgn(known)
        elif (choice == 4):
            if(using_database):
                user_menu()
            else:
                login_menu()
        elif (choice == 5):
            sys.exit()
        current_log = None
def main():
    login_menu()
    main_menu()

