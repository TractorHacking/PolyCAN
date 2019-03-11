from polycan.menu import *
from polycan.log import *
from polycan.sql_interface import *
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
from scipy.cluster.hierarchy import linkage
from scipy.cluster.hierarchy import dendrogram
from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import cophenet
from operator import itemgetter
import csv
import sys
import matplotlib.pyplot as plt
import collections

def display_log(log):
    display_pages(log)
def numerize_data(data):
    bytestring = data.replace(" ", '')
    return int(bytestring, 16)
def break_data(data):
    byte_list = data.rstrip(' ')
    byte_list = data.lstrip(' ')
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
    print(byte_list)
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

def detail_view(known, log):
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
        if not log.at[option, 'pgn'] in known:
            print("Unknown PGN {}".format(log.at[option,'pgn']))
            continue
        else:
            break
    print_pgn(known[log.at[option, 'pgn']], log.at[option, 'data'])
    return

def get_pgn(known):
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
    print_pgn(known[pgn], '')

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
    input('Press enter to continue...')

def find_log():
    names = get_lognames()
    if len(names) == 0:
        return ''
    choice = launch_menu(names)
    return names[choice]
    
def filter_menu(current_log, known):
    df = None
    while(1):
        filter_options=["By PGN", "By Time", "By Source", "By Destination", "Unique entries", "Custom filter", "Data Frequency", "PGN Frequency", "Return"]
        option = launch_menu(filter_options)
        if option == 0:
            try:
                pgn = int(input("Please enter PGN: "))
                df = current_log.query('pgn == {}'.format(pgn))
                display_log(current_log.query('pgn == {}'.format(pgn)))
            except:
                print("Must be an integer")
                continue
        elif option == 1:
            try:
                start = float(input("Start time: "))
                end = float(input("End time: "))
                df =current_log.query('time >= {} & time <= {}'.format(start, end))
                display_log(current_log.query('time >= {} & time <= {}'.format(start, end)))
            except:
                print("Invalid time")
                continue
        elif option == 2:
            try:
                source = int(input("Please enter source address: "))
                df = current_log.query('source == {}'.format(source))
                display_log(current_log.query('source == {}'.format(source)))
            except:
                print("Invalid source")
                continue
        elif option == 3:
            try:
                dest = int(input("Please enter destination address: "))
                df = current_log.query('destination == {}'.format(dest))
                display_log(current_log.query('destination == {}'.format(dest)))
            except:
                print("Invalid source")
                continue
        elif option == 4:
            print("Please enter unique columns (example: pgn,data,source,destination): ")
            columns = input("").split(",")
            df = current_log.drop_duplicates(columns)
            display_log(current_log.drop_duplicates(columns))
        elif option == 5:
            print("Please enter filters (example: pgn==331,time>=50.1,time<=50.5,src==52,dest==45): ")
            choice = input("")
            filters = choice.replace(",", "&")
            print("Unique? (example: pgn,data)")
            uniq_choice = input("")
            uniq_tags = choice.split(",")
            if(uniq_tags == []):
                df = current_log.query(filters)
                display_log(current_log.query(filters))
            else:
                df = current_log.query(filters).drop_duplicates(uniq_tags)
                display_log(current_log.query(filters).drop_duplicates(uniq_tags))
        elif option == 6:
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
            display_log(uniq_ddf.to_string())
        elif option == 7:
            sorted_by_pgn = current_log.sort_values(by='pgn')
            uniq_df = current_log.drop_duplicates(['pgn'])
            uniq_ddf = pd.DataFrame(uniq_df, columns = ['pgn', 'frequency', 'count'])
            uniq_ddf['frequency'] = [np.mean(np.diff(arr)) if len(arr)>1 \
                else 0 for arr in \
                [np.array(sorted_by_pgn.query(('pgn == {}').format(y)) \
                .sort_values(by='time')['time']) \
                for y in uniq_df['pgn']]]
            uniq_ddf['count'] = [len(sorted_by_pgn.query('pgn == {}'.format(y))) for y in uniq_df['pgn']]
            display_log(uniq_ddf.to_string())
        elif option == 8:
            return
        else:
            print("Please enter an integer for menu entry")
            continue
        input('Press enter to continue...')
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
    
    #Hierarchy clustering
    X = pd.DataFrame([numerize_data(x) for x in fixed.data])
    X_dist = pdist(X)
    X_link = linkage(X, method='ward')
    coph_cor, coph_dist = cophenet(X_link, X_dist)
    print(coph_cor)
    dendrogram(X_link, truncate_mode='lastp', p=15, show_contracted=True)
    plt.show()
         
def log_menu(log, known):
    while(1):
        options = ["Display Log", "Filter Log", "Sort Log", "Analyze single entry", "Analyze PGN", "Learn", "Pattern Matching", "Plot PGN", "Return"]
        option = launch_menu(options)
        if option == 0:
            display_log(log)
        elif option == 1:
            filter_menu(log, known)
        elif option == 2:
            sort_menu(log, known)
        elif option == 3:
            detail_view(known,log)
        elif option == 4:
            get_pgn(known)
        elif option == 5:
            learn(log)
        elif option == 6:
            log2_name = find_log()
            log2 = get_log(log2_name, [])
            find_patterns(log, log2)
        elif option == 7:
            plot_pgn(log)
        elif option == 8:
            return

def plot_pgn(log):
    pgn = int(input("Please enter PGN to plot: "))
    time_axis = log.query('pgn == {}'.format(pgn))['time'].as_matrix()
    data_axis = log.query('pgn == {}'.format(pgn))['data'].as_matrix()
    num_data = np.array([numerize_data(x) for x in data_axis])
    plt.plot(time_axis, num_data)
    plt.show()

def find_patterns(log1, log2):
    """
    cols = ['pgn1','data1','pgn2','data2','diff']
    df = pd.DataFrame(data={'pgn1': log1['pgn'],
                        'data1':log1['data'],
                        'pgn2':log2['pgn'],
                        'data2':log2['data']},
                        columns = cols)
    df['diff'] = df['data1'] == df['data2']
    df.dropna(how = 'all')
    print(df)
    #df['pgn2'] = log2['pgn']
    #df['data2'] = log2['data']
    #df['diff'] = df['data'] == df['data2']
    """
    count = 0
    patterns = []
    save_i = 0
    max_patern_length = 0
    min_size = min(len(log1), len(log2))
    log1=log1.truncate(after=min_size-1)
    log2=log2.truncate(after=min_size-1)

    uniq_idx_log1 = log1.drop_duplicates(['pgn', 'data']).index
    for i in uniq_idx_log1:
        queried = log2.query('pgn == {} & data == "{}"'.format(
            log1.loc[i, 'pgn'],
            log1.loc[i, 'data']))
        if(len(queried) == 0):
            continue
        save_i = i
        for j in queried.index:
            k = j
            #print("i: {} k: {}".format(i,k))
            while(k < min_size and i < min_size and
                log2.loc[k, 'pgn'] == log1.loc[i, 'pgn'] and
                log2.loc[k, 'data'] == log1.loc[i, 'data']):
                k += 1
                i += 1
                count += 1
            if count > 1:
                patterns.append(log2[save_i:i])
            i = save_i
            count = 0

    for l in range(0, len(patterns)):
        print('Pattern #{}'.format(l+1))
        print('Item count = {}'.format(len(patterns[l])))
        print(patterns[l])

    input('Press enter to continue...')

def KMP_logs(pattern, log2):
    X = 0
    ret = [0] * len(pattern)
    for j in range(1,len(pattern)):
        if pattern.iat[j,0] ==  pattern.iat[X,0] and \
            pattern.iat[j,1] == pattern.iat[X,1]:
            ret[j] = ret[X]
            X += 1
        else:
            ret[j] = X
            X = ret[X]
    i = 0
    j = 0
    print(ret)
    while(i < len(log2)):
        if j == len(pattern):
            print("Found pattern:")
            print(log2.iloc[i-len(pattern):i])
            j = ret[j-1]
        elif pattern.iat[j,0] ==  log2.iat[i,0] and \
            pattern.iat[j,1] == log2.iat[i,1]:
            i += 1
            j += 1
        else:
            if j != 0:
                j = ret[j]
            i += 1

def compare_logs(log1, log2):
    print(log1)
    pattern = input("Please choose a pattern to search in log2 (ex. 1-52): ")
    ptrn = log1[['pgn','data','time']].iloc[int(pattern.split("-")[0]):int(pattern.split("-")[1])+1]
    txt = log2[['pgn','data','time']]
    print(ptrn)
    KMP_logs(ptrn ,txt) 
    pass

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
            
#@des creates a list with entries from a choosen logfile, generated from the result of comparing entry by entry of two logs. If entry is not in both logs, it looks for the lowest amount of different bytes for the data and adds the amount and index of the different bytes to the entry of the new list, (eg. xxx98xxxt6xxx4xx). After comparison is done, you can delete identical codes in the new list, sort the list by pgn letter or compare that list to an other logfile
#@param {dataframe} uploaded_logs Stored logfiles in database
#@param {int} known Stored known pgns in database
#@param {string/list} table Within first use string to define first use, after recall of function list
#@required itemgetter
def compare_logs(uploaded_logs, known, table):
    bol = False
    if(table != "ok"):
        input("\n --selecting log to compare with--")
        log2_Name = find_log()
        if log2_Name in uploaded_logs:
            log2 = uploaded_logs[log2_Name]
        else:
            log2 = get_log(log2_Name, known)
            uploaded_logs[log2_Name] = log2
        log2 = log2.values.tolist()
        print("\n --log selected, comparing...--")
        log1 = table
        bol = True
    else:
        input("\n --selecting first log--")
        log1_Name = find_log()
        if log1_Name in uploaded_logs:
            log1 = uploaded_logs[log1_Name]
        else:
            log1 = get_log(log1_Name, known)
            uploaded_logs[log1_Name] = log1
        log1 = log1.values.tolist()
        input("\n --selecting second log--")
        log2_Name = find_log()
        if log2_Name in uploaded_logs:
            log2 = uploaded_logs[log2_Name]
        else:
            log2 = get_log(log2_Name, known)
            uploaded_logs[log2_Name] = log2
        log2 = log2.values.tolist()
        print("\n --logs selected, comparing...--")
        bol = False
    table = []
    breakCount = 0;
    diffCount = 0;
    pgnCount = 0
    dataCount = 0
    shortData = 0
    len1 = len(log1)
    len2 = len(log2) - 1
    printProgressBar(0, len1, prefix = 'Progress:', suffix = 'Complete', length = 50)
    for idx1, val1 in enumerate(log1):
        pgnBool = False
        dataBool = False;
        printProgressBar(idx1 + 1, len1, prefix = 'Progress:', suffix = 'Complete', length = 50)
        if bol:
            pgnStr1 = val1[0]
            dataStr1 = val1[1]
        else:
            if val1[1] in known.keys():
                pgnName = known[val1[1]].name
            else:
                pgnName = "Unknown"
            dataStr1 = ''.join(val1[5].split())
            pgnStr1 = str(val1[1])
        pgnData1 = pgnStr1 + dataStr1
        if len(dataStr1) < 16:
            shortData += 1
        dataDiffShort = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
        for idx2, val2 in enumerate(log2):
            dataDiffOld = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
            dataDiff = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
            dataStr2 = ''.join(val2[5].split())
            pgnStr2 = str(val2[1])
            pgnData2 = pgnStr2 + dataStr2
            if pgnStr1 == pgnStr2:
                pgnBool = True
                idxCount = 0
                if len(dataStr1) == 16 and len(dataStr2) == 16:
                    for idxChar in dataDiff:
                        char1 = dataStr1[idxChar]
                        char2 = dataStr2[idxChar]
                        if char1 == char2:
                            del dataDiffOld[idxCount]
                            idxCount -= 1
                        idxCount += 1
                    if len(dataDiffOld) < len(dataDiffShort):
                        dataDiffShort = dataDiffOld
            if dataStr1 == dataStr2:
                dataBool = True
            if pgnData1 == pgnData2:
                breakCount += 1
                break
            elif idx2 == len2:
                diffCount += 1
                dataDiffAmount = len(dataDiffShort)
                xCode = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]
                if len(dataStr1) == 16:
                    for idx5, val5 in enumerate(dataStr1):
                        for idx6, val6 in enumerate(dataDiffShort):
                            if val6 == idx5:
                                xCode[idx5] = val5
                                break
                            else:
                                xCode[idx5] = 'x'
                    xCode = ''.join(xCode)
                if bol:
                    table_entry = [log1[idx1][0], log1[idx1][1], log1[idx1][2], log1[idx1][3], log1[idx1][4], log1[idx1][5], dataDiffAmount, xCode]
                else:
                    table_entry = [pgnStr1, dataStr1, dataDiffAmount, dataDiffShort, pgnName, xCode]
                table.append(table_entry)
                if not pgnBool:
                    pgnCount += 1
                if not dataBool:
                    dataCount += 1 
                    
    printTable(table)
    printCodeResults(len1, breakCount, diffCount, pgnCount, dataCount, shortData, 0)
    input('Press enter to continue...')

    while(1):
        options = ["Delete identical data codes", "Sort list", "Compare to an other log", "Done comparing logs"]
        choice = launch_menu(options)
        if choice == 0:
            delSame(table, len1, breakCount, diffCount, pgnCount, dataCount, shortData)
            input('Press enter to continue...')
        elif choice == 1:
            table = sorted(table, key=itemgetter(4))
            printTable(table)
            input('Press enter to continue...')
        elif choice == 2:
            return compare_logs(uploaded_logs, known, table)
        else:
            return
            
#@des deletes identical codes in newly created list by compare_logs function above
#@param {list} table list of all entries which are found in on log but not in the other
#@param {int} len1 number of entries of log1
#@param {int} breakCount number of entries found in log1 and log2
#@param {int} diffCount number of entries found in log1 but not in log2
#@param {int} pgnCount number of unique pngs found in log1
#@param {int} dataCount number of data entries found in log1 but not in log2
#@param {int} shortData number of data entries with less 16

def delSame(table, len1, breakCount, diffCount, pgnCount, dataCount, shortData):
    table2 = []
    len3 = len(table)
    printProgressBar(0, len3, prefix = 'Progress:', suffix = 'Complete', length = 50)
    for idx3, val3 in enumerate(table):
        data1 = val3[1]
        idx4 = 0
        len4 = len(table)
        printProgressBar(idx3 + 1, len4, prefix = 'Progress:', suffix = 'Complete', length = 50)
        while idx4 < len4:
            data2 = table[idx4][1]
            if data1 == data2:
                if idx4 > idx3:
                    del table[idx4]
                    len4 = len(table)
                    idx4 += 0
                    continue
            idx4 += 1
                        
                    
    printTable(table)
    
    printCodeResults(len1, breakCount, diffCount, pgnCount, dataCount, shortData, table)
    len5 = len(table) - 1
    
    
#@des prints newly created list by compare_logs function above
#@param {list} table list of all entries which are found in on log but not in the other    
def printTable(table):
    print(tabulate(table,
            headers= ["index", "pgn","data", "amount diff bytes", "index diff bytes", "pgn Name", "data x", "amount diff bytes", "data x", "amount diff bytes", "data x"], \
                      showindex = True,
                     # tablefmt = "pipe"
                      ))

#@des prints results from comparision by compare_logs function above
#@param {int} len1 number of entries of log1
#@param {int} breakCount number of entries found in log1 and log2
#@param {int} diffCount number of entries found in log1 but not in log2
#@param {int} pgnCount number of unique pngs found in log1
#@param {int} dataCount number of data entries found in log1 but not in log2
#@param {int} shortData number of data entries with less 16    
#@param {list} table list of all entries which are found in on log but not in the other
def printCodeResults(len1, breakCount, diffCount, pgnCount, dataCount, shortData, table):
    print("Total codes") 
    print(len1)
    print("Total matches")
    print(breakCount)
    print("Total differences")
    print(diffCount)
    print("Total pgn differences")
    print(pgnCount)
    print("Total data differences")
    print(dataCount)
    print("Short Data")
    print(shortData)
    if(table != 0):
        print("Unique codes")
        print(len(table))
    
#@des Call in a loop to create terminal progress bar
#@param {int} iteration corrent iteration
#@param {int} total total iterations
#@param {string} prefix prefix string
#@param {string} suffix suffix string
#@param {int} decimals positive number of decimals in percent complete
#@param {int} length character length of bar
#@param {string} fill bar fill character
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total: 
        print()
        
#@des able to change data bytes in logfile and store it so it can be send to tractor
#@param {dataframe} uploaded_logs Stored logfiles in database
def manipulate_logs(known):
    print("\n --select log which you want to clone and manipulate--")
    log_Name = find_log()
    log = get_log(log_Name, known)
    log = log.values.tolist()
    print("choose pgn you want to manipulate (eg: 61444 for RPM)")
    choosenPgn = input('')
    for i in range(0, 10):
        if(len(choosenPgn) == 5):
            break
        else:
            print("Pgn must contain 5 digits long. Insert pgn")
            choosenPgn = input('')
    choosenPgn = int(choosenPgn)
    pgnIndexArray = []
    for idx, val in enumerate(log):
        if(val[1] == choosenPgn):
            pgnIndexArray.append(idx)
    arrayLen = len(pgnIndexArray)
    print(str(arrayLen) + " pgn matches")
    if(arrayLen == 0):
        return
    print("from index " + str(pgnIndexArray[0]) + " to index " + str(pgnIndexArray[arrayLen - 1]))
    print("In how many sectors do you want to split log:")
    sectorAmount = input('')
    sectorAmount = int(sectorAmount)
    sectorArray = []
    for x in range(sectorAmount):
        print("Choose sector  " + str(x + 1) + " index start:")
        sectorStart = input('')
        sectorStart = int(sectorStart)
        print("Choose sector " + str(x + 1) + " index end:")
        sectorEnd = input('')
        sectorEnd = int(sectorEnd)
        sectors = [sectorStart, sectorEnd]
        sectorArray.append(sectors)
    for y in range(len(sectorArray)):
        for z in range(len(sectorArray[y])):
            closest = min(pgnIndexArray, key=lambda x:abs(x-sectorArray[y][z]))
            index = pgnIndexArray.index(closest)
            sectorArray[y][z] = index
    digitRangeArray = []
    print("choose digits range start in data you want to change (eg. RPM = 6-9 so type 6)")
    digitStart = input('')
    digitStart = int(digitStart)
    digitRangeArray.append(digitStart)
    print("choose digits range end in data you want to change (eg. RPM = 6-9, so type 9)")
    digitEnd = input('')
    digitEnd = int(digitEnd)
    digitRangeArray.append(digitEnd)
    valueArray = []
    for h in range(sectorAmount):
        print("choose value you want to replace sector " + str(h + 1) + " with: (eg: 1000rpm = 401F, 2000rpm = 803E, 3000rpm = C05D)")
        value = input('')
        value = str(value)
        value = list(value)
        valueArray.append(value)
    for u in range(len(sectorArray)):
        for k in range(sectorArray[u][0], sectorArray[u][1]+1):
            log[pgnIndexArray[k]][5] = list(''.join(log[pgnIndexArray[k]][5].split()))
            #for idx1, val1 in enumerate(digitRangeArray):
            wHelp = 0
            for w in range(digitRangeArray[0], digitRangeArray[1]+1):
                log[pgnIndexArray[k]][5][w] = valueArray[u][wHelp]
                wHelp += 1
            log[pgnIndexArray[k]][5] = ''.join(log[pgnIndexArray[k]][5])
            log[pgnIndexArray[k]][5] = ' '.join([log[pgnIndexArray[k]][5][s:s+2] for s in range(0, len(log[pgnIndexArray[k]][5]), 2)])
    manipulatedLog = []
    for q in range(len(log)):
        mylist = log[q]
        myorder = [0, 1, 4, 3, 2, 5]
        mylist = [mylist[i] for i in myorder]
        manipulatedLog.append(mylist)
    for r in range(len(manipulatedLog)):
        print(manipulatedLog[r])
    print("Name log (eg. manipulatedLog.csv)")
    logName = input('')
    csvfile = logName
    with open(csvfile, "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerows(manipulatedLog)
    print("your log has been stored with name " + logName)
        
