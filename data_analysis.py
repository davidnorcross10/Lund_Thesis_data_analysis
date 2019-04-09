import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import lemurs as lm
import COMTRADE_API as COM
import time

### WORLD BANK DATA ###
                                ###CSV###
population_path = '/home/david/Documents/Lund_Thesis/Thesis_Data/WB/population/population.csv'
population_0_14_path = '/home/david/Documents/Lund_Thesis/Thesis_Data/WB/population_0_14/population_0_14.csv'
agr_va_path = '/home/david/Documents/Lund_Thesis/Thesis_Data/WB/agr_va_per_worker/agr_va_per_worker.csv'
emp_in_ag_path = '/home/david/Documents/Lund_Thesis/Thesis_Data/WB/emp_in_ag/emp_in_ag.csv'
emp_to_pop_path = '/home/david/Documents/Lund_Thesis/Thesis_Data/WB/emp_to_pop/emp_to_pop.csv'
                                ###JSON###
population_json_path = '/home/david/Documents/Lund_Thesis/Thesis_Data/WB/population/population.json'
population_0_14_json_path = '/home/david/Documents/Lund_Thesis/Thesis_Data/WB/population_0_14/population_0_14.json'
agr_va_json_path = '/home/david/Documents/Lund_Thesis/Thesis_Data/WB/agr_va_per_worker/agr_va_per_worker.json'
emp_in_ag_json_path = '/home/david/Documents/Lund_Thesis/Thesis_Data/WB/emp_in_ag/emp_in_ag.json'
emp_to_pop_json_path = '/home/david/Documents/Lund_Thesis/Thesis_Data/WB/emp_to_pop/emp_to_pop.json'

### OECD DATA ###
                                ###CSV###
comp_by_ind_path = '/home/david/Documents/Lund_Thesis/Thesis_Data/OECD/comp_by_ind.csv'
exchange_path = '/home/david/Documents/Lund_Thesis/Thesis_Data/OECD/DP_LIVE_Exchange_rates.csv'
                                ###JSON###
comp_by_ind_json_path = '/home/david/Documents/Lund_Thesis/Thesis_Data/OECD/comp_by_ind.json'
exchange_json_path = '/home/david/Documents/Lund_Thesis/Thesis_Data/OECD/DP_LIVE_Exchange_rates.json'

### Bureau of Labor Statistics (BLS) DATA (Consumer Price Index)###
                                ###XLSX###
CPI_path = '/home/david/Documents/Lund_Thesis/Thesis_Data/BLS/CPI.xlsx'
                                ###JSON###
CPI_2010_normalized_JSON_path = '/home/david/Documents/Lund_Thesis/Thesis_Data/BLS/CPI_2010_normalized.json'

OECD_countries = ['AUS','AUT','BEL','CAN','CHL','CZE','DNK','EST','FIN','FRA','DEU','GRC','HUN','ISL','IRL','ISR','ITA','JPN','KOR','LVA','LTU','LUX','MEX','NLD','NZL','NOR','POL','PRT','SVK','SVN','ESP','SWE','CHE','TUR','GBR','USA']

def csv_to_json():
    #Units: people
    emp_to_pop = lm.read_WB(emp_to_pop_path)

def CPI_2010_normalize():
    CPI_df = pd.read_excel(CPI_path,skiprows=11)
    CPI_df.set_index('Year',inplace=True)
    CPIJSON = {}
    CPIyears = CPI_df.index.values
    yearList = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    for year in CPIyears:
        try:
            avg = np.mean([CPI_df.loc[year][i] for i in yearList])
            avg2010 = np.mean([CPI_df.loc[2010][i] for i in yearList])
            value = avg2010/avg
            CPIJSON[str(year)] = value
        except:
            pass
    json.dump(CPIJSON,open(CPI_2010_normalized_JSON_path,'w'))

CPI_2010_index = json.load(open(CPI_2010_normalized_JSON_path))

def COMtotalExportValue(year):
    value = COM.totalExportValue(year) * CPI_2010_index[str(year)]
    return value

#Units: value of local currency in USD
exchange_rates_USD = lm.read_JSON(exchange_json_path)

#obtain country and year disaggregated percentages of employment in agriculture
emp_in_ag = lm.read_JSON(emp_in_ag_json_path)
emp_in_ag = emp_in_ag.multiply(.01)

#obtain total working age population by subtracting population 0-14 y/o from total
population = lm.read_JSON(population_json_path)
population_0_14 = lm.read_JSON(population_0_14_json_path)
working_age = population.subtract(population_0_14)

#obtain total number of people working in agriculture by multiplying ratio of
#agricultural employment to total employment by total number of employed people
emp_to_pop = lm.read_JSON(emp_to_pop_json_path)
emp_to_pop = emp_to_pop.multiply(.01)
total_emp = working_age.multiply(emp_to_pop)
total_agr_emp = total_emp.multiply(emp_in_ag)
#print('ag workers')
#print(total_agr_emp.data['TUR'])

#Units: value added per worker (constant 2010 USD)
agr_va = lm.read_JSON(agr_va_json_path)
agr_va = agr_va.filter(**{'Subject':'Agriculture, forestry, and fishing, value added per worker (constant 2010 US$)'})
total_agr_va = agr_va.multiply(total_agr_emp)
#print(total_agr_va.data['TUR'])

#Units: National currency, current prices (millions)
comp_by_ind = lm.read_JSON(comp_by_ind_json_path)
for c in comp_by_ind.data:
    iList = []
    for t in comp_by_ind.data[c]:
        for i in comp_by_ind.data[c][t]:
            if i not in iList:
                if i == 'D1VA' or i == 'D1':
                    iList.append(i)


agr_comp = comp_by_ind.filter(**{'Subject':'D1VA'})
total_comp = comp_by_ind.filter(**{'Subject':'D1'})
agr_comp = agr_comp.multiply(1000000)
#print(agr_comp.data['TUR'])
total_comp = total_comp.multiply(1000000)

#Change units to current price USD
agr_comp = agr_comp.divide(exchange_rates_USD)

#Change units to constant 2010 USD
agr_comp = agr_comp.scale(CPI_2010_index)

agr_comp_pw = agr_comp.divide(total_agr_emp)
print(agr_comp_pw.data['TUR'])
agr_comp_to_va = agr_comp_pw.divide(agr_va)

def graph_agr_comp_to_va():
    fig,ax = plt.subplots()
    #country_list = ['FRA','POL','SWE','ISR','TUR','ITA','ESP','AUT','BEL']
    country_list = OECD_countries
    graphDict = {}

    for c in agr_comp_to_va.data:
        if c in country_list:
            xVals = [i for i in agr_comp_to_va.data[c]]
            yVals = [agr_comp_to_va.data[c][i]['Value'] for i in agr_comp_to_va.data[c]]
            acpw = [agr_comp_pw.data[c][i]['Value'] for i in agr_comp_pw.data[c]]

            ax.plot(xVals,yVals,label=c)
    plt.title('Ratio of Agricultural Compensation to Value Added per worker')
    plt.show()

def avg_agr_va_pw(year,countryList):
    sum_va = 0
    sum_emp = 0
    for c in countryList:
        sum_va = np.nansum([total_agr_va.data[c][str(year)]['Value'],sum_va])
        sum_emp = np.nansum([total_agr_emp.data[c][str(year)]['Value'],sum_emp])
    return sum_va/sum_emp

def avg_agr_emp(year,countryList):
    

def graph_ag_comp():
    fig,ax = plt.subplots()
    for i in ['TUR','FRA','ISR','ITA','CZE','POL']:
        x = [str(j) for j in range(1999,2018)]
        y = [agr_comp_pw.data[i][str(j)]['Value'] for j in range(1999,2018)]
        ax.plot(x,y,label=i)
    plt.legend()
    plt.title('Agricultural Compensation per Worker',weight='bold',y=1.08)
    plt.ylabel('Constant 2010 USD')
    plt.xlabel('Source: OECD')
    plt.grid()
    plt.xticks(rotation=45)
    plt.show()

def graph_agr_workers():
    fig,ax = plt.subplots()
    for i in ['TUR','FRA','ISR','ITA','CZE','POL']:
        x = [str(j) for j in range(1998,2018)]
        y = [emp_in_ag.data[i][str(j)]['Value']*100 for j in range(1998,2018)]
        ax.plot(x,y,label=i)
    plt.legend()
    plt.title('Percent of workforce employed in agriculture',weight='bold',y=1.08)
    plt.ylabel('Percent')
    plt.xlabel('Source: World Bank')
    plt.grid()
    plt.xticks(rotation=45)
    plt.show()

def graph_agr_va():
    fig,ax = plt.subplots()
    countryList = OECD_countries
    year_list = [str(y) for y in np.arange(1998,2017)]
    OECD_AVG = [avg_agr_va_pw(y,countryList) for y in year_list]
    ax.plot(year_list,OECD_AVG,label='OECD Average')
    Turkey_va_pw = [agr_va.data['TUR'][str(y)]['Value'] for y in year_list]
    ax.plot(year_list,Turkey_va_pw,label='Turkey')
    oecdRate = np.mean([(OECD_AVG[i+1]-OECD_AVG[i])/OECD_AVG[i] for i in range(len(OECD_AVG)-1)])
    TurkeyRate = np.mean([(Turkey_va_pw[i+1]-Turkey_va_pw[i])/Turkey_va_pw[i] for i in range(len(Turkey_va_pw)-1)])
    print(oecdRate)
    print(TurkeyRate)
    plt.legend()
    plt.title('Value Added in Agriculture, Forestry, and Fishing (per worker)',weight='bold',y=1.08)
    plt.ylabel('Constant 2010 USD')
    plt.xlabel('Source: World Bank')
    plt.grid()
    plt.ylim((0,30000))
    plt.xticks(rotation=45)
    plt.show()

def graph_exports_to_va():
    fig,ax = plt.subplots()

    total_agr_va_TUR = total_agr_va.data['TUR']

    xVals = [i for i in range(1999,2018)]
    #yVals = [COMtotalExportValue(int(i))/total_agr_va_TUR[i]['Value'] for i in total_agr_va_TUR]
    yVals = [COMtotalExportValue(int(i)) for i in range(1999,2018)]
    yVals2 = [total_agr_va_TUR[str(i)]['Value'] for i in range(1999,2018)]
    ax.plot(xVals,yVals,label='Export Value')
    ax.plot(xVals,yVals2,label='Value Added')
    plt.legend()
    plt.xticks(rotation=45)
    plt.show()

graph_ag_comp()
#graph_agr_comp_to_va()
#graph_agr_comp_to_va()
'''fig,ax = plt.subplots()
country_list = ['FRA','POL','SWE','ISR','TUR']
print([i for i in agr_comp_pw.data])
for c in agr_comp_pw.data:
    if c in country_list:
        xVals = [i for i in agr_comp_pw.data[c]]
        yVals = [agr_comp_pw.data[c][i]['Value'] for i in agr_comp_pw.data[c]]
        ax.plot(xVals,yVals)
plt.xticks(rotation=45)
plt.show()'''
#import_json()
#csv_to_json()

'''
#### APPEND JSON FORMATTED ELEMENTS TO EXCHANGE RATE (EUR) DATABASE LIST ####
exchange_rates_EUR = []
for y in range(1999,2018):
    usd_to_eur = 1/([i for i in exchange_rates_USD.data if i['LOCATION'] == 'EU28' and i['TIME'] == y][0]['Value'])
    for el in [i for i in exchange_rates_USD.data if i['TIME'] == y]:
        #el['Value'] = el['Value'] * usd_to_eur
        exchange_rates_EUR.append({'TIME':el['TIME'],'LOCATION':el['LOCATION'],'Value':el['Value']*usd_to_eur})
exchange_rates_EUR = lm.read_List(exchange_rates_EUR)

for i in comp_by_ind.data:
    try:
        i['Value'] = i['Value'] * exchange_rates_EUR.query(**{'LOCATION':i['LOCATION'],'TIME':i['TIME']})
    except:
        i['Value'] = None

#print(comp_by_ind.fields)
#print(comp_by_ind.query(**{'LOCATION':'TUR','TIME':2012,'Subject':'Agriculture, forestry and fishing (ISIC Rev.4)'}))
'''
'''fig,ax = plt.subplots()
for c in countries:
    displayJSON = {}
    for i in [j for j in comp_by_ind if j['Country'] == c]:
        displayJSON[i['TIME']] = i['Value']
        #if i['Value'] > 100000000:
            #print(c)
    ax.plot([i for i in displayJSON],[displayJSON[i] for i in displayJSON])
plt.xticks(np.arange(1999,2019),rotation=45)
plt.show()'''

countryList = ['World','Arab World','Egypt Arab Rep.','Germany','Saudi Arabia','Turkey',]
