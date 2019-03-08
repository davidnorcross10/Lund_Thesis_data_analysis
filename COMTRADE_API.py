import json
from requests_html import HTMLSession
import time

classificationHS_path = "/home/david/Documents/Thesis_Data/classificationHS.json"
classificationHS = json.load(open(classificationHS_path))
masterJSON_path = "/home/david/Documents/Thesis_Data/COMTRADE/TurkeyExportsMaster.json"

codeList = [i["id"] for i in classificationHS["results"] if len(i["id"]) == 4]

yearDict = {1:"1999,2000,2001,2002,2003",2:"2004,2005,2006,2007,2008",3:"2009,2010,2011,2012,2013",4:"2014,2015,2016,2017"}

def pullData():
    for i in yearDict:
        if i > 3:
            y = yearDict[i]
            token = True
            index = 0
            while token == True:
                codes = codeList[index:index+20]
                for j,c in enumerate(codes):
                    if int(c[:2]) >= 24:
                        codes = codes[:j]
                        token = False
                        break
                index += 20
                codeString = ",".join(codes)
                print(codeString)
                time.sleep(1)
                #first {} should be replaced with comma separated list of years
                #second {} should be replaced with comma separated list of product codes
                url = 'http://comtrade.un.org/api/get?max=50000&type=C&freq=A&px=HS&ps={}&r=792&p=all&rg=2&cc={}&head=M'.format(y,codeString)

                session = HTMLSession()
                page = session.get(url)
                responseJSON = json.loads(page.html.html)
                dumpPath = '/home/david/Documents/Thesis_Data/COMTRADE/TurkeyExports{}.json'.format(yearDict[i][:4]+'-'+codeString[:4])
                json.dump(responseJSON,open(dumpPath,'w'))

def readData():
    resultList = []
    for i in yearDict:
        token = True
        index = 0
        while token == True:
            codes = codeList[index:index+20]
            for j,c in enumerate(codes):
                if int(c[:2]) >= 24:
                    codes = codes[:j]
                    token = False
                    break
            codeString = ",".join(codes)
            index += 20
            readPath = '/home/david/Documents/Thesis_Data/COMTRADE/TurkeyExports{}.json'.format(yearDict[i][:4]+'-'+codeString[:4])
            r = json.load(open(readPath))
            resultList.append(r)
    return resultList

def cleanData():
    resultList = []
    for i in yearDict:
        token = True
        index = 0
        while token == True:
            codes = codeList[index:index+20]
            for j,c in enumerate(codes):
                if int(c[:2]) >= 24:
                    codes = codes[:j]
                    token = False
                    break
            codeString = ",".join(codes)
            index += 20
            readPath = '/home/david/Documents/Thesis_Data/COMTRADE/TurkeyExports{}.json'.format(yearDict[i][:4]+'-'+codeString[:4])
            r = json.load(open(readPath))
            for d in r["dataset"]:
                x = {}
                for subIndex in d:
                    if d[subIndex] != '' and d[subIndex] != None:
                        x[subIndex] = d[subIndex]
                resultList.append(x)
    outJSON = {"dataset":resultList}
    json.dump(outJSON,open('/home/david/Documents/Thesis_Data/COMTRADE/TurkeyExportsMaster.json','w'))

def totalExportValue(year):
    masterJSON = json.load(open(masterJSON_path))
    data = masterJSON["dataset"]
    data = [i for i in data if i['yr'] == year]
    totalValue = 0
    for i in data:
        totalValue += i['TradeValue']
    print(totalValue)

totalExportValue(2003)

#pullData()
#cleanData()
'''readPath = '/home/david/Documents/Thesis_Data/COMTRADE/TurkeyExports{}.json'.format('2009'+'-'+'1517')
r = json.load(open(readPath))
data = r["dataset"]
data = [i for i in data if i['yr'] == 2010]
print(data)
goods = set([i['cmdCode'] for i in data])
for g in goods:
    rateJSON = {}
    desc = None
    subset = [i for i in data if i['cmdCode'] == g]
    for j in subset:
        try:
            desc = j['cmdDescE']
            rateJSON[j['pt3ISO']] = j['TradeValue']/j['NetWeight']
        except:
            rateJSON[j['pt3ISO']] = None
    print(desc + ': ' + str(rateJSON))'''

'''r1 = readData()

'NetWeight'
'yr'
'cmdCode'
'TradeValue'
'pt3ISO'
for i in r1[0]["dataset"]:
    if i['pt3ISO'] == None:
        print(i)
    #print(i['pt3ISO'])
'''
