import pandas as pd
import json
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

OECDdata = json.load(open('/home/david/Documents/COMTRADE/OECDData.json'))
TurkeyData = json.load(open('/home/david/Documents/COMTRADE/TurkeyData.json'))
PPPlist = OECDdata['data']
TurkeyPPP = [i for i in PPPlist if i['Country'] == 'Turkey']
TurkeyPPPGDP = [i for i in TurkeyPPP if i['TRANSACT'] == 'PPPGDP']
TurkeyPPPind = [i for i in TurkeyPPP if i['TRANSACT'] == 'PPPP41']
TurkeyEXC = [i for i in TurkeyPPP if i['TRANSACT'] == 'EXC']

dates = [datetime.strptime(i['Year'],"%Y") for i in TurkeyPPPGDP]
PPPGDP = [float(i['Value']) for i in TurkeyPPPGDP]
PPPind = [float(i['Value']) for i in TurkeyPPPind]
EXC = [float(i['Value']) for i in TurkeyEXC]
print(dates)
print([i['Transaction'] for i in TurkeyPPP])
fig,ax = plt.subplots()
ax.plot(dates,PPPGDP)
ax.plot(dates,PPPind)
ax.plot(dates,EXC)
plt.show()
