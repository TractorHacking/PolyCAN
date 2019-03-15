import os
import csv
from polycan.canable import *
import pandas as pd
from polycan.menu import *

def get_file_path(path):
    while(1):
        for root, dirs, files in os.walk(path):
            logs = list(filter(lambda x: x[-4:] == ".csv", files))
            choice = display_log_pages(dirs + logs + ["Go Back"])
            if (choice < len(dirs)):
                path = path+"/"+dirs[choice]
                break
            elif(choice < len(dirs)+len(logs)):
                return path+"/"+logs[choice-len(dirs)]
            else:
                return ""
            
def open_log():
    path = "../logs"
    newpath = get_file_path(path)
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
        
def sendAndCapture_log():
    global line_offset
    clear_screen()
    pathOut = input(line_offset+'Enter log name to log to: ')
    pathOut = "../logs/"+pathOut
    if not(pathOut[-4:] == ".csv"):
        pathOut = pathOut+".csv"
    input(line_offset+'Select the log file you want to send...')
    pathIn = get_file_path("../logs/")
    if not(pathIn[-4:] == ".csv"):
        pathIn = pathIn+".csv"
    sendCSVWhileRead(pathIn,pathOut)
    input(path_offset+'Press Enter to continue...')
    return


def save_log(name, log_frame):
    path = "../logs"
    log_frame.to_csv((path+"/"+name+".csv"))
    global line_offset
    input(line_offset+"Saved log to "+path+"/"+name+".csv")
    '''
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

'''
def capture_log():
    global line_offset
    path = input(line_offset+'Enter log name: ')
    path = "../logs/"+path
    if not(path[-4:] == ".csv"):
        path = path+".csv"
    get_csv(path)
    input(line_offset+'Press Enter to continue...')
    return

