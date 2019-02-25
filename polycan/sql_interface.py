from tqdm import tqdm
import csv
import os 
import sys
import collections
import pandas as pd
import glob
import mysql.connector
from mysql.connector import Error
import glob
import ntpath
import subprocess as sp

global database

class db:
    def __init__(self, password):
        self.passwd = password
        self.connection = mysql.connector.connect(host='tractor-hackers.chfkczch0d9t.us-east-1.rds.amazonaws.com',
                                                  database='tractorhackers',
                                                  user='tractormaster',
                                                  passwd=password)
        if self.connection.is_connected():
            self.cursor = self.connection.cursor()

    def clear_screen(self):
        sp.call('clear',shell=True)
        return
        
    def get_known(self):
        return []

    def list_logs(self):
        query = "SELECT name FROM `5055E` GROUP BY name"
        names = [] 
        self.cursor.execute(query)
        for name in self.cursor:
            names.append(name[0])
        return names

    def import_logs(self):
        #launch_menu(files)
        
        end_messages = []
        print("Uploading Logs...\n")
        db_Info = self.connection.get_server_info()
        files = glob.glob("../logs/*.csv")
        logs = self.list_logs()
        for file in tqdm(files):
            name = ntpath.basename(file)[:-4]
            print(name)
            if (name in logs):
                end_messages.append("Log already exists: " + name)
                self.clear_screen()
                print("Uploading Logs...\n")
                continue
            try:
                print("\nUploading " + name + "...") 
                with open(file, newline='') as csvfile:
                    log = csv.DictReader(csvfile)                    
                    sql_insert_query = "INSERT INTO `5055E` (`name`, `pgn`, `destination`, `source`, `priority`, `time`, `data`) VALUES (%s,%s,%s,%s,%s,%s,%s)"
                    records = []
                    for line in log:
                        data = (ntpath.basename(file)[:-4], 
                                int(line['PGN'], 10),
                                int(line['DA'], 10),  
                                int(line['SA'], 10), 
                                int(line['Priority'], 10), 
                                float(line['Time']), 
                                line['Data']) 
                        records.append(data)
                #cursor.execute(sql_insert_query, data) 
                    result  = self.cursor.executemany(sql_insert_query, records)
                    self.connection.commit()
                    end_messages.append("Log sucessfully uploaded: " + name)
            except FileNotFoundError:
                print("Error. File not found.")
                continue
            self.clear_screen()
            print("Uploading Logs...\n")
        for line in end_messages:
            print(line)
        return

    def get_log(self, log):
        #columns=["time","pgn", "priority", "source", "destination", "data"]
        query = 'SELECT time, pgn, priority, source, destination, data FROM `5055E` WHERE `name` = "%s" ORDER BY `time`'
        df = pd.read_sql((query % log), con=self.connection)
       # print(df)
        return df
    
    def close(self):
        if(self.connection.is_connected()):
            self.cursor.close()
            self.connection.close()

def init_db(password):
    global database 
    database = db(password)
    return

def get_log(log, known):
    return database.get_log(log)

def close_db():
    database.close()

def import_logs():
    database.import_logs()
    input('')
    return

def get_lognames():
    return database.list_logs()

def get_known():
    return database.get_known()
