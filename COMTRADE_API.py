import json
from requests_html import HTMLSession
import time

classificationHS_path = "/home/david/Documents/Lund_Thesis/Thesis_Data/classificationHS.json"
classificationHS = json.load(open(classificationHS_path))
masterJSON_path = "/home/david/Documents/Lund_Thesis/Thesis_Data/COMTRADE/Turkey/TurkeyExportsMaster.json"

codeList = [i["id"] for i in classificationHS["results"] if len(i["id"]) == 4]

yearDict = {1:"1999,2000,2001,2002,2003",2:"2004,2005,2006,2007,2008",3:"2009,2010,2011,2012,2013",4:"2014,2015,2016,2017"}

def pullData(r,rg):
    #rg = trade flow. 1 = import, 2 = export
    #r = reporter. 792 = Turkey, 376 = Israel, 300 = Greece
    rDict = {'Turkey':'792','Israel':'376','Greece':'300'}
    rgDict = {'Imports':'1','Exports':'2'}
    for i in yearDict:
        if i > -1:
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
                url = 'http://comtrade.un.org/api/get?max=50000&type=C&freq=A&px=HS&ps={}&r={}&p=all&rg={}&cc={}&head=M'.format(y,rDict[r],rgDict[rg],codeString)

                session = HTMLSession()
                page = session.get(url)
                responseJSON = json.loads(page.html.html)
                dumpPath = '/home/david/Documents/Lund_Thesis/Thesis_Data/COMTRADE/{}.json'.format(r+'/'+r+rg+yearDict[i][:4]+'-'+codeString[:4])
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
            readPath = '/home/david/Documents/Lund_Thesis/Thesis_Data/COMTRADE/Turkey/TurkeyExports{}.json'.format(yearDict[i][:4]+'-'+codeString[:4])
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
            readPath = '/home/david/Documents/Lund_Thesis/Thesis_Data/COMTRADE/Turkey/TurkeyExports{}.json'.format(yearDict[i][:4]+'-'+codeString[:4])
            r = json.load(open(readPath))
            for d in r["dataset"]:
                x = {}
                for subIndex in d:
                    if d[subIndex] != '' and d[subIndex] != None:
                        x[subIndex] = d[subIndex]
                resultList.append(x)
    outJSON = {"dataset":resultList}
    json.dump(outJSON,open('/home/david/Documents/Lund_Thesis/Thesis_Data/COMTRADE/Turkey/TurkeyExportsMaster.json','w'))

def totalExportValue(year):
    masterJSON = json.load(open(masterJSON_path))
    data = masterJSON["dataset"]
    data = [i for i in data if i['yr'] == year]
    totalValue = 0
    for i in data:
        totalValue += i['TradeValue']
    return totalValue

#totalExportValue(2010)
#pullData('Turkey','Imports')
#pullData()
#cleanData()
'''readPath = '/home/david/Documents/Lund_Thesis/Thesis_Data/COMTRADE/Turkey/TurkeyExports{}.json'.format('2009'+'-'+'1517')
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
