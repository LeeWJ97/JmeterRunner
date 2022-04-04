import json
import time,os,yaml,sys
from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
import logger
#projectpath = os.path.dirname(sys.argv[0]).replace('/','\\')
projectpath = sys.path[0]
print('projectpath:',projectpath)
def stamp2time(timestamp):
    try:
        k = len(str(timestamp)) - 10
        timestamp = datetime.fromtimestamp(timestamp / (1 * 10 ** k))
        timestr = timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")
        return timestr[:-3]
    except Exception as e:
        print(e)
        return [False,str(e)]

#读取配置文件
with open(f'{projectpath}\config.yml','r',encoding='utf-8') as f:
    getconfig = yaml.safe_load(f)

#更新目录

getconfig.update({'casefolder':getconfig['casefolder'].replace('projectpath',projectpath)})
getconfig.update({'resultrootfolder':getconfig['resultrootfolder'].replace('projectpath',projectpath)})
getconfig.update({'batfolder':getconfig['batfolder'].replace('projectpath',projectpath)})

#赋值
threadnum = getconfig['threadnum']
durtion = getconfig['durtion']
concurrentuser = getconfig['concurrentuser']
ramptime = getconfig['ramptime']
casefolder = getconfig['casefolder']
resultrootfolder = getconfig['resultrootfolder']
batfolder = getconfig['batfolder']


nowtime = stamp2time(int(time.time()*1000)).replace(':','_').replace(' ','_')
resultpath = rf'{resultrootfolder}\{nowtime}'

#判断是否存在必要的文件夹
if not os.path.exists(batfolder):
    os.mkdir(batfolder)
    print(f'[log] create {batfolder} successfully!')

if not os.path.exists(resultrootfolder):
    os.mkdir(resultrootfolder)
    print(f'[log] create {resultrootfolder} successfully!')

if not os.path.exists(resultpath):
    os.mkdir(resultpath)
    print(f'[log] create {resultrootfolder}\{nowtime} successfully!')

#实例化logger
logdrive = logger.Logger(resultpath)
logdrive.info(f'Run config: {json.dumps(getconfig,indent=4)}')

filelist = []
for i,j,k in os.walk(casefolder):
    filelist = k
for i in filelist:
    if '.jmx' not in i:
        filelist.remove(i)
logdrive.info(filelist)


# with open(rf'{resultpath}\config.txt','w',encoding='utf8') as f:
#     f.write(f'threadnum:{threadnum}  duration:{durtion}  concurrentuser:{concurrentuser}  ramptime:{ramptime}')

#开始循环case
runcount = 0
for i in filelist:
    runcount+=1
    logdrive.info(f'--------------------Runcount{runcount} {i}  start------------------------------')
    resultname = f'{i[:i.rfind(".jmx")]}'

    if not os.path.exists(rf'{resultrootfolder}\{nowtime}\{resultname}'):
        os.mkdir(rf'{resultrootfolder}\{nowtime}\{resultname}')
        #print(f'[log] create {resultrootfolder}\{nowtime}\{resultname} successfully!')

    if not os.path.exists(rf'{batfolder}\{nowtime}'):
        os.mkdir(rf'{batfolder}\{nowtime}')

    cmd = rf'jmeter -n -t "{casefolder}\{i}" -l "{resultrootfolder}\{nowtime}\{resultname}.jtl" -e -o "{resultrootfolder}\{nowtime}\{resultname}" -Dthread.num={str(threadnum)} -Dd.duration={str(durtion)} -Dc.concurrentuser={str(concurrentuser)} -Dr.ramptime={str(ramptime)}'
    with open(rf'{batfolder}\{nowtime}\{resultname}.bat','w',encoding='utf8') as f:
        f.write(f'{cmd}')
    #################执行####################
    try:
        print(f'[run for {durtion} s] {cmd}')
        print('\n')
        os.chdir(rf'{batfolder}\{nowtime}')
        p = Popen(f"cmd.exe /c {batfolder}\{nowtime}\{resultname}.bat", stdout=PIPE, stderr=STDOUT)

        curline = p.stdout.readline()

        while (curline != b''):
            logdrive.info(curline)
            curline = p.stdout.readline()

        p.wait()
        logdrive.info(f'[finish running for {durtion} s] {cmd}')
        logdrive.info(p.returncode)
        logdrive.info('\n\n')
        time.sleep(5)

    except Exception as e:
        logdrive.error(f'[error to run] {cmd}')
        logdrive.exception(e)

    finally:
        logdrive.info(f'--------------------Runcount{runcount} {i}   end------------------------------')

print('done')
#input('')