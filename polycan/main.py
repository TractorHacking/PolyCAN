from polycan.file_interface import *
from polycan.menu import *
from polycan.log_handler import *
from polycan.log import *
from polycan.sql_interface import *
from polycan.log_viewer import *
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
        text_output = []
        for name in logs:
            print(save_log(name, get_log(name)))
        input('')
    elif (choice == 1):
        known = []
        log_name = find_log()
        log = get_log(log_name)
        input(save_log(log_name, log))
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
                clear_screen()
                print(line_offset+"Error, invalid login (Press enter to continue)...")
                input('')
            if (using_database):
                break
        elif line_select == 1:
            using_database = False
            break
        elif line_select == 2:
            clear_screen()
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
    uploaded_logs = {}
    while(1):
        if (using_database):
            option_four = "Account Settings"
            known = get_known()
        else:
            option_four = "Login"
            known = []
        main_text = ["Open Log", "Log Menu", "Capture Log", "Send While Capturing Data","Compare Logs", "Lookup PGN", "Manipulate Log", option_four, "Exit"]
        choice = launch_menu(main_text)
        if (choice == 0): 
#  main_text = ["Open Log", "Log menu", "Capture Log", "Send While Capturing Data","Compare Logs", "Lookup PGN", option_four, "Exit"]
            if len(uploaded_logs) == 2:
                clear_screen()
                print("Too many logs open")
            else:
                open_log(uploaded_logs, known)
        elif choice == 1:
            if len(uploaded_logs) == 0:
                clear_screen()
                print("No logs open")
            else: 
                log_viewer = LogViewer(uploaded_logs, known)
                log_viewer.log_menu()
        elif (choice == 2):
            capture_log()
        elif (choice == 3):
            sendAndCapture_log()
        elif (choice == 4):
            helper = "ok"
            compare_logs({}, known, helper)
        elif (choice == 5):
            if (using_database):
                get_pgn(known)
            else:
                input(line_offset+"You must log in to use this feature...")
        elif (choice == 6):
            manipulate_logs(using_database)
        elif (choice == 7):
            if(using_database):
                user_menu()
            else:
                login_menu()
        elif (choice == 8):
            sys.exit()
def main():
    login_menu()
    main_menu()

