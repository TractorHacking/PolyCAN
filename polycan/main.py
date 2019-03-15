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
def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

def clear_screen():
    sp.call('clear',shell=True)
    print(splash)
    return

def export_logs():
    choice = launch_menu(["Download all logs", "Download specific Log", "Cancel"]);
    if (choice == 0):
        logs = get_lognames()
        for name in logs:
            save_log(name, get_log(name))
    elif (choice == 1):
        known = []
        log_name = find_log()
        log = get_log(log_name)
        save_log(log_name, log)
    return

def login_menu():
    global using_database
    global line_offset
    using_databse = False
    login_text = ["Login","Continue as Guest", "Quit"]
    while (1):
        line_select = launch_menu(login_text)
        if line_select == 0:
            clear_screen()
            username = input(line_offset+"Enter Username: ")
            password = input(line_offset+"Enter Password: ")
            try: 
                init_db(username,password)
                using_database = True
            except:
                using_database = False
                print(line_offset+"Error, invalid login (Press any key to continue)...")
                input('')
            if (using_database):
                break
        elif line_select == 1:
            using_database = False
            break
        elif line_select == 2:
            print(line_offset+"Goodbye\n")
            sys.exit()

def user_menu():
    items = ["Upload Log", "Download Log", "Go Back"]
    choice = launch_menu(items)
    
    if (choice == 0):
        import_logs()
    elif (choice == 1):
        export_logs()
    
    return

def main_menu():
    global using_database
 
    while(1):
        if (using_database):
            option_four = "Account Settings"
            known = get_known()
        else:
            option_four = "Login"
        main_text = ["Open Log", "Capture Log", "Send While Capturing Data","Compare Logs", "Lookup PGN", "Manipulate Log", option_four, "Exit"]
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
            sendAndCapture_log()
        elif (choice == 3):
            helper = "ok"
            compare_logs({}, known, helper)
        elif (choice == 4):
            if (using_database):
                get_pgn(known)
            else:
                input(line_offset+"You must log in to use this feature...")
        elif (choice == 5):
            manipulate_logs(known, using_database)
        elif (choice == 6):
            if(using_database):
                user_menu()
            else:
                login_menu()
        elif (choice == 7):
            sys.exit()
def main():
    login_menu()
    main_menu()

