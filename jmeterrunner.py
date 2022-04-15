import json,time,os,sys
from common import config,commontool
projectpath = sys.path[0]
config.configdict.update({'projectpath':projectpath})
#读取配置文件
config.get_config(rf'{projectpath}\config.yml')

#更新目录
config.configdict.update({'casefolder':config.configdict['casefolder'].replace('projectpath',projectpath)})
config.configdict.update({'resultrootfolder':config.configdict['resultrootfolder'].replace('projectpath',projectpath)})
config.configdict.update({'batfolder':config.configdict['batfolder'].replace('projectpath',projectpath)})

#赋值
threadnum = config.configdict['threadnum']
duration = config.configdict['duration']
concurrentuser = config.configdict['concurrentuser']
ramptime = config.configdict['ramptime']
casefolder = config.configdict['casefolder']
resultrootfolder = config.configdict['resultrootfolder']
batfolder = config.configdict['batfolder']
nowtime = commontool.stamp2time(int(time.time()*1000)).replace(':','_').replace(' ','_')
resultpath = rf'{resultrootfolder}\{nowtime}'


#检查文件夹是否存在，不存在就新建
commontool.newfolder(batfolder)
commontool.newfolder(resultrootfolder)
commontool.newfolder(resultpath)

#实例化logger
from common import logger
print('--------------------------------',resultpath)
logdrive = logger.Logger(resultpath)

from subprocess import Popen, PIPE, STDOUT
from common import mail,zip


print('projectpath:',projectpath)

#命令行传参更新邮箱信息
try:
    config.configdict['mail'] = sys.argv[1]
except:
    pass
try:
    config.configdict['pwd'] = sys.argv[2]
except:
    pass
try:
    config.configdict['mailto'] = sys.argv[3]
except:
    pass

showconfig = dict()
for k,v in config.configdict.items():
    if ('mail' in k) or ('pwd' in k):
        continue
    showconfig.update({k:v})
logdrive.info(f'Run config: {json.dumps(showconfig)}')

filelist = []
bakfilelist = []
for i,j,k in os.walk(casefolder):
    filelist = k
for i in filelist:
    if '.jmx' in i:
        bakfilelist.append(i)

filelist = bakfilelist
logdrive.info(filelist)


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

    cmd = rf'jmeter -n -t "{casefolder}\{i}" -l "{resultrootfolder}\{nowtime}\{resultname}.jtl" -e -o "{resultrootfolder}\{nowtime}\{resultname}" -Dthread.num={str(threadnum)} -Dd.duration={str(duration)} -Dc.concurrentuser={str(concurrentuser)} -Dr.ramptime={str(ramptime)}'
    with open(rf'{batfolder}\{nowtime}\{resultname}.bat','w',encoding='utf8') as f:
        f.write(f'{cmd}')
    #################执行####################
    try:
        print(f'[run for {duration} s] {cmd}')
        print('\n')
        os.chdir(rf'{batfolder}\{nowtime}')
        p = Popen(f"cmd.exe /c {batfolder}\{nowtime}\{resultname}.bat", stdout=PIPE, stderr=STDOUT)

        curline = p.stdout.readline()

        while (curline != b''):
            logdrive.info(curline)
            curline = p.stdout.readline()

        p.wait()
        logdrive.info(f'[finish running for {duration} s] {cmd}')
        logdrive.info(p.returncode)
        logdrive.info('\n\n')
        time.sleep(5)

    except Exception as e:
        logdrive.error(f'[error to run] {cmd}')
        logdrive.exception(e)

    finally:
        logdrive.info(f'--------------------Runcount{runcount} {i}   end------------------------------')

print('done')
zippath = rf'{resultrootfolder}\PerfTestResult_{nowtime}'
zip.Zip(zippath,rf'{resultrootfolder}\{nowtime}')

mailobj = mail.Mail([zippath+'.zip'],[rf'PerfTestResult_{nowtime}.zip'])
mailobj.send(f'<h2>{nowtime} PerfTestResult</h2><p>{json.dumps(showconfig)}</p>')
print('send mail done')
#input('')