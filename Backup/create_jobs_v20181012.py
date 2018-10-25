#!/Users/wdai11/anaconda3/bin/python3
import os
import re
import subprocess
import glob
import numpy as np
from shutil import copyfile
import sys
sys.path.insert(0,'/Users/wdai11/function')
import my_output as my

######################### 
# global variables
##########################
class common:
    fname="rad.py"     
    nslot=3

######################### 
# generate one job
##########################
def simu_fun(i,j,k,sig):
    print('-------------------')
    fname=common.fname
    dname=sig
    if not os.path.exists(dname):
        os.makedirs(dname)
        # write the new py file
        fname2=os.path.join(dname,fname)
        my.file_re_sub(fname,fname2,
                       (r'^idx1=.*$',"idx1={:d}".format(i)),
                       (r'^idx2=.*$',"idx2={:d}".format(j)),
                       (r'^idx3=.*$',"idx3={:d}".format(k)))

        print("Generate {:s}".format(fname2))
        # generate job file
        os.chdir(dname)
        subprocess.call(["mkjob-py-all",fname])
        files=glob.glob('dwt*job')
        fname=files[0]
        my.file_re_sub(fname,fname,
                       (r'-pe\s+smp.*$','-pe smp {:d}'.format(common.nslot)))

        open("job.begin", 'a').close()
        print("Generate job.begin")


######################### 
# check two files
##########################
def check_two_files():
    with open(common.fname) as f:
        file1=f.read().splitlines()

    with open("create_jobs.py") as f:
        file2=f.read().splitlines()

    file1=[line for line in file1 if re.search('=',line)]
    file2=[line for line in file2 if re.search('=',line)]
    
    sameline=[line for line in file1 if line in file2]

    print('-----------------------')
    for line in sameline:
        print(line)
    print('-----------------------')
    userInput = input('The two files have such commone lines. y/n?  ');

    if userInput!='y':
        sys.exit('Something is wrong. Modify the file')
    
########################## 
# main function
##########################
check_two_files()
userInput = input('How many job slots?  ')
if userInput.isdigit():
    common.nslot=int(userInput)

# generate new folders
path=os.path.abspath("./")

geoms=['Al']
pols=['Ex']
src_hs=np.arange(400,500,20)/1000


count=0
for i,geom in enumerate(geoms):
    for j,pol in enumerate(pols):
        if geom=='Empty':
            sig="{}_{}".format(geom,pol)
            os.chdir(path)
            simu_fun(i,j,0,sig)
            count+=1
        else:
            for k,src_h in enumerate(src_hs):
                sig="{}_{}_h{:0.3f}".format(geom,pol,src_h)
                os.chdir(path)
                simu_fun(i,j,k,sig)
                count+=1
            
print('{} jobs are generated'.format(count))
    
    
