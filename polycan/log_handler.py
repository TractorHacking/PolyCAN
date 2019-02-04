from polycan.log import *
from polycan.firebase_interface import *
from tqdm import tqdm
from tabulate import tabulate
import numpy as np
import pandas as pd
import sklearn.model_selection as ms
from sklearn import neighbors
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import naive_bayes
import csv
import sys
import collections
def numerize_data(data):
    bytestring = data.replace(" ", '')
    return int(bytestring, 16)
def break_data(data):
    byte_list = data[1:-1].split(" ")
    for i in range(0, len(byte_list)):
        byte_list[i] = int(byte_list[i], 16)
    return byte_list

def param_values(data, length, params):
    values = {}
    byte_list = data[1:-1].split(" ")
    for i in range(0, length):
        byte_list[i] = int(byte_list[i], 16)
    byte_list.reverse()
    byte_list.insert(0, 0)
    # byte_list[8] - MSB, [1] - LSB
    for value in params:
        
        start_pos = value.start_pos
        field_len = int(value.length[:-1])
        param_name = value.description
        values[param_name] = 0

        boundaries = start_pos.split("-")
        start = []
        end = []
        if len(boundaries) == 1:
        #within the byte
            start = boundaries[0].split(".")
            if len(start) == 1:
            #whole byte
                values[param_name] = byte_list[int(start[0])]
            else:
            #fraction of byte
                values[param_name] = byte_list[int(start[0])] >> (int(start[1])-1)
                values[param_name] = values[param_name] & ~(255 << field_len)
        else:
        #across byte boundary
            start = boundaries[0].split(".")
            end = boundaries[1].split(".")

            #integer byte length: X-Y (> 1 byte)
            if len(boundaries[0]) == 1 and len(boundaries[1]) == 1:
                for i in range(int(start[0]), int(end[0])+1):
                    values[param_name] += (byte_list[i] << 8*(i-int(start[0])))

            #fractional byte across byte boundary: X.x - Y (> 1 byte)
            if len(boundaries[0]) > 1 and len(boundaries[1]) == 1:
                for i in range(int(start[0])+1, int(end[0])+1):
                    values[param_name] += (byte_list[i] << 8*(i-int(start[0])))

                values[param_name] = values[param_name] >> (int(start[1])-1)
                values[param_name] += (byte_list[int(start[0])] >> (int(start[1])-1))

            #fractional byte across byte boundary: X - Y.y (> 1 byte)
            if len(boundaries[0]) == 1 and len(boundaries[1]) > 1:
                for i in range(int(start[0]), int(end[0])):
                    values[param_name] += (byte_list[i] << 8*(i-int(start[0])))

                values[param_name] += ((byte_list[int(end[0])] >> (int(end[1])-1)) & \
                ~(255 << field_len % 8)) << (8*(int(end[0])-int(start[0])))

            #fractional byte across byte boundary: X.x - Y.y            
            if len(boundaries[0]) > 1 and len(boundaries[1]) > 1:
                remaining = field_len - (8-int(start[1])+1)
                values[param_name] = byte_list[int(start[0])] >> (int(start[1])-1)
                values[param_name] += ((byte_list[int(end[0])] >> (int(end[1])-1)) & \
                ~(255 << remaining)) << 8-int(start[1])+1
    return values

def detail_view(known, log=None):
    if log == None:
        get_pgn(known)
    else:
        while(1):
            choice = input("Please enter line number or q to quit: ")
            if choice == 'q':
                return
            try:
                option = int(choice)
            except:
                print("Invalid input")
                continue
            if option < 0 or option >= len(log):
                print("Number out of bounds")
                continue
            if not log['pgn'][option] in known:
                print("Unknown PGN {}".format(option))
                continue
            else:
                break
        get_pgn(known, log['pgn'][option], log['data'][option])
    return

def get_pgn(known, pgn = -1, data = ''):
    if pgn == -1:
        while(1):
            choice = input("Please enter PGN or q to quit: ")
            if choice == 'q':
                return
            try:
                pgn = int(choice)
            except:
                print("Invalid input")
                continue
            if not pgn in known:
                print("Unknown PGN")
                continue
            else: 
                break
    print_pgn(known[pgn], data)

def print_pgn(pgn_object, data):
    print('\n-----------------------------------------')
    print('{}'.format(pgn_object.pgn))
    print('{}'.format(pgn_object.description))
    print('\tData Length: {0:14d}'.format(pgn_object.data_length))
    print('\tExtended Data Page: {0:7d}'.format(pgn_object.edp))
    print('\tData Page: {0:16d}'.format(pgn_object.dp))
    print('\tPDU Format: {0:15d}'.format(pgn_object.pdu_format))
    print('\tPDU Specific: {0:13d}'.format(pgn_object.pdu_specific))
    print('\tDefault Priority: {0:9d}'.format(pgn_object.default_priority))

    if data != '':
        print('\tData: {0:21s}'.format(data))
    print('\nStart Position\tLength\tParameter Name\tSPN', end = '')

    if data != '':
        print('\tValue')
        pdata = param_values(data, pgn_object.data_length, pgn_object.parameters)
    else:
        print()

    for item in pgn_object.parameters:
        print("%-*s %-*s %s" % (15, item.start_pos, 7, item.length, item.description), \
        end = '')
        if data != '':
            print(10*' ' + "%d" % (pdata[item.description]), end='')
        print()

def find_log(uploaded_logs):
    names = get_lognames()
    if len(names) == 0:
        print("No logs found")
        return
    for i in range(0, len(names)):
        print("%d. %s" % (i, names[i]))
    while(1):
        option = 0
        choice = input("Please enter log number or q to quit: ") 
        if choice == 'q':
            return
        try:
           option = int(choice) 
        except:
            print("Invalid log number")
            continue
        if option < 0 or option >= len(names):
            print("Invalid log number")
            continue
        else:
            break
    if names[option] in uploaded_logs:
        return uploaded_logs[names[option]]
    log = get_log(names[option])
    uploaded_logs[names[option]] = log
    return log
    
def filter_menu(current_log, known):
    df = None
    while(1):
        print("Filter Menu\n")
        print("1. By PGN")
        print("2. By time")
        print("3. By Source")
        print("4. By Destination")
        print("5. Unique entries")
        print("6. Custom filter")
        print("7. Data Frequency")
        print("8. PGN Frequency")
        print("9. Return")
        choice = input("")
        try:
            option = int(choice)
        except:
            print("Please enter an integer for menu entry")
            continue
        if option == 1:
            try:
                pgn = int(input("Please enter PGN: "))
                df = current_log.query('pgn == {}'.format(pgn))
                print(current_log.query('pgn == {}'.format(pgn)))
            except:
                print("Must be an integer")
                continue
        elif option == 2:
            try:
                start = float(input("Start time: "))
                end = float(input("End time: "))
                df =current_log.query('time >= {} & time <= {}'.format(start, end))
                print(current_log.query('time >= {} & time <= {}'.format(start, end)))
            except:
                print("Invalid time")
                continue
        elif option == 3:
            try:
                source = int(input("Please enter source address: "))
                df = current_log.query('source == {}'.format(source))
                print(current_log.query('source == {}'.format(source)))
            except:
                print("Invalid source")
                continue
        elif option == 4:
            try:
                dest = int(input("Please enter destination address: "))
                df = current_log.query('destination == {}'.format(dest))
                print(current_log.query('destination == {}'.format(dest)))
            except:
                print("Invalid source")
                continue
        elif option == 5:
            print("Please enter unique columns (example: pgn,data,source,destination): ")
            columns = input("").split(",")
            df = current_log.drop_duplicates(columns)
            print(current_log.drop_duplicates(columns))
        elif option == 6:
            print("Please enter filters (example: pgn==331,time>=50.1,time<=50.5,src==52,dest==45): ")
            choice = input("")
            filters = choice.replace(",", "&")
            df = current_log.query(filters)
            print(current_log.query(filters))
            print("Unique? (example: pgn,data)")
            choice = input("")
            uniq_tags = choice.split(",")
            df = current_log.query(filters).drop_duplicates(uniq_tags)
            print(current_log.query(filters).drop_duplicates(uniq_tags))
        elif option == 7:
            sorted_by_pgn = current_log.sort_values(by='pgn')
            uniq_df = current_log.drop_duplicates(['pgn', 'data'])
            uniq_ddf = pd.DataFrame(uniq_df, columns=['pgn','data','frequency', 'count'])
            uniq_ddf['frequency'] = [np.mean(np.diff(arr)) if len(arr) > 1 \
                else 0 for arr in \
                    [np.array(sorted_by_pgn.query( \
                        ('pgn == {} & data == "{}"').format(y,z)) \
                .sort_values(by='time')['time']) \
                for y,z in zip(uniq_df['pgn'],uniq_df['data'])]]
            uniq_ddf['count'] = [len(sorted_by_pgn.query('pgn == {} & data == "{}"'.format(y,z))) \
                for y,z in zip(uniq_df['pgn'], uniq_df['data'])]
            print(uniq_ddf.to_string())
        elif option == 8:
            sorted_by_pgn = current_log.sort_values(by='pgn')
            uniq_df = current_log.drop_duplicates(['pgn'])
            uniq_ddf = pd.DataFrame(uniq_df, columns = ['pgn', 'frequency', 'count'])
            uniq_ddf['frequency'] = [np.mean(np.diff(arr)) if len(arr)>1 \
                else 0 for arr in \
                [np.array(sorted_by_pgn.query(('pgn == {}').format(y)) \
                .sort_values(by='time')['time']) \
                for y in uniq_df['pgn']]]
            uniq_ddf['count'] = [len(sorted_by_pgn.query('pgn == {}'.format(y))) for y in uniq_df['pgn']]
            print(uniq_ddf.to_string())
        elif option == 9:
            break
        else:
            print("Please enter an integer for menu entry")
            continue
def learn(current_log):
    #take only 8-byte data
    criterion = current_log['data'].map(lambda x: len(x) == 25)
    fixed = current_log[criterion]
    X = pd.DataFrame([numerize_data(x) for x in fixed.data])
    Y = pd.DataFrame(fixed.pgn)
    unique_pgns = len(current_log.drop_duplicates(['pgn']))

    #KNN classification
    XTrain, XTest, YTrain, YTest = ms.train_test_split(X,Y,test_size=0.3, random_state=7) 
    k_neigh = list(range(1,unique_pgns,2))
    n_grid = [{'n_neighbors':k_neigh}]
    model = neighbors.KNeighborsClassifier()
    cv_knn = GridSearchCV(estimator=model, param_grid = n_grid, cv=ms.KFold(n_splits=10))
    cv_knn.fit(XTrain, YTrain)
    best_k = cv_knn.best_params_['n_neighbors']
    knnclf = neighbors.KNeighborsClassifier(n_neighbors=best_k)
    knnclf.fit(XTrain, YTrain)
    y_pred = knnclf.predict(XTest)
    print("K Nearest Neighbors, best k = %d" % best_k)
    print(classification_report(YTest, y_pred))

    #Naive Bayes
    X = pd.DataFrame([break_data(x) for x in fixed.data])
    X_train, X_test, Y_train, Y_test = ms.train_test_split(X, Y, test_size=0.3, random_state=7)
    model = naive_bayes.MultinomialNB().fit(X_train, Y_train)
    confusion_matrix(Y_train, model.predict(X_train))
    y_pred = model.predict(X_test)
    pred_probs = model.predict_proba(X_test)
    print(pred_probs)
    print(confusion_matrix(Y_test, y_pred))
    print(classification_report(Y_test, y_pred))
    
    
    """
    print(np.array([numerize_data(x) for x in sorted_by_pgn['data']]))
    X = pd.DataFrame([numerize_data(x) for x in sorted_by_pgn['data']],
        columns=['1','2','3','4','5','6','7','8'])
    Y = pd.DataFrame([x for x in sorted_by_pgn['pgn']])
    print(X)
    print(Y)
    XTrain, XTest, YTrain, YTest = \
        ms.train_test_split(X.values, Y.values, test_size = 0.3, random_state = 7)
    k_neighbours = list(range(1, 250, 2))
    n_grid = [{'n_neighbors':k_neighbours}]
    model = neighbors.KNeighborsClassifier()
    cv_knn = GridSearchCV(estimator=model, \
        param_grid = n_grid, \
        cv = ms.KFold(n_splits=10))    
    cv_knn.fit(XTrain, YTrain)
    best_k = cv_knn.best_params_['n_neighbors']
    print("Best k = %d" % best_k)
    print("Best params:")
    print(cv_knn.best_params_)
    """
    
def log_menu(log, known):
    while(1):
        print("Log Menu")
        print("0. Display Log")
        print("1. Filter Log")
        print("2. Sort Log")
        print("3. Analyze single entry")
        print("4. Analyze PGN")
        print("5. Learn")
        print("6. Return")
        choice = input("")
        try:
            option = int(choice)
        except:
            print("Please enter an integer for menu entry")
            continue
        if option == 0:
            print(log)
        elif option == 1:
            filter_menu(log, known)
        elif option == 2:
            sort_menu(log, known)
        elif option == 3:
            detail_view(known,log)
        elif option == 4:
            analyze_menu(log, known)
        elif option == 5:
            learn(log)
        elif option == 6:
            return
        else:
            print("Please enter an integer for menu entry")
def compare_logs(uploaded_logs, known):
    pass
    """
    if len(uploaded_logs) < 2:
        print("Upload more logs")
        return
    name1 = input("Please enter first log name: ")
    name2 = input("Please enter second log name: ")
    log1_sorted_by_pgn = uploaded_logs[name1].sort_values[by='pgn']
    log2_sorted_by_pgn = uploaded_logs[name1].sort_values[by='pgn']
    pgn = int(input("Please enter PGN: "))
    num_entries = int(input("Please enter number of entries: "))
    df1 = log1_sorted_by_pgn.query('pgn == {}'.format(pgn)).head(num_entries)
    df2 = log1_sorted_by_pgn.query('pgn == {}'.format(pgn)).head(num_entries)
    """

def sort_menu(current_log, known):
    while(1):
        print("Sort Menu\n")
        print("1. By PGN")
        print("2. By time")
        print("3. By Source")
        print("4. By Destination")
        print("5. Return")
        choice = input("")
        try:
            option = int(choice)
        except:
            print("Please enter an integer for menu entry")
            continue
        if option == 1:
            print(current_log.sort_values(by='pgn'))
        elif option == 2:
            print(current_log.sort_values(by='time'))
        elif option == 3:
            print(current_log.sort_values(by='source'))
        elif option == 4:
            print(current_log.sort_values(by='destination'))
        elif option == 5:
            return
        else:
            print("Please enter an integer for menu entry")
            continue
