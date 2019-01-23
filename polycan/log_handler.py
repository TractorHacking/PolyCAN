from polycan.log import *
from polycan.firebase_interface import *
from tqdm import tqdm
from tabulate import tabulate
import csv
import sys
import collections

def param_values(data, length, params):
    values = {}
    byte_list = data[1:-1].split(" ")
    for i in range(0, length):
        byte_list[i] = int(byte_list[i], 16)
    byte_list.reverse()
    byte_list.insert(0, 0)
    # byte_list[8] - MSB, [1] - LSB
    for value in params:
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
            if not option in known:
                print("Unknown PGN")
                continue
            else:
                break
        get_pgn(known, log[option].pgn, log[option].data)
    return

def get_pgn(known, pgn = '', data = ''):
    if pgn == '':
        while(1):
            choice = input("Please enter PGN or q to quit: ")
            if choice == 'q':
                return
            try:
                option = int(choice)
            except:
                print("Invalid input")
                continue
            if not option in known:
                print("Unknown PGN")
                continue
            else: 
                break
    print_pgn(known[option], data)

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
        pdata = param_values(data, pgn_object.data_length, params)
    else:
        print()

    for item in pgn_object.parameters:
        print("%-*s %-*s %s" % (15, item['start_pos'], 7, item['length'], item['param_name']), \
        end = '')
        if data != '':
            print(10*' ' + "%d" % (pdata[item['param_name']]), end='')
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
    for x in uploaded_logs:
        if x.name == names[option]:
            return x
    log = get_log(names[option])
    uploaded_logs.append(log)
    return log

def filter_by_pgn(current_log):
    choice = input("Please enter PGN: ")
    try:
        option = int(choice)
    except:
        print("Please enter an integer")
        return filter_by_pgn(current_log, known)
    current_log.filter_log(lambda x: x.pgn == option)
    return

def filter_by_time(current_log):
    starttime = 0.0
    endtime = 0.0
    try:
        starttime = float(input("Start time: "))
        endtime = float(input("End time: "))
    except:
        print("Please enter valid time")
        return filter_by_time(current_log)
    current_log.filter_log(lambda x: x.time >= starttime and x.time <= endtime)
    return

def filter_by_src(current_log):
    choice = input("Please enter source address: ")
    try:
        option = int(choice)
    except:
        print("Please enter an integer")
        return filter_by_src(current_log)
 
    current_log.filter_log(lambda x: x.src == option)
    return

def filter_by_dest(current_log):
    choice = input("Please enter destination address: ")
    try:
        option = int(choice)
    except:
        print("Please enter an integer")
        return filter_by_dest(current_log)
 
    current_log.filter_log(lambda x: x.dest == option)
    return

def filter_menu(current_log, known):
    while(1):
        print("Filter Menu\n")
        print("1. By PGN")
        print("2. By time")
        print("3. By Source")
        print("4. By Destination")
        print("5. Remove filters")
        print("6. Return")
        choice = input("")
        try:
            option = int(choice)
        except:
            print("Please enter an integer for menu entry")
            continue
        if option == 1:
            filter_by_pgn(current_log)
        elif option == 2:
            filter_by_time(current_log)
        elif option == 3:
            filter_by_src(current_log)
        elif option == 4:
            filter_by_dest(current_log)
        elif option == 5:
            current_log.remove_filters()
        elif option == 6:
            break
        else:
            print("Please enter an integer for menu entry")
            continue

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
            current_log.sort(lambda x: x.pgn)
        elif option == 2:
            current_log.sort(lambda x: x.time)
        elif option == 3:
            current_log.sort(lambda x: x.src)
        elif option == 4:
            current_log.sort(lambda x: x.dest)
        elif option == 5:
            return
        else:
            print("Please enter an integer for menu entry")
            continue
