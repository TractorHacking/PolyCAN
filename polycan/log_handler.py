from polycan import db, input_prompt
from tqdm import tqdm
from tabulate import tabulate
import csv
import sys
import collections

known = {}
current_data = [] 
current_log = ""

def rshift(val, n): return val>>n if val >= 0 else (val+0x100000000)>>n

# To Do: Find the mean and variance of dT for a given pgn
def get_statistics(pgn, log):
    pass
#    return {"mean": mean, "variance": variance}

# To Do: Add a detail view for known packets
def param_values(data, length, params):
    values = {}
    byte_list = data[1:-1].split(" ")
    for i in range(0, length):
        byte_list[i] = int(byte_list[i], 16)
    byte_list.reverse()
    byte_list.insert(0, 0)
    # byte_list[8] - MSB, [1] - LSB
    for key,value in params.items():
        start_pos = value['start_pos']
        field_len = int(value['length'][:-1])
        param_name = value['param_name']

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

def detail_view(line = -1):
    if line == -1:
        get_pgn()
    else:
        if line > len(current_data)-1:
            print("Number out of bounds")
            return
        get_pgn(current_data[line][1], current_data[line][6])
    return

def get_pgn(pgn = '', data = ''):
    if pgn == '':
        pgn = input("\nPlease enter PGN or 'q' to return to the log menu: ")
        if pgn == 'q':
            print('\n')
            return
    if int(pgn) in known:
        print_pgn(int(pgn), data)
    else:
        print('\nError: unknown PGN \'{}\'. Please try again.\n'.format(pgn))

def print_pgn(pgn, data):
    record = known[pgn]
    info = record[0]
    params = record[1]
    print('\n-----------------------------------------')
    print('{}'.format(info['pgn']))
    print('{}'.format(info['description']))
    print('\tData Length: {0:14d}'.format(info['data_length']))
    print('\tExtended Data Page: {0:7d}'.format(info['edp']))
    print('\tData Page: {0:16d}'.format(info['dp']))
    print('\tPDU Format: {0:15d}'.format(info['pdu_format']))
    print('\tPDU Specific: {0:13d}'.format(info['pdu_specific']))
    print('\tDefault Priority: {0:9d}'.format(info['default_priority']))
    if data != '':
        print('\tData: {0:21s}'.format(data))
    print('\nStart Position\tLength\tParameter Name\tSPN', end = '')

    if data != '':
        print('\tValue')
        pdata = param_values(data, int(info['data_length']), params)
    else:
        print()

    for key,value in params.items():
        print("%-*s %-*s %s" % (15, value['start_pos'], 7, value['length'], value['param_name']), \
        end = '')
        if data != '':
            print(10*' ' + "%d" % (pdata[value['param_name']]), end='')
        print()

def param_values(data, length, params):
    values = {}
    byte_list = data.split(" ")
    for i in range(0, length):
        byte_list[i] = int(byte_list[i])

    # byte_list[0] - MSB
    for parameter in params:
        start_pos = parameter['start_pos']
        field_len = int(parameter['length'][:-1])
        param_name = parameter['param_name']

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
                values[param_name] = byte_list[int(start[0])] >> int(start[1]) 
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
                    values[param_name] += (byte_list[i] << 8*(i-int(start[0])-1))

                values[param_name] = (values[param_name] << (8-int(start[1])+1)) + \
                (byte_list[int(start[0])] >> (int(start[1])-1))

            #fractional byte across byte boundary: X - Y.y (> 1 byte)
            if len(boundaries[0]) == 1 and len(boundaries[1]) > 1:
                for i in range(int(start[0]), int(end[0])):
                    values[param_name] += (byte_list[i] << 8*(i-int(start[0])))

                values[param_name] += ((byte_list[int(end[0])] >> (int(end[1])-1)) & \
                ~(255 << field_len % 8))

            #fractional byte across byte boundary: X.x - Y.y            
            if len(boundaries[0]) > 1 and len(boundaries[1]) > 1:
                values[param_name] = byte_list[int(start[0])] >> (int(start[1])-1)
                values[param_name] += ((byte_list[int(end[0])] >> (int(end[1])-1)) & \
                ~(255 << field_len-(8-int(start[1])+1))) << (field_len - (8-int(start[1])+1))
    return values

# This function gets the name of all logs in database
# It prompts the user to select one and returns the chosen name 
def prompt_log():
    while(1):
        logs = db.collection(u'logs').get()
        x = 1
        log_names = []

        print("\n0. Main Menu")
        for log in logs:
            log_names.append(log.id)
            print("{num}. {name}".format(num=x, name=log.id))
            x+=1
        if len(log_names) == 0:
            print("No logs found. Press 3 to import a log file.")
            return main_menu()
        print("")
        choice = int(input(input_prompt))
        if (choice == 0):
            return
        elif (choice > 0 and choice <= len(log_names)):
            return log_names[choice-1]
        else:
            print("Error. Enter an integer between 0 and " + str(x-1))        

#This function takes the name of the log to be filtered and allows the user to select filter options
#It queries the database with the filter configuration and displays the filtered list using show_log
def filter_log(filter, term):
    switch_log(log_name = current_log, filter = filter, filter_arg = term)
    return

'''
#This function gets known packet data and tags all the packets in the log
#It then tabulates the data and displays to the user
#This function then allows the user to choose analysis options
def show_log(docs, name):
    current_log = name
    print("using show log\n")
    current_data = process_log(docs, name)
    print_log(current_data, name)
    log_menu(current_data, name)
    return
    
#Takes log name and returns dictionaries with all information, including description
def process_log(docs, name):
    k = db.collection(u'known').get()
    known = {}
    for entry in k:
        e = entry.to_dict()
        known[int(e['pgn'])] = e['description']
    data = []
    x = 1
    for doc in docs:
        d = doc.to_dict()
        dlist = [d['time'], d['pgn'], d['priority'], d['source'], d['destination']]
        if d['pgn'] in known:
            dlist.append(known[d['pgn']])
        else:
            dlist.append("Unknown")
        dlist.append(d['data'])
        # Add packet to data
        data.append(dlist)
    return data
'''
#Takes data as dictionary and prints using tabulate
def print_log(data):
    #Print all data using tabluate
    print("")
    print(tabulate(data, headers=["time","pgn", "prty", "src", "dest", "description", "data" ], showindex = True, tablefmt = "pipe"))
    print("")


# This function downloads a log from database and returns a list
def get_log(log_name, sort, filter_field = '', filter_data = ''):
    if (filter_field != 'none' and filter_data != ''):
        print('filtering by ' + filter_field + ' with arg ' + filter_data)
        log_ref = db.collection(u'logs').document(log_name).collection(u'log').where(filter_field, '==', int(filter_data)).order_by(sort).get()
    else:
        log_ref = db.collection(u'logs').document(log_name).collection(u'log').order_by(sort).get()
    data = []
    for doc in log_ref:
        d = doc.to_dict()
        dlist = [d['time'], d['pgn'], d['priority'], d['source'], d['destination']]
        if d['pgn'] in known:
            dlist.append(known[d['pgn']][0]['name'])
        else:
            dlist.append("Unknown")
        if len(d['data']) > 30:
            dlist.append(d['data'][:24] + "...")
        else: dlist.append(d['data'])
        # Add packet to data
        data.append(dlist)
    return data

# This function is responsible for displaying logs, it calls many subfunctions
def switch_log(log_name = '', data = '', filter = 'none', filter_arg = '', sort = 'time'):
    global current_log, current_data
    # Prompt user and get the name of desired log
    if log_name == '':
        log_name = prompt_log()

    # Get the data for that log
    if data == '':
        data = get_log(log_name, sort, filter, filter_arg)

    # If we are filtering by log
    if filter == 'mask': 
        mask_data = get_log(mask_name, sort)
        #TODO: Masking Algorithm
        pass

    # Store reference to current log
    current_log = log_name
    current_data = data
    # Display the log data
    print_log(data)
    
    return

    '''
    if (log_name in log_cache):
        print("log " + log_name + " is cached!")
    else:
        print("log " + log_name + " is not cached!")
        if (len(log_cache) > 3):
            log_cache.remove()
        log_cache.append(log_name
                   
   
   '''
# Populate list of known   
def get_known():
    collection_ref = db.collection(u'known')
    collection = db.collection(u'known').get()
    for pgn in collection:
        params_dict = {}
        params = collection_ref.document(pgn.id).collection(u'parameters').get()
        for param in params:
            params_dict[param.id] = param.to_dict()
        known[int(pgn.id)] = [pgn.to_dict(), params_dict]

#This function allows the user to add a csv log to the database
def import_log():
    batch = db.batch()
    path = input("\nEnter file path: ")
    if len(path) <= 4:
        print("Error, Invalid File Name")
        return
    x = 0
    try:
        with open("logs/"+path, newline='') as csvfile:
            log = csv.DictReader(csvfile)
            doc_ref = db.collection(u'logs').document(path[:-4]).collection('log')
            db.collection(u'logs').document(path[:-4]).set({u'model': '5055E'})
            print("\nUploading " + path[:-4] + "...") 
            for line in tqdm(log):
                line_ref = doc_ref.document(line['time'])
                batch.set(line_ref,{ u'pgn': int(line['pgn'], 16),
                                     u'destination': int(line['destination'], 16),
                                     u'source': int(line['source'], 16),
                                     u'priority': int(line['source'], 16),
                                     u'time': float(line['time']),
                                     u'data': line['data']
                                     })
                x += 1
                if x % 500 == 0:
                    batch.commit()
            print("Uploaded", x-2, "lines.")
    except FileNotFoundError:
        print("Error. File not found.")
    
    return

known = get_known() 
