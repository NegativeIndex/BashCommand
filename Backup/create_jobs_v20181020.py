#!/Users/wdai11/anaconda3/bin/python3
import os
import re
import subprocess
import glob
import numpy as np
import shutil 
import sys
sys.path.insert(0,'/Users/wdai11/function')
import my_output as my

######################### 
# global variables
##########################
class common:
    fname="rad.py"     
    otherfiles=('materials.py',)
    nslot=2
    cpu=None

######################### 
# generate one job
##########################
def simu_fun(i,j,k,l,sig):
    print('-------------------')
    fname=common.fname
    dname=sig
    if not os.path.exists(dname):
        os.makedirs(dname)
        # write the new py file
        fname2=os.path.join(dname,fname)
        my.file_re_sub(fname,fname2,
                       (r'^(\s+idx1)=.*$',r"\1={:d}".format(i)),
                       (r'^(\s+idx2)=.*$',r"\1={:d}".format(j)),
                       (r'^(\s+idx3)=.*$',r"\1={:d}".format(k)),
                       (r'^(\s+idx4)=.*$',r"\1={:d}".format(l))    )
        print("Generate {:s}".format(fname2))

        # copy files
        for ff in common.otherfiles:
            print('Copy file '+ff)
            shutil.copy(ff,dname)

        # generate job file
        os.chdir(dname)
        subprocess.call(["mkjob-mpi-all",fname])
        files=glob.glob('dwt*job')
        fname=files[0]
        my.file_re_sub(fname,fname,
                       (r'-pe\s+smp.*$','-pe smp {:d}'.format(common.nslot)),
                       (r'mpirun -np\s+\d+','mpirun -np {:d}'.format(
                           common.nslot)))
        if common.cpu:
            my.file_re_sub(fname,fname,
                           (r'-l\s+\d+G=true','-l {}=true'.format(
                               common.cpu)))
            print('{:d} {} CPU are used'.format(common.nslot,common.cpu))
        else:
            my.file_re_sub(fname,fname,
                           (r'#\$ -l \d+G=true\s+',''))
            print('{:d} any CPU are used'.format(common.nslot))
        
        
        # generate job.begin
        # open("job.begin", 'a').close()
        # print("Generate job.begin")


######################### 
# check two files
##########################
def check_two_files():
    with open(common.fname) as f:
        file1=f.read().splitlines()

    with open("create_jobs.py") as f:
        file2=f.read().splitlines()

    file1=[line.lstrip().rstrip() for line in file1 
           if re.search('=',line)]
    file2=[line.lstrip().rstrip()
           for line in file2 if re.search('=',line)]
    
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
userInput = input('What kinds of CPU (128G/256G/512G/N)? ')
if userInput in ('128G','256G','512G'):
    common.cpu=userInput
elif userInput in ('128','256','512'):
    common.cpu=userInput+'G'
else:
    common.cpu=None

userInput = input('How many job slots?  ')
if userInput.isdigit():
    common.nslot=int(userInput)

# generate new folders
path=os.path.abspath("./")

pols=["Ex","Ey","Ez"]
geoms=["Empty","Wg"]

count=0
for i,pol in enumerate(pols):
    for j,geom in enumerate(geoms):
        if geom=='Empty':
            sig='{}_{}'.format(geom,pol)
            os.chdir(path)
            simu_fun(i,j,0,0,sig)
            count+=1
        else:
            widths=np.arange(0.05,1,0.1)
            for k,width in enumerate(widths):
                hs_src=np.arange(0.0,width/2,0.1)
                for l,h_src in enumerate(hs_src):
                    sig='{}_{}_W{:0.3f}S{:0.3f}'.format(geom,pol,width,h_src)
                    os.chdir(path)
                    simu_fun(i,j,k,l,sig)
                    count+=1
            
print('{} jobs are generated'.format(count))
    
    
