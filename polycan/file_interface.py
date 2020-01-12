import os
import csv
from polycan.canable import *
import pandas as pd
from polycan.menu import *
from pathlib import Path


def get_file_path(path):
    while (1):
        for root, dirs, files in os.walk(path):
            logs = list(filter(lambda x: x[-4:] == ".csv", files))
            choice = display_log_pages(dirs + logs + ["Go Back"])
            if (choice < len(dirs)):
                path = path + "/" + dirs[choice]
                break
            elif (choice < len(dirs) + len(logs)):
                return path + "/" + logs[choice - len(dirs)]
            else:
                return ""


def list_logs_file(self):
    path = Path(os.path.dirname(os.path.realpath(__file__)))
    print(path)


def open_log_file(uploaded_logs):
    while (1):
        filepath = input("Please enter path to .csv log file or q to quit: ")
        if filepath == 'q':
            return
        elif filepath[-4:] != ".csv":
            print("Bad file path")
            clear_screen()
        else:
            filename = filepath.rsplit('/', 1)[1]
            logname = filename.rsplit('.', 1)[0]
            print("Opening " + filename + "...")
            try:
                with open(filepath) as csvfile:
                    df = pd.read_csv(csvfile, sep=',')
                    df.columns = ['number', 'time', 'pgn', 'priority', 'source', 'destination', 'data', 'description']
                    uploaded_logs[logname] = df
                    return
            except FileNotFoundError:
                print("File not found, please try again")
                clear_screen()


def save_log(name, log_frame):
    path = "./logs"
    log_frame.to_csv((path + "/" + name + ".csv"))
    global line_offset
    return (line_offset + "Saved log to " + path + "/" + name + ".csv")


"""
 while(1):
     for root, dirs, files in os.walk(path):
         logs = list(filter(lambda x: x[-4:] == ".csv", files))
         choice = display_log_pages(["Cancel"] + dirs + logs)
         if (choice == 0):
             return
             
             if (len(path) > 7):
                 k = path.rfind("/")
                 path = path[:k]
             else:
                 return save_log(name, log_frame)
 


         elif (choice <= len(dirs) ):
             path = path+"/"+dirs[choice-1]
             break
         elif(choice <= len(dirs)+len(logs)):
             log_frame.to_csv((path+"/"+name+".csv"))
         else:
             return 

 """


def capture_log():
    global line_offset
    path = input(line_offset + 'Enter log name: ')
    path = "./logs/" + path
    if not (path[-4:] == ".csv"):
        path = path + ".csv"
    get_csv(path)
    input(line_offset + 'Press Enter to continue...')
    return


def sendAndCapture_log():
    global line_offset
    clear_screen()
    pathOut = input(line_offset + 'Enter log name to log to: ')
    pathOut = "./logs/" + pathOut
    if not (pathOut[-4:] == ".csv"):
        pathOut = pathOut + ".csv"
    input(line_offset + 'Select the log file you want to send...')
    pathIn = get_file_path("./logs/")
    if not (pathIn[-4:] == ".csv"):
        pathIn = pathIn + ".csv"
    sendCSVWhileRead(pathIn, pathOut)
    input(path_offset + 'Press Enter to continue...')
    return
