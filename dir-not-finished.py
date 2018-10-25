#!/Users/wdai11/anaconda3/bin/python3

import sys
import subprocess
import datetime
import re
import os,glob,time
import random

cwd=os.getcwd()
folders=[x[0] for x in os.walk(cwd)]
folders.sort()

for folder in folders:
    os.chdir(folder)
    if glob.glob('dwt*job'): 
        # if os.path.isfile('job.done'):
        if not glob.glob('*dat'): 
            print(folder)
