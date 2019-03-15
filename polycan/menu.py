import polycan.keyreader as kr
import subprocess as sp
import sys, os
import termios, fcntl
import select
global splash
splash = ("\n\n\t\t\t\t\t\t\t   ___       __     ________   _  __\n"
          +"\t\t\t\t\t\t\t  / _ \___  / /_ __/ ___/ _ | / |/ /\n"
          +"\t\t\t\t\t\t\t / ___/ _ \/ / // / /__/ __ |/    / \n"
          +"\t\t\t\t\t\t\t/_/   \___/_/\_, /\___/_/ |_/_/|_/  \n"
          +"\t\t\t\t\t\t\t            /___/                   \n")
global line_offset 
line_offset = "\t\t\t\t\t\t\t"

down = chr(27) + chr(91) + chr(66)
up = chr(27) + chr(91) + chr(65)
right = chr(27) + chr(91) + chr(67)
left = chr(27) + chr(91) + chr(68)
quit = chr(113)
enter = chr(10)

def clear_screen():
    global splash
    sp.call('clear',shell=True)
    print(splash)
    return

def display_log_pages(options):
    global splash
    page = 0
    fr = 0
    to = 19
    page_max = len(options)//20
    if not (len(options)%20 ==0):
        page_max+=1
    line_select = 0
    line_max = len(options)-1
    if line_max < 1:
        return 0
    while(1):
        clear_screen()
#        print(line_select)
        for i in range(fr, to+1):
            if (i == line_select):
                print(line_offset+"> " + options[i])
            else:
                print(line_offset+"  " + options[i])
        print(line_offset+"Page {} out of {}".format(page+1, page_max))
        keyreader = kr.KeyReader()
        inp, outp, err = select.select([sys.stdin], [], [])
        entry = keyreader.getch()
        if (entry == down):
            if (line_select < to):
                line_select = line_select+1
            else:
                line_select = fr
        elif (entry == up):
            if (line_select > fr):
                line_select = line_select-1
            else:
                line_select = to
        elif (entry == chr(10)):
            return line_select
        elif (entry == left):
            if (page == 0):
                pass
            else:
                page -= 1
                fr = 0 + page*20
                to = 20 + page*20
                line_select = line_select - 20
        elif (entry == right):
            if (page < page_max):
                page += 1
                fr += 20
                to += 20
                line_select += 20
                if (line_select > len(options)):
                    line_select = fr
                if (to > len(options)):
                    to = len(options)-1
            else:
                pass
            
        del keyreader

def display_pages(log):
    global splash
    page = 0
    fr = 0
    to = 20
    page_max = len(log)//20
    while(1):
        clear_screen() 
        print(log[fr:to])
        print(line_offset+"Page {} out of {}".format(page+1, page_max))
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
    global splash
    
    line_select = 0
    line_max = len(options)-1
    if line_max < 1:
        return 0
    while(1):
        clear_screen()
        for i in range(0, line_max+1):
            if (i == line_select):
                print(line_offset+"> " + options[i])
            else:
                print(line_offset+"  " + options[i])
        keyreader = kr.KeyReader()
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
        del keyreader

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
