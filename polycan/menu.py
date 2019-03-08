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
right = chr(27) + chr(91) + chr(67)
left = chr(27) + chr(91) + chr(68)
quit = chr(113)
enter = chr(10)

def clear_screen():
    sp.call('clear',shell=True)
    print(splash)
    return

def display_pages(log):
    page = 0
    fr = 0
    to = 20
    page_max = len(log)//20
    while(1):
        clear_screen() 
        print(log[fr:to])
        print('Page {} out of {}'.format(page+1, page_max))
        keyreader = kr.KeyReader()
        inp, outp, err = select.select([sys.stdin], [], [])
        entry = keyreader.getch()
        if (entry == left):
            if (page == 0):
                pass
            else:
                page -= 1
                fr = 0 + page*20
                to = 20 + page*20
        elif (entry == right):
            if (page+1 == page_max):
                if(len(log)%20 != 0):
                    fr = page*20
                    to = page*20 + len(log)%20
                    page += 1
            elif page+1 > page_max:
                pass
            else:
                page += 1
                fr = 0 + page*20
                to = 20 + page*20
        elif (entry == chr(10) or entry == quit):
            return
        del keyreader

def launch_menu(options):
    line_select = 0
    line_max = len(options)-1
    if line_max < 1:
        return 0
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
