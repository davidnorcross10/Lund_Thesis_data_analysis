import pandas as pd
import numpy as np
import json

class DataJSON:
    def __init__(self,data):
        self.data = data

    '''def query(self,**kwargs):
        response = self.data
        for key, value in kwargs.items():
            response = [i for i in response if i[key] == value]
        return response[0]['Value']'''

    #def common_keys(self,data2,*args):
        #indices = [[element[i] for i in element if i in args] for element in self.data]
        #indices2 = [[element[i] for i in element if i in args] for element in data2.data]
        #return {'metadata':args,'data':[value for value in indices if value in indices2]}

    def filter(self,**kwargs):
        if 'Subject' in kwargs:
            Subject = kwargs['Subject']
            data = {}
            for LOCATION in [i for i in self.data]:
                data[LOCATION] = {}
                for TIME in self.data[LOCATION]:
                    try:
                        Value = self.data[LOCATION][TIME][Subject]['Value']
                        data[LOCATION][TIME] = {'Value':Value}
                    except:
                        data[LOCATION][TIME] = {'Value':np.nan}
            return DataJSON(data)
        else:
            return self

    def subtract(self,subtrahend):
        difference = {}
        for LOCATION in [i for i in self.data if i in subtrahend.data]:
            difference[LOCATION] = {}
            for TIME in [i for i in self.data[LOCATION] if i in subtrahend.data[LOCATION]]:
                Subject_self = [i for i in self.data[LOCATION][TIME]][0]
                Subject_sub = [i for i in subtrahend.data[LOCATION][TIME]][0]
                try:
                    d = self.data[LOCATION][TIME][Subject_self]['Value'] - subtrahend.data[LOCATION][TIME][Subject_sub]['Value']
                except:
                    d = np.nan
                difference[LOCATION][TIME] = {'Value':d}
        return DataJSON(difference)

    def multiply(self,factor):
        product = {}
        if type(factor) is int or type(factor) is float:
            for LOCATION in [i for i in self.data]:
                product[LOCATION] = {}
                for TIME in [i for i in self.data[LOCATION]]:
                    if 'Value' in self.data[LOCATION][TIME]:
                        self_item_path = self.data[LOCATION][TIME]
                    else:
                        Subject_self = [i for i in self.data[LOCATION][TIME]][0]
                        self_item_path = self.data[LOCATION][TIME][Subject_self]
                    try:
                        d = self_item_path['Value'] * factor
                    except:
                        d = np.nan
                    product[LOCATION][TIME] = {'Value':d}
        else:
            for LOCATION in [i for i in self.data if i in factor.data]:
                product[LOCATION] = {}
                for TIME in [i for i in self.data[LOCATION] if i in factor.data[LOCATION]]:
                    if 'Value' in self.data[LOCATION][TIME]:
                        self_item_path = self.data[LOCATION][TIME]
                    else:
                        Subject_self = [i for i in self.data[LOCATION][TIME]][0]
                        self_item_path = self.data[LOCATION][TIME][Subject_self]

                    if 'Value' in factor.data[LOCATION][TIME]:
                        factor_item_path = factor.data[LOCATION][TIME]
                    else:
                        Subject_fac = [i for i in factor.data[LOCATION][TIME]][0]
                        factor_item_path = factor.data[LOCATION][TIME][Subject_fac]

                    try:
                        d = self_item_path['Value'] * factor_item_path['Value']
                    except:
                        d = np.nan
                    product[LOCATION][TIME] = {'Value':d}
        return DataJSON(product)

    def divide(self,divisor):
        quotient = {}
        if type(divisor) is int or type(divisor) is float:
            for LOCATION in [i for i in self.data]:
                quotient[LOCATION] = {}
                for TIME in [i for i in self.data[LOCATION]]:
                    if 'Value' in self.data[LOCATION][TIME]:
                        self_item_path = self.data[LOCATION][TIME]
                    else:
                        Subject_self = [i for i in self.data[LOCATION][TIME]][0]
                        self_item_path = self.data[LOCATION][TIME][Subject_self]
                    try:
                        d = self_item_path['Value'] / divisor
                    except:
                        d = np.nan
                    quotient[LOCATION][TIME] = {'Value':d}
        else:
            for LOCATION in [i for i in self.data if i in divisor.data]:
                quotient[LOCATION] = {}
                for TIME in [i for i in self.data[LOCATION] if i in divisor.data[LOCATION]]:
                    if 'Value' in self.data[LOCATION][TIME]:
                        self_item_path = self.data[LOCATION][TIME]
                    else:
                        Subject_self = [i for i in self.data[LOCATION][TIME]][0]
                        self_item_path = self.data[LOCATION][TIME][Subject_self]

                    if 'Value' in divisor.data[LOCATION][TIME]:
                        divisor_item_path = divisor.data[LOCATION][TIME]
                    else:
                        Subject_fac = [i for i in divisor.data[LOCATION][TIME]][0]
                        divisor_item_path = divisor.data[LOCATION][TIME][Subject_fac]

                    try:
                        d = self_item_path['Value'] / divisor_item_path['Value']
                    except:
                        d = np.nan
                    quotient[LOCATION][TIME] = {'Value':d}
        return DataJSON(quotient)

    def scale(self,scaler):
        scaled = {}
        for LOCATION in [i for i in self.data]:
            scaled[LOCATION] = {}
            for TIME in [i for i in self.data[LOCATION]]:
                if 'Value' in self.data[LOCATION][TIME]:
                    self_item_path = self.data[LOCATION][TIME]
                else:
                    Subject_self = [i for i in self.data[LOCATION][TIME]][0]
                    self_item_path = self.data[LOCATION][TIME][Subject_self]
                scaled[LOCATION][TIME] = {'Value':self_item_path['Value']*scaler[TIME]}
        return DataJSON(scaled)
        
def read_WB(path):
    WB_to_OECD = {'Country Code':'LOCATION','Country Name':'Country','Indicator Name':'Subject'}

    df = pd.read_csv(path)
    index = df.columns.values
    text_index = []
    year_index = []
    for i in index:
        try:
            int(i)
            year_index.append(i)
        except ValueError:
            text_index.append(i)
    data = {}
    for r in df.iterrows():
        row = r[1]
        if row['Country Code'] not in data:
            data[row['Country Code']] = {}
        for year in year_index:
            if year not in data[row['Country Code']]:
                data[row['Country Code']][year] = {}
            if row['Indicator Name'] not in data[row['Country Code']][year]:
                data[row['Country Code']][year][row['Indicator Name']] = {'Value':row[year]}
    JSONPath = path.split('.')[0] + '.json'
    json.dump(data,open(JSONPath,'w'))
    return DataJSON(data)

def read_OECD(path):
    df = pd.read_csv(path)
    index = df.columns.values
    data = {}
    for r in df.iterrows():
        row = r[1]
        if row['LOCATION'] not in data:
            data[row['LOCATION']] = {}
        if row['TIME'] not in data[row['LOCATION']]:
            data[row['LOCATION']][row['TIME']] = {}
        if 'INDICATOR' in index:
            if row['INDICATOR'] not in data[row['LOCATION']][row['TIME']]:
                data[row['LOCATION']][row['TIME']][row['INDICATOR']] = {'MEASURE':row['MEASURE'],'Value':row['Value']}
        else:
            if row['SUBJECT'] not in data[row['LOCATION']][row['TIME']]:
                data[row['LOCATION']][row['TIME']][row['SUBJECT']] = {'MEASURE':row['MEASURE'],'Value':row['Value']}
    JSONPath = path.split('.')[0] + '.json'
    json.dump(data,open(JSONPath,'w'))
    return DataJSON(data)

def read_JSON(path):
    data = json.load(open(path))
    return DataJSON(data)
