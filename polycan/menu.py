import polycan.keyreader as kr
import subprocess as sp
import sys, os
import termios, fcntl
import select


splash = ("   ___       __     ________   _  __\n"
         +"  / _ \___  / /_ __/ ___/ _ | / |/ /\n"
         +" / ___/ _ \/ / // / /__/ __ |/    / \n"
         +"/_/   \___/_/\_, /\___/_/ |_/_/|_/  \n"
         +"            /___/                   \n")
down = chr(27) + chr(91) + chr(66)
up = chr(27) + chr(91) + chr(65)
enter = chr(10)


def clear_screen():
    sp.call('clear',shell=True)
    print(splash)
    return

def launch_menu(options):
    line_select = 0
    line_max = len(options)-1
    keyreader = kr.KeyReader()
    while(1):
        clear_screen()
        for i in range(0, line_max+1):
            if (i == line_select):
                print("> " + options[i])
            else:
                print("  " + options[i])
        inp, outp, err = select.select([sys.stdin], [], [])
        entry = keyreader.getch()
        if (entry == down):
            if (line_select < line_max):
                line_select = line_select+1
            else:
                line_select = 0
        elif (entry == up):
            if (line_select > 0):
                line_select = line_select-1
            else:
                line_select = line_max
        elif (entry == chr(10)):
            return line_select

'''
def launch_advanced_menu(options, suboptions):
    line_select = 0
    enter_menu = False
    line_max = len(options)-1
    keyreader = kr.KeyReader()
    while(1):
        clear_screen()
        for i in range(0, line_max+1):
            if (i == line_select):
                print("> " + options[i])
            else:
                print("  " + options[i])
        
        inp, outp, err = select.select([sys.stdin], [], [])
        entry = keyreader.getch()
        if (entry == down):
            if (line_select < line_max):
                line_select = line_select+1
            else:
                line_select = 0
        elif (entry == up):
            if (line_select > 0):
                line_select = line_select-1
            else:
                line_select = line_max
        elif (entry == chr(10)):
            if (suboptions[line_select] == []):
                return line_select
            menu_number = line_select
            line_select += 1
            new_options = []
            new_options.append(options[:menu_number])
            new_options.append(suboptions[menu_number])
            new_options.append(options[menu_number:])
            while(1):
                clear_screen()
                for i in range(0, line_max+1):
                    if (i == line_select):
                        print("> " + new_options[i])
                    else:
                        print("  " + new_options[i])
                        inp, outp, err = select.select([sys.stdin], [], [])
                        entry = keyreader.getch()
                        if (entry == down  and line_select < line_max):
                            line_select = line_select+1
                        elif (entry == up and line_select > 0):
                            line_select = line_select-1
                        elif (entry == chr(10)):
                            if (line_select > menu_number and line_select <= menu_number + len(suboptions)) :
                                return (menu_number, line_select - menu_number)
                            else:
                                if (suboptions[line_select-len(suboptions)] == []):
                                    return line_select-len(suboptions)
                                enter_menu = True
                                break
                            

'''
