from polycan import db
from polycan.log import *
from tqdm import tqdm
import csv
import sys
import collections
import pandas as pd

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
        with open(path, newline='') as csvfile:
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
