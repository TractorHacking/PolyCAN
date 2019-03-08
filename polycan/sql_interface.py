from tqdm import tqdm
from polycan.log import *
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
from polycan import file_interface
global database

class db:
    
    def __init__(self, username, password):
        self.username = username
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

    def import_known_old_group(self):
        unique = []
        print("Uploading Known...\n")
        db_Info = self.connection.get_server_info()
        path = "_idinfo/"
        files = glob.glob(path + "*.md")
        for filename in tqdm(files):
            params = []
            with open(filename, newline='') as myfile:
                title = str(int(filename[len(path) + 2: -5], 16))
                if title in unique:
                    continue
                unique.append(title)
                data = {}
                data['parameters'] = []
                for line in myfile:
                    if (line[0:13] == "description: "):
                        data['name'] = line[13:].strip()
                        data['description'] = line[13:].strip()
                    elif (line[0:7] == "* PGN: "):
                        data['pgn'] = int(line[7:].strip())
                    elif (line[0:19] == "* PDU Format (PF): "):
                        data['pdu_format'] = int(line[19:].strip(), 16)
                    elif (line[0:13] == "* Data Page: "):
                        data['data_length'] = len(line[13:].strip())
                    elif (line[0:12] == "* Priority: "):
                        data['default_priority'] = int(line[12:].strip())
                    elif (line[0:2] == "| " and line != "| Name | Size | Byte Offset |\n" and line != "| ---- | ---- | ----------- |\n"):
                        tokens = line[2:-3].split(" | ")
                        data['dp'] = 0
                        data['edp'] = 0
                        data['pdu_specific'] = 0
                        data['parameters'].append({'length': tokens[1], 'param_name': tokens[0], 'start_pos' : tokens[2]})
                
                records = ((self.username, data['pgn'], "5055E", data['name'], data['description'], 
                                data['pdu_format'], data['data_length'], data['default_priority']))
                
                for x in data['parameters']:
                    params.append((self.username, data['pgn'], x['start_pos'], "5055E", x['param_name'], x['length']))
       
            #Upload all of the data to database
            sql_insert_query = ("INSERT INTO `known` (`username`, `pgn`, `model`, `name`, `description`, "
                                +"`pdu_format`, `data_length`, `default_priority`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                                +"ON DUPLICATE KEY UPDATE `model` = %s, `name` = %s, `description` = %s, "
                                +"`pdu_format` = %s, `data_length` = %s, `default_priority` = %s")
            result = self.cursor.execute(sql_insert_query, (records + records[2:]))
           
            sql_insert_query2 = ("INSERT INTO `known_params` (`username`, `pgn`, `start_pos`, `model`, `param_name`, `length`) "
                                +"VALUES (%s, %s, %s, %s, %s, %s)"
                                +"ON DUPLICATE KEY UPDATE `param_name` = %s, `length` = %s")
            for x in params:
                self.cursor.execute(sql_insert_query2, (x + (x[4], x[5])))
            self.connection.commit()
            
        print("Uploaded " + str(len(unique)), "entries")
        for entry in unique:
            print("\t" + entry)

        print("\nPress Enter to continue...")
        input('');
        return

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
            except FileNotFoundError:
                print("Error. File not found.")
                continue
            self.clear_screen()
            print("Uploading Logs...\n")
        for line in end_messages:
            print(line)
        result  = self.cursor.executemany(sql_insert_query, records)
        self.connection.commit() 
        return

    def get_log(self, log):
        #columns=["time","pgn", "priority", "source", "destination", "data"]
        query = 'SELECT time, pgn, priority, source, destination, data FROM `5055E` WHERE `name` = "%s" ORDER BY `time`'
        df = pd.read_sql((query % log), con=self.connection)
       # print(df)
        return df
    
    def get_known(self):
        known = {}
        params = {}
        query = 'SELECT * FROM `known`'
        query2 = 'SELECT * from `known_params`'
        df = pd.read_sql(query, con=self.connection)
        df_params = pd.read_sql(query2, con=self.connection)
        for index, row in df.iterrows():
            known[row['pgn']] = Pgn(pgn=row['pgn'],
                                    data_len=row['data_length'],
                                    dflt_prty=row['default_priority'],
                                    name=row['name'],
                                    descr=row['description'],
                                    pdu_format=int(row['pdu_format']))
            params[row['pgn']] = []
        for index, row in df_params.iterrows():
            params[row['pgn']].append(PgnParameter(start_pos=row['start_pos'],
                                                   length=row['length'],
                                                   description=row['param_name']))
        for key,value in params.items():
            known[key].parameters = value
    
        return known

    def close(self):
        if(self.connection.is_connected()):
            self.cursor.close()
            self.connection.close()

def init_db(username, password):
    global database 
    database = db(username, password)
    return

def get_log(log, known):
    return database.get_log(log)
    
def close_db():
    database.close()

def import_logs():
    database.import_logs()

def import_known():
    database.import_known()

def export_known():
    input("Error this feature is still in development\nPress ENTER to continue...")

def get_lognames():
    return database.list_logs()
def get_known():
    database.get_known()
    return
