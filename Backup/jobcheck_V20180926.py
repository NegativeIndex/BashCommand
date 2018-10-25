#!/Users/wdai11/anaconda3/bin/python3
import sys
import subprocess
import datetime 
import re
import os,glob,time
import random
from apscheduler.schedulers.blocking import BlockingScheduler

sys.path.insert(0,'/Users/wdai11/function')
import my_output as my

##########################################
# define a class to collect information from qstat
###########################################
class Rjob:
    def __init__(self,idx,status,btime,server):
        self.idx = idx
        self.status = status 
        self.btime=btime
        self.server=server
    def __str__(self):
        ss="{:>7} {:>3} {:>6}   {:20}".format(
            self.idx,self.status,self.server,
            self.btime.strftime("%m/%d/%Y %H:%M:%S"))
        return  ss     
 
class Rjob_list:
    def __init__(self):
        self.rjobs=[]
        
    def __str__(self):
        ss=""
        for rjob in self.rjobs:
            ss=ss+str(rjob)+"\n"
        ss=ss[:-1]
        return ss

    def append(self,rjob):
        self.rjobs.append(rjob)
        
    # check the status givin idx
    def checkstatus(self,idx):
        for job in self.rjobs:
            if idx==job.idx:
                return job.status
        return "n"
        
    # find a job based on idx    
    def find(self,idx):
        for job in self.rjobs:
            if idx==job.idx:
                return job
        return None

    # how many UI used    
    def UI_usage(self):
        n=0
        for job in self.rjobs:
            if job.server=="UI":
                n+=1
        return n

    # how many jobs submitted
    def n_jobs(self):
        return len(self.rjobs)
    
    # how many jobs running
    def n_rjobs(self):
        n=0
        for job in self.rjobs:
            if job.status=="r":
                n+=1
        return n

    # update itself based on myq results
    def myq(self):
        res = subprocess.check_output("myq")
        lines=res.splitlines()
        del lines[0:2]

        for ll in lines:
            line=ll.decode("utf-8")
            words=line.split()
            idx=words[0]
            status=words[4]
            btime_str=words[5]+" "+words[6]
            queue=words[7]
            btime=datetime.datetime.strptime(btime_str, "%m/%d/%Y %H:%M:%S")
    
            matchObj = re.match( r'(.*)@', queue, re.M|re.I)
            if matchObj:
                server=matchObj.group(1)
            else:
                server="all.q"
            rjob=Rjob(idx,status,btime,server)
            self.append(rjob)

##########################################
# define a class for static jobs from folders
###########################################
# check status,
# qw: wait
# r: good and wait
# eqw: kill and resubmit
# n: not running, check folder, update to d or nd
# d: done, good
# nd: not done and not running, resubmit
class Sjob: 
    def __init__(self,folder,status,message):
        self.folder = folder
        self.status = status 
        self.message = message
    
    def __str__(self):
        ss="------------------------------------------\n{}\n{}".format(
            self.folder,self.message)
        return  ss   

class Sjob_list:
    def __init__(self):
        self.sjobs=[]
       
    def __str__(self):
        ss=""
        for job in self.sjobs:
            if job.status!='d': 
                ss=ss+str(job)+"\n"
        ss=ss[:-1]
        return ss

    def append(self,sjob):
        self.sjobs.append(sjob) 

    def n_jobs(self):
        nqw=0
        nr=0
        nd=0
        n=0
        for job in self.sjobs:
            n+=1
            if job.status=='qw':
                nqw+=1
            elif job.status=='r':
                nr+=1
            elif job.status=='d':
                nd+=1
        return (n,nqw,nr,nd)

    def n_jobs_str(self):
        data=self.n_jobs()
        n=data[0]
        nqw=data[1]
        nr=data[2]
        nd=data[3]
        ss="There are {} jobs; {} finished; {} running; {} waiting".format(
        n,nd,nr,nqw)
        return ss
##########################################
# check job.begin to get information
###########################################
def read_job_begin(folder):
    # get job idx
    fname=os.path.join(folder,"job.begin")
    if os.path.isfile(fname):
        with open(fname) as f:
            lines=f.readlines()
        
        idx="0000"
        if len(lines)>0:
            line=lines[-1]
            matchObj = re.match( r'Your job ([\d]+)', line, re.M|re.I)
            if matchObj:
                idx=matchObj.group(1)
        return (idx,)

    return None

####################################
def read_job_info(folder,idx):
    # Giving idx, retrun btime and etime
    info=(idx,)
    fname=os.path.join(folder,"job.info")
    if os.path.isfile(fname):
        with open(fname) as f:
            lines=f.readlines()
    else:
        return info

    # get btime, job begin time
    for i in range(len(lines)-2):
        matchObj1=re.match( r'^[+]+$', lines[i], re.M|re.I)
        matchObj2=re.match( '^'+idx, lines[i+2], re.M|re.I)
        if matchObj1 and matchObj2:
            line=lines[i+1]
            ss=line.split()
            newline="{}/{}/{} {}".format(ss[1],ss[2],ss[5],ss[3])
            btime=datetime.datetime.strptime(newline, "%b/%d/%Y %H:%M:%S")
            info+=(btime,)

    for i in range(len(lines)-2):
        matchObj1=re.match( r'^[-]+$', lines[i], re.M|re.I)
        matchObj2=re.match( '^'+idx, lines[i+2], re.M|re.I)
        if matchObj1 and matchObj2:
            line=lines[i+1]
            ss=line.split()
            newline="{}/{}/{} {}".format(ss[1],ss[2],ss[5],ss[3])
            etime=datetime.datetime.strptime(newline, "%b/%d/%Y %H:%M:%S")
            info+=(etime,)
    
    return info

####################################
def submit_job(server="all.q",smp=2):
    files= glob.glob("dwt*.job")
    if files:
        jobname=files[0]
        comm1=["-q", server]
        comm2=["-pe", "smp", str(smp)]
        # comm3=["|","tee","-a","job.begin"]
        # comm3=[">>","job.begin"]
        res=subprocess.check_output(["qsub"]+comm1+comm2+[jobname])
        line=res.decode("utf-8")
        print(line)
        with open("job.begin", "a+") as f:
            f.write(line)
      
####################################
def kill_job(idx):
    comm=["qdel",idx]
    res = subprocess.check_output(comm)
    print(res)
    time.sleep(3)

####################################
def touch(path):
    basedir = os.path.dirname(path)
    if not os.path.exists(basedir):
        os.makedir(basedir)

    with open(path, 'a'):
        os.utime(path, None)            

#########################################
# main function, check job files in folders
##########################################
def main(path):
    print("######################################")
    running_jobs=Rjob_list()
    running_jobs.myq()
    print(running_jobs)
    nUI=running_jobs.UI_usage()
    print("There are {} UI jobs".format(nUI))
    print("{} jobs running; {} jobs submitted".format(
        running_jobs.n_rjobs(),running_jobs.n_jobs()))
    ###################################
    # check folders for static jobs
    ###################################
    os.chdir(path)
    cwd=os.getcwd()
    folders=[x[0] for x in os.walk(cwd)]
    folders.sort()
    # print(folders)
    # generate the job list I want to monitor
    # the folder should has job.begin
    folder_jobs=Sjob_list()
    for folder in folders:
        os.chdir(folder)
        # print(folder)
        # working folder when it has job.begin file
        binfo=read_job_begin(folder)
        if binfo is not None:
            idx=binfo[0]
            # print(folder)
            # now get idx status
            status=running_jobs.checkstatus(idx)
            info=read_job_info(folder,idx)
            if status=="n":
                if len(info)==3 and glob.glob("*.dat"):
                    status="d"
                else:
                    status="nd"
    
            # print(status)

            if status=='r':
                rjob=running_jobs.find(idx)
                stime=rjob.btime  # job submission time
                btime=info[1]     # job beginning time
                ctime=datetime.datetime.now() # current time
                dtime=ctime-btime  # job running time

                ctime_str=datetime.datetime.strftime(ctime,"%m/%d/%Y %H:%M:%S")
                dtime_str=my.nice_sec2str(dtime.total_seconds())
                ss1="Running     "+idx
                ss2="Checked at "+ctime_str
                ss3="Running time: "+dtime_str
                message=ss1+"\n"+ss2+"\n"+ss3
            elif status=="qw":
                ss1="Waiting     "+idx
                ctime=datetime.datetime.now() # current time
                rjob=running_jobs.find(idx)
                stime=rjob.btime  # job submission time      
                dtime=ctime-stime

                ctime_str=datetime.datetime.strftime(ctime,"%m/%d/%Y %H:%M:%S")
                dtime_str=my.nice_sec2str(dtime.total_seconds())
                ss2="Checked at "+ctime_str
                ss3="Waiting time: "+dtime_str
                message=ss1+"\n"+ss2+"\n"+ss3   
            elif status=="eqw":
                print(folder)
                # kill it and resubmit
                ctime=datetime.datetime.now()
                ctime_str=datetime.datetime.strftime(ctime,"%m/%d/%Y %H:%M:%S")

                ss1="Error     "+idx+" Kill and resubmit"
                ss2="Checked at "+ctime_str
                message=ss1+"\n"+ss2
                kill_job(idx)
                nsmp=random.randint(2,4)
                if nUI<2:
                    submit_job(server="UI",smp=nsmp)
                    nUI=nUI+1
                else:
                    submit_job(server="all.q",smp=nsmp)
            elif status=="d":
                btime=info[1]
                etime=info[2]
                dtime=etime-btime
                dtime_str=my.nice_sec2str(dtime.total_seconds())
                ss1="Done"
                ss2="Simulation time "+dtime_str
                message=ss1+"\n"+ss2      
            else:
                print(folder)
                ctime=datetime.datetime.now()
                ctime_str=datetime.datetime.strftime(ctime,"%m/%d/%Y %H:%M:%S")
                ss1="Not running, resubmit"
                ss2="Checked at "+ctime_str
                message=ss1+"\n"+ss2
                if nUI<2:
                    submit_job(server="UI")
                    nUI=nUI+1
                else:
                    submit_job(server="all.q")
        
            fjob=Sjob(folder,status,message)
            folder_jobs.append(fjob)

    # for job in folder_jobs:
    #     print(job)

    print(folder_jobs.n_jobs_str())
    print(folder_jobs)
    print("End of the scan")
    sys.stdout.flush()
    os.chdir(cwd)


############################
# run main function
##############################
def my_job():
    oldstdout = sys.stdout
    sys.stdout = open('currentjob.txt', 'w+')
    main('./')
    sys.stdout.flush()
    sys.stdout=oldstdout


scheduler = BlockingScheduler()
scheduler.add_job(my_job, 'interval', minutes=10,
                  next_run_time=datetime.datetime.now())
scheduler.start()



