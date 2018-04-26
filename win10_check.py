# -*- coding: utf-8 -*-
import os
import re
import datetime
import time
import json

host = {}
stat = {}

passLength = 8
passHistory = 12
passMaxage = 90
passMinage = 1

resultCheck = 0
resultCheck1 = 0

securityPatch = "KB4093112"
windowVer = "16299"

def regSearch(subject, regPath, regName):
    """이 함수는 세 개의 str 값을 입력받아 레지스트리 값을 검색 후 결과를 반환함.

    : param: str subject: 레지스트리의 의미
    : prram: str regPath: 레지스트리의 위치
    : param: str regName: 레지스트리의 이름
    
    예제:
        다음과 같이 사용:
        >>> regSearch("RecoveryConsoleSecurityLevel", "\"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Setup\RecoveryConsole\"", "SecurityLevel")
        ['0', '1']
    """ 
    try:
        #print("reg query "+ regPath + " /v " + regName + " | find \"" + regName + "\"")
        command = os.popen("reg query "+ regPath + " /v " + regName + " | find \"" + regName + "\"")
        c = re.findall("\d+", command.readline())
        result = c[1]
        #print(subject + ": " + result)
        host[subject] = result
        return result
    except Exception as ex:
        print(ex)
        result = "not found"
        #print(subject + ": " + result)
        host[subject] = result
        return result

def shareSearch():
    """이 함수는 Windows10 PC의 공유 폴더를 검색 후 결과를 반환함.
    
    예제:
        다음과 같이 사용:
        >>> shreSearch()
        ['temp', 'C://temp', '0']
    
    :returns list: 일반 공유폴더 정보를 반환 3번째 값은 공유자에 Everyone 포함 여부를 나타내며 0이면 1이면 취약  
    """
    num = 0
    shareFolder = []
    result = os.popen(u'net share | find /V "기본 공유" | find /V "원격 IPC" | find /V "원격 관리" | find /V "명령을 잘 실행했습니다." | find /V "공유 이름" | find /V "-----" | find ":"')
    try:
        while True:
            line = result.readline()
            if not line:
                line = ["empty", "empty", 0]
                shareFolder.append(line)
                break 
            line = line.split()
            result1 = os.popen("net share " + line[0]).read()
            if result1.find("Everyone") > -1: line.append(1)
            else: line.append(0)
            shareFolder.append(line)
            host["shareFolderStat"] = shareFolder
        return shareFolder
    except Exception as ex:
        print(ex)
        line = ["empty", "empty", 0]
        shareFolder.append(line)
        host["shareFolderStat"] = shareFolder
        return shareFolder

def nameDateTime():
    """이 함수는 host list 에 PC 의 hostname 과 현재날짜, 현재시간을 기록함.
    
    예제:
        다음과 같이 사용:
        >>> nameDatetime()
    """
    result = []
    h = os.popen("hostname").readline().split()
    hostname = h[0]
    result.append(hostname)
    print(hostname)

    dayTime = str(datetime.datetime.now())
    dt = dayTime.split()
    result.append(dt[0])
    result.append(dt[1])
    print(dt[0])
    print(dt[1])

    return result

ndt = nameDateTime()
host["name"] = ndt[0]
host["date"] = ndt[1]
host["time"] = ndt[2]

print(u"PC-01 패스워드 주기적 변경 and PC-02 패스워드 정책이 해당 기관의 보안 정책에 적합하게 설정")
os.popen("secedit.exe /export /cfg temp.txt")
time.sleep(1)
#print((os.popen("dir")).read())
f = open("temp.txt", 'r', encoding='UTF-16')
while True:
    line = f.readline()
    if not line: 
        break
    if line.find("ClearTextPassword") > -1:
        i = int(re.findall("\d+", line)[0])
        if i != 0: resultCheck += 1
        stat[u"ClearTextPassword"] = i
    elif line.find("PasswordComplexity") > -1:
        i = int(re.findall("\d+", line)[0])
        if i != 1: resultCheck += 1
        stat[u"PasswordComplexity"] = i
    elif line.find("MinimumPasswordLength") > -1:
        i = int(re.findall("\d+", line)[0])
        if i < passLength: resultCheck += 1
        stat[u"MinimumPasswordLength"] = i
    elif line.find("PasswordHistorySize") > -1:
        i = int(re.findall("\d+", line)[0])
        if i < passHistory: resultCheck += 1
        stat[u"PasswordHistorySize"] = i
    elif line.find("MaximumPasswordAge") > -1:
        i = int(re.findall("\d+", line)[0])
        if i < passMaxage: resultCheck1 += 1
        stat[u"MaximumPasswordAge"] = i
    elif line.find("MinimumPasswordAge") > -1:
        i = int(re.findall("\d+", line)[0])
        if i < passMinage: resultCheck1 += 1
        stat[u"MinimumPasswordAge"] = i
host["passStat"] = stat
if resultCheck1 > 0 : host["PC-01"] = "false"
elif resultCheck1 ==0: host["PC-01"] = "true"
if resultCheck > 0 : host["PC-02"] = "false"
elif resultCheck ==0: host["PC-02"] = "true"
resultCheck = 0
resultCheck1 = 0
stat = {}
f.close()
os.remove("temp.txt")

print(u"PC-03 복구 콘솔 자동 로그온 금지")
subject = "RecoveryConsoleSecurityLevel"
regPath = "\"HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Setup\RecoveryConsole\""
regName = "SecurityLevel"
result = regSearch(subject, regPath, regName)
if result == '0': host["PC-03"] = "true"
else: host["PC-03"] = "false"

print(u"PC-04 공유 폴더 제거")
subject = "AutoShareFolder"
regPath = "\"HKLM\SYSTEM\CurrentControlSet\Services\lanmanserver\parameters\""
regName = "AutoShareWks"
result = regSearch(subject, regPath, regName)
share = shareSearch()
every = 0
for s in share:
    every = every + s[2]
if ((result == '0') and (every == 0)) : host["PC-04"] = "true"
else: host["PC-04"] = "false"

print(u"PC-05 불필요한 서비스 제거")
host["PC-05"] = "null"

print(u"PC-06 Windows Messenger(MSN, .NET 메신저 등)와 같은 상용 메신저의 사용 금지")
subject = "WindowsMessengerRun"
regPath = "\"HKCU\Software\Policies\Microsoft\Messenger\Client\""
regName = "PreventRun"
result = regSearch(subject, regPath, regName)
if result == '0': host["PC-06"] = "true"
elif result == "not found": host["PC-06"] = "true"
else: host["PC-06"] = "false"

print(u"PC-07 파일 시스템을 NTFS로 포맷")
result = os.popen("fsutil fsinfo drives")
result = (result.read()).split()
del result[0] #드락이브: 제거
for drive in result:
    result1 = os.popen("fsutil fsinfo volumeInfo " + drive)
    if (result1.read()).find("NTFS") > -1: 
        stat[drive] = "true"
    else: 
        stat[drive] = "false"
        resultCheck += 1
host["ntfsStat"] = stat
if resultCheck == 0: host["PC-07"] = "true"
elif resultCheck > 0: host["PC-07"] = "false"
resultCheck = 0
stat = {}

print(u"PC-08 다른 OS로 멀티 부팅 금지")
result = os.popen("bcdedit")
count = (result.read()).count("description")
host["osCount"] = count-1
if count > 2: host["PC-08"] = "false"
else: host["PC-08"] = "true"

print(u"PC-09 브라우저 종료 시 임시 인터넷 폴더 내용 삭제")
subject = "InternetCacheRemove"
regPath = "\"HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\Cache\""
regName = "Persistent"
result = regSearch(subject, regPath, regName)
if result == '0': host["PC-09"] = "true"
else: host["PC-09"] = "false"

print(u"PC-10 HOT FIX 등 최신 보안패치")
result = os.popen('wmic qfe | find "' + securityPatch + '"')
if (result.read()).find("Security") > -1: host["PC-10"] = "true"
else: host["PC-10"] = "false"

print(u"PC-11 최신 서비스팩 적용")
result = os.popen("ver")
if (result.read()).find(windowVer) > -1: host["PC-11"] = "true"
else: host["PC-11"] = "false"

print(u"PC-12 응용 프로그램에 대한 최신 보안 패치 및 벤더 권고사항 적용")
host["PC-12"] = "null"

print(u"PC-13 바이러스 백신 프로그램 설치 및 주기적 업데이트")
subject = "v3AutoUpdateUse"
regPath = "\"HKLM\Software\AhnLab\ASPack\9.0\Option\\UPDATE\""
regName = "autoupdateuse"
result = regSearch(subject, regPath, regName)
if result == '1': host["PC-13"] = "true"
else: host["PC-13"] = "false"

print(u"PC-14 바이러스 백신 프로그램에서 제공하는 실시간 감시 기능 활성화")
subject = "v3ServiceStat"
regPath = "\"HKLM\Software\AhnLab\ASPack\9.0\ServiceStatus\""
regName = "AvMon"
result = regSearch(subject, regPath, regName)
if result == '1': host["PC-14"] = "true"
else: host["PC-14"] = "false"

print(u"PC-15 OS에서 제공하는 침입차단 기능 활성화")
subject = "firewallStat"
regPath = "\"HKLM\SYSTEM\CurrentControlSet\Services\MpsSvc\""
regName = "Start"
result = regSearch(subject, regPath, regName)
if result == '2': host["PC-15"] = "true"
else: host["PC-15"] = "false"

print(u"PC-16 화면보호기 대기 시간 설정 및 재시작 시 암호 보호 설정")
result = os.popen("reg query \"HKCU\Control Panel\Desktop\" | find /I \"save\"")
while True:
    line = result.readline()
    if not line:
        break
    i = int(re.findall("\d+", line)[0])
    if line.find("ScreenSaveActive") > -1:
        stat["ScreenSaveActive"] = i
        if i == 0:
            resultCheck += 1
    elif line.find("ScreenSaverIsSecure") > -1:
        stat["ScreenSaverIsSecure"] = i
        if int(re.findall("\d+", line)[0]) == 0:
            resultCheck += 1
    elif line.find("ScreenSaveTimeOut") > -1:
        stat["ScreenSaveTimeOut"] = i
        if int(re.findall("\d+", line)[0]) > 600:
            resultCheck += 1
host["ScreenSaveStat"] = stat
if resultCheck == 0: host["PC-16"] = "false"
elif resultCheck > 0: host["PC-16"] = "ture"
resultCheck = 0
stat = []

print(u"PC-17 CD, DVD, USB 메모리 등과 같은 미디어의 자동실행 방지 등 이동식 미디어에 대한 보안대책 수립")
result = os.popen("reg query \"HKLM\Software\Microsoft\Windows\CurrentVersion\Policies\Explorer\" /v NoDriveTypeAutoRun")
while True:
    line = result.readline()
    if not line:
        break
    if line.find("NoDriveTypeAutoRun") > -1:
        if line.find("0xff") > -1: 
            host["NoDriveTypeAutoRun"] = "0xff"
            host["PC-17"] = "true"
        else: 
            host["NoDriveTypeAutoRun"] = "false"
            resultCheck = 1
if resultCheck == 0: host["PC-17"] = "false"
elif resultCheck == 1: resultCheck = 0

print(u"PC-18 PC 내부의 미사용(3개월) ActiveX 제거")
host["PC-18"] = "null"

print(u"PC-19 시스템 부팅 시 Windows Messenger 자동실행 금지")
host["PC-19"] = "null"

print(u"PC-20 항목 원격 지원 금지 정책 설정")
subject = "RDPService"
regPath = "\"HKLM\SYSTEM\CurrentControlSet\Control\Terminal Server\""
regName = "fDenyTSConnections"
result = regSearch(subject, regPath, regName)
if result == '1': host["PC-20"] = "ture"
else: host["PC-20"] = "false"

stringOfJsonData = json.dumps(host)
fileName = ndt[0] + "_" + ndt[1] + ".json"
f = open(fileName, 'w')
f.write(stringOfJsonData)
f.close()