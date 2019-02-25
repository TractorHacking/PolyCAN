from polycan import db
from polycan.log import *
from tqdm import tqdm
import csv
import sys
import collections
import pandas as pd

def get_log(log_name, known):
    log_document = db.collection(u'logs').document(log_name)
    collection_ref = log_document.collection('log')
    collection = collection_ref.get()
    model_name = log_document.get().to_dict()['model']
    list_of_dicts = [x.to_dict() for x in collection]
    res = pd.DataFrame(columns=['data', 'destination', 'pgn', 'priority', 'source', 'time', 'description'],data=list_of_dicts)
    res['description'] = ["Unknown" if not x in known else known[x] for x in res['pgn']]
    return res

def get_lognames():
    logs = db.collection(u'logs').get()
    log_names = []
    for log in logs:
        log_names.append(log.id)
    return log_names

def import_log():
    batch = db.batch()
    path = input("\nEnter file path: ")
    if len(path) <= 4:
        print("Error, Invalid File Name")
        return
    x = 0 
    try:
        with open("CANable/logs/"+path, newline='') as csvfile:
            log = csv.DictReader(csvfile)
            doc_ref = db.collection(u'logs').document(path[:-4]).collection('log')
            db.collection(u'logs').document(path[:-4]).set({u'model': '5055E'})
            print("\nUploading " + path[:-4] + "...") 
            for line in tqdm(log):
                line_ref = doc_ref.document(line['Time'])
                batch.set(line_ref,{ u'pgn': int(line['PGN'], 10),
                                     u'destination': int(line['DA'], 10),
                                     u'source': int(line['SA'], 10),
                                     u'priority': int(line['Priority'], 10),
                                     u'time': float(line['Time']),
                                     u'data': line['Data']
                                     })  
                x += 1
                if x % 500 == 0:
                    batch.commit()
            print("Uploaded", x-2, "lines.")
    except FileNotFoundError:
        print("Error. File not found.")
    return    

'''
def import_log():
    batch = db.batch()
    path = input("\nEnter file path: ")
    if len(path) <= 4:
        print("Error, Invalid File Name")
        return
    if path[-4:] != ".csv":
        print("Not a csv file")
        return
    x = 0 
    try:
        with open("CANable/logs/"+path, newline='') as csvfile:
            log = csv.DictReader(csvfile)
            filename = path.rpartition('/')
            doc_ref = db.collection(u'logs').document(filename[:-4]).collection('log')
            db.collection(u'logs').document(filename[:-4]).set({u'model': '5055E'})
            print("\nUploading " + filename + "...") 
            for line in tqdm(log):
                if(filename[:6] == "2018-01" or filename[:6] == "2018-02"):
                    line_ref = doc_ref.document(line['Time'])
                    batch.set(line_ref,{ u'pgn': int(line['ID'], 16),
                                     u'destination': 255,
                                     u'source': 255,
                                     u'priority': 255,
                                     u'time': float(line['Time']),
                                     u'data': line['Data']
                                     })  
                else:
                    line_ref = doc_ref.document(line['Time'])
                    batch.set(line_ref,{ u'pgn': int(line['Pgn'], 10),
                                     u'destination': int(line['DA'], 10),
                                     u'source': int(line['SA'], 10),
                                     u'priority': int(line['Priority'], 10),
                                     u'time': float(line['Time']),
                                     u'data': (line['Data']).strip()
                                     })  

                x += 1
                if x % 500 == 0:
                    batch.commit()
            print("Uploaded", x-2, "lines.")
    except FileNotFoundError:
        print("Error. File not found.")
    return    
'''
def get_known():
    known = {}
    collection_ref = db.collection(u'known_test')
    collection = db.collection(u'known_test').get()

    for doc in collection:
        doc_dict = doc.to_dict()
        pgn_object = Pgn.from_dict(doc_dict)

        params_list = []
        params = collection_ref.document(doc.id).collection(u'parameters').get()
        for param in params:
            param_dict = param.to_dict()
            params_list.append(PgnParameter.from_dict(param_dict))
        pgn_object.parameters = params_list
        known[pgn_object.pgn] = pgn_object
    return known



'''
from polycan import db
from polycan.log import *
from tqdm import tqdm
import csv
import sys
import collections
import pandas as pd
import glob


def import_known(path):
    x = 0
    batch = db.batch()
    unique = []
    for filename in tqdm(glob.glob(path+'*.md')):
        with open(filename, newline='') as myFile:
            pcount = 1
            title = str(int(filename[len(path) + 2:-5], 16))
            if title in unique:
                continue
            unique.append(title)
            data = {}
            docref = db.collection(u'known_test').document(title)
            for line in myFile:
                if (line[0:13] == "description: "):
                    data['name'] = line[13:].strip()
                    data['description'] = line[13:].strip()
                elif (line[0:7] == "* PGN: "):
                    data['pgn'] = int(line[7:].strip())
#                    print("PGN: " + line[7:].strip())
                elif (line[0:19] == "* PDU Format (PF): "):
                    data['pdu_format'] = int(line[19:].strip(), 16)
#                    print("PDU Format (PF):", int(line[19:].strip(), 16))
                elif (line[0:13] == "* Data Page: "):
                    data['data_length'] = len(line[13:].strip())
#                    print("Data Page:", len(line[13:].strip()))
                elif (line[0:12] == "* Priority: "):
                    data['default_priority'] = int(line[12:].strip())
#                    print("Priority: " + line[12:-1])
                elif (line[0:2] == "| " and line != "| Name | Size | Byte Offset |\n" and line != "| ---- | ---- | ----------- |\n"):
                    tokens = line[2:-3].split(" | ")
                    data['dp'] = 0
                    data['edp'] = 0
                    data['pdu_specific'] = 0
                    batch.set(docref, data)
                    batch.set(docref.collection(u'parameters').document(), {u'length' : tokens[1],
                                                                            u'param_name' : tokens[0],
                                                                            u'start_pos' : tokens[2].split('-')[0]})
                    x+=2
                if x % 500 == 0:
                    batch.commit()
 #           print("Uploaded" + filename)
    batch.commit()
    return    

def get_log(log_name):
    log_document = db.collection(u'logs').document(log_name)
    collection_ref = log_document.collection('log')
    collection = collection_ref.get()
    model_name = log_document.get().to_dict()['model']
    list_of_dicts = [x.to_dict() for x in collection]
    return pd.DataFrame(list_of_dicts)

def get_lognames():
    logs = db.collection(u'logs').get()
    log_names = []
    for log in logs:
        log_names.append(log.id)
    return log_names

def import_log():
    batch = db.batch()
    path = input("\nEnter file path: ")
    if len(path) <= 4:
        print("Error, Invalid File Name")
        return
    if path[-4:] != ".csv":
        print("Not a csv file")
        return
    x = 0 
    try:
        with open("CANable/logs/"+path, newline='') as csvfile:            log = csv.DictReader(csvfile)
            filename = path.rpartition('/')
            doc_ref = db.collection(u'logs').document(filename[:-4]).collection('log')
            db.collection(u'logs').document(filename[:-4]).set({u'model': '5055E'})
            print("\nUploading " + filename + "...") 
            for line in tqdm(log):
				if(filename[:6] == "2018-01" or filename[:6] == "2018-02"):
                    line_ref = doc_ref.document(line['Time'])
                    batch.set(line_ref,{ u'pgn': int(line['ID'], 16),
                                     u'destination': 255,
                                     u'source': 255,
                                     u'priority': 255,
                                     u'time': float(line['Time']),
                                     u'data': line['Data']                                     })  
                else:
                    line_ref = doc_ref.document(line['Time'])
                    batch.set(line_ref,{ u'pgn': int(line['Pgn'], 10),
                                     u'destination': int(line['DA'], 10),
                                     u'source': int(line['SA'], 10),
                                     u'priority': int(line['Priority'], 10),
                                     u'time': float(line['Time']),
                                     u'data': (line['Data']).strip()
                                     })  

                x += 1
                if x % 500 == 0:
                    batch.commit()
            print("Uploaded", x-2, "lines.")
    except FileNotFoundError:
        print("Error. File not found.")
    batch.commit()
    return    

def get_known():
    known = {}
    collection_ref = db.collection(u'known_test')
    collection = db.collection(u'known_test').get()

    for doc in collection:
        doc_dict = doc.to_dict()
        pgn_object = Pgn.from_dict(doc_dict)

        params_list = []
        params = collection_ref.document(doc.id).collection(u'parameters').order_by(u'start_pos').get()
        for param in params:
            param_dict = param.to_dict()
            params_list.append(PgnParameter.from_dict(param_dict))
        pgn_object.parameters = params_list
        known[pgn_object.pgn] = pgn_object
    return known
'''
