# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 22:59:21 2020

@author: znhua
"""


import pyautogui, time

# Open browser window to 
# http://spellout.net/ibexexps/pontexpt/pont-test01/experiment.html
# https://ibexfarm.languagemindbrain.science/ibexexps/pontexpt/test_barewh/experiment.html
def add_url(url):
    # Ctrl L - get to the URL bar
    pyautogui.hotkey('ctrl', 'l')
    # Type in URL, hit enter
    pyautogui.write(url, interval=0)
    pyautogui.press('enter')
    time.sleep(2)



url_base = r'https://spellout.net/ibexexps/znhuang/pineapple-double/server.py?withsquare=000'



pyautogui.hotkey('alt', 'tab')

latin_square = 10 # should go up to ... 30?
for ls in range(6):
    ind = str(ls + 1)
    url = url_base + ind
    add_url(url)
    pyautogui.typewrite(['tab', ind, 'tab', 'space', 'tab', 'enter', 'tab', 'enter'])
    # Instructinos
    for q in range(7):
        pyautogui.typewrite([str(q+1)])
        time.sleep(.2) # Instructions
    time.sleep(1) # Instructions
    pyautogui.typewrite(['tab', 'enter'])
    
    # Actual items
    #for q in range(12+12+4+28):
    for q in range(12+12+48):
        pyautogui.typewrite([ind])
        time.sleep(.1)
    # Profile
    pyautogui.typewrite(["3", "2"])
    time.sleep(1) # Instructions
    pyautogui.hotkey('ctrl', 'r')
    
"""

https://spellout.net/ibexexps/znhuang/pineapple-double/server.py?withsquare=0001
https://spellout.net/ibexexps/znhuang/pineapple-double/server.py?withsquare=0002
https://spellout.net/ibexexps/znhuang/pineapple-double/server.py?withsquare=0003
https://spellout.net/ibexexps/znhuang/pineapple-double/server.py?withsquare=0004
https://spellout.net/ibexexps/znhuang/pineapple-double/server.py?withsquare=0005
https://spellout.net/ibexexps/znhuang/pineapple-double/server.py?withsquare=0006


https://spellout.net/ibexexps/znhuang/pineapple-comp/server.py?withsquare=0001
https://spellout.net/ibexexps/znhuang/pineapple-comp/server.py?withsquare=0002
https://spellout.net/ibexexps/znhuang/pineapple-comp/server.py?withsquare=0003
https://spellout.net/ibexexps/znhuang/pineapple-comp/server.py?withsquare=0004
https://spellout.net/ibexexps/znhuang/pineapple-comp/server.py?withsquare=0005
https://spellout.net/ibexexps/znhuang/pineapple-comp/server.py?withsquare=0006
"""