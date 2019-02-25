import os
import csv
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
