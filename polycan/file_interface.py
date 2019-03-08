import os
import csv
from polycan.canable import *
import pandas as pd
from polycan.menu import *

def open_log():
    path = "../logs"
    while(1):
        for root, dirs, files in os.walk(path):
            logs = list(filter(lambda x: x[-4:] == ".csv", files))
            choice = launch_menu(dirs + logs + ["Go Back"])
            if (choice < len(dirs)):
                path = path+"/"+dirs[choice]
                break
            elif(choice < len(dirs)+len(logs)):
                newpath = path+"/"+logs[choice-len(dirs)]
                print("Opening " + newpath + "...")
                with open(newpath) as csvfile:
                    log = csv.DictReader(csvfile)                    
                    records = {'time': [], 'pgn': [], 'priority': [], 'source': [], 'destination': [], 'data': []}
                    for line in log:
                        records['time'].append(float(line['Time']))
                        records['pgn'].append(int(line['PGN'], 10))
                        records['priority'].append(int(line['Priority'], 10))
                        records['source'].append(int(line['SA'], 10))
                        records['destination'].append(int(line['DA'], 10))
                        records['data'].append(line['Data'])
                    df = pd.DataFrame(data=records)
                    return df
            else:
                return pd.DataFrame(data={})

def sendAndCapture_log():
    pathOut = input('Enter log name to log to: ')
    pathOut = "../logs/"+pathOut
    if not(pathOut[-4:] == ".csv"):
        pathOut = pathOut+".csv"
    pathIn = input('Enter log file you want to send: ')
    pathIn = "../logs/"+pathIn
    if not(pathIn[-4:] == ".csv"):
        pathIn = pathIn+".csv"
    sendCSVWhileRead(pathIn,pathOut)
    input('Press Enter to continue...')
    return


def save_log(name, log_frame):
    path = "../logs"
    while(1):
        for root, dirs, files in os.walk(path):
            logs = list(filter(lambda x: x[-4:] == ".csv", files))
            choice = launch_menu(["..."] + dirs + logs + ["Save"] + ["Cancel"])
            if (choice == 0):
                if (len(path) > 7):
                    k = path.rfind("/")
                    path = path[:k]
                else:
                    return save_log(name, log_frame)
            elif (choice <= len(dirs) ):
                path = path+"/"+dirs[choice-1]
                input('a')
                break
            elif(choice <= len(dirs)+len(logs)):
                input('b')
                log_frame.to_csv((path+"/"+name+".csv"))
            elif(choice == len(dirs) + len(logs) + 2):
                return
            else:
                return 


def capture_log():
    path = input('Enter log name: ')
    path = "../logs/"+path
    if not(path[-4:] == ".csv"):
        path = path+".csv"
    get_csv(path)
    input('Press Enter to continue...')
    return

