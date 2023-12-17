import pandas as pd
import requests
import io
import csv
import os
from datetime import datetime
from logger import *

def test():
    spotname=['BANKNIFTY','NIFTY']
    weekly_expiry_index=[0,0]
    response=requests.get('https://public.fyers.in/sym_details/NSE_FO.csv')
    instruments=pd.read_csv(io.StringIO(response.text),header=None)
    instruments.to_csv('NSE_FO.csv',index=False,header=None)
    wr=csv.writer(open('NSE_FO_Formated.csv','w'))
    for x in range(len(spotname)):
        instruments=pd.read_csv('NSE_FO.csv',header=None)
        instruments=instruments[instruments[13]==spotname[x]]
        if not instruments.empty :
            instruments[8]=pd.to_datetime(instruments[8],unit='s')
            instruments[8]=instruments[8].dt.strftime('%Y-%m-%d')
            wei=instruments.sort_values(by=8).head(1)[8].iloc[weekly_expiry_index[x]]
            instruments=instruments[instruments[8]==wei]
            print(spotname[x],wei)
            instruments.to_csv('NSE_FO_Formated.csv',mode='a',index=False,header=None)

contract_folder = 'contract'
nse_fo_file = 'NSE_FO.csv'
ab_nse_fo_file = 'AB_NSE_FO.csv'


# Create the 'log' folder if it doesn't exist
if not os.path.exists(contract_folder):
    os.makedirs(contract_folder)
fo_path = os.path.join(contract_folder, nse_fo_file)
ab_fo_path = os.path.join(contract_folder, ab_nse_fo_file)

def get_option_info(spotname):
    spot_file = '{}\\NSE_FO_{}.csv'.format(contract_folder,spotname)
    response=requests.get('https://public.fyers.in/sym_details/NSE_FO.csv')
    instruments=pd.read_csv(io.StringIO(response.text),header=None)
    instruments.to_csv(fo_path,index=False)
    wr=csv.writer(open(spot_file,'w'))

    instruments=instruments[instruments[13]==spotname]
    if not instruments.empty : 
        df = pd.DataFrame()       
        instruments[8]=pd.to_datetime(instruments[8],unit='s')
        instruments[8]=instruments[8].dt.strftime('%Y-%m-%d')
        df["expiry_start_date"]  = instruments[7]
        df["expiry_date"]  = instruments[8]
        df["strike_price"] = instruments[15]
        df["option"] = instruments[16]
        df["symbol"] = instruments[9]
        df["symbol_info"] = instruments[1]
        df["spot"] = instruments[13]
        df.to_csv(spot_file)

def get_option_info_ab(spotname):
    spot_file = '{}\\AB_NSE_FO_{}.csv'.format(contract_folder,spotname)
    response=requests.get('https://v2api.aliceblueonline.com/restpy/static/contract_master/NFO.csv')
    instruments=pd.read_csv(io.StringIO(response.text))
    instruments.to_csv(ab_fo_path,index=False)
    wr=csv.writer(open(spot_file,'w'))

    instruments=instruments[instruments['Symbol']==spotname]
    if not instruments.empty : 
        df = pd.DataFrame()       
        df["expiry_date"]  = instruments['Expiry Date']
        df["strike_price"] = instruments['Strike Price']
        df["option"] = instruments['Option Type']
        df["symbol"] = instruments['Trading Symbol']
        df["symbol_info"] = instruments['Formatted Ins Name']
        df["spot"] = instruments['Symbol']
        df["Lot Size"] = instruments['Lot Size']
        df["Token"] = instruments['Token']
        df.to_csv(spot_file)

    
def get_option_details(spotname, broker = "", retry = 0):
    spot_file = '{}\\NSE_FO_{}{}.csv'.format(contract_folder,broker,spotname)
    if os.path.isfile(spot_file):
        print('{} existed.'.format(spot_file))
        df = pd.read_csv(spot_file)
        df = df.sort_values(by="option", key = lambda x: x.map({value: index for index, value in enumerate(['XX', 'CE', 'PE'])}))
        return df
    else :
        if retry > 3:
            print("unable to get the spot price")
            return None
        retry = retry + 1
        print('downloading {}'.format(spot_file))
        if broker == "ab": get_option_info_ab(spotname)
        else : get_option_info(spotname)
        
        return get_option_details(spotname, broker = "", retry=retry)
    

def get_active_options(spotname) :
    df = get_option_details(spotname)
    return df['symbol']

def get_symbol(df):
    dfs = pd.DataFrame()
    dfs['symbol'] = df['symbol']
    dfs['symbol_info'] = df['symbol_info']
    dfs['strike_price'] = df['strike_price']
    dfs['expiry_date'] = df['expiry_date']
    return dfs
    
def get_active_futures(spotname) :
    df = get_option_details(spotname)
    df = df[df['option'] == "XX"]    
    return get_symbol(df)

def nearest_strike(current_price):
    strike = round(current_price / 100) * 100
    return strike

def get_options_by_range(spotname, min_spot, max_spot) :
    df = get_option_details(spotname)
    df = df[df['option'] != "XX"]
    lower_bound = nearest_strike(min_spot) 
    upper_bound = nearest_strike(max_spot)
    print(lower_bound)
    print(upper_bound)
    df = df[(df['strike_price'] >= lower_bound) & (df['strike_price'] <= upper_bound)]
    return get_symbol(df)

def get_options_by_month(spotname, current_month, current_year):
    df = get_option_details(spotname)
    df['expiry_date'] = pd.to_datetime(df['expiry_date'])
    # Filter the DataFrame for the current month
    month_df = df[(df['expiry_date'].dt.month == current_month) & (df['expiry_date'].dt.year == current_year)]    
    return month_df

def get_current_month_options(spotname):
    return get_options_by_month(spotname, datetime.now().month, datetime.now().year)

def get_options_by_month_step(spotname, month_step):
    c_date = datetime.now() + pd.DateOffset(months=month_step)
    return get_options_by_month(spotname, c_date.month, c_date.year)

def get_available_expiries(df):    
    if not df.empty:
        exp = df['expiry_date'].unique()
        return pd.to_datetime(exp).strftime('%Y-%m-%d')
    else:
        print("data frame is empty")
            

if __name__ == '__main__':
    get_option_details("BANKNIFTY", "ab")
    #res = get_active_futures("BANKNIFTY")    
    #print(res)
    #filtered = get_options_by_range("BANKNIFTY",45386.5,48749.2)
    #print(filtered)    
    mdf = get_options_by_month("BANKNIFTY", datetime.now().month, datetime.now().year)
    #print("get_options_by_month:\n{}".format(mdf))
    exp = get_available_expiries(mdf)
    print("get_options_by_month avail expires:\n{}".format(exp))

    mdf = get_current_month_options("BANKNIFTY")
    #print("get_current_month_options:\n{}".format(mdf))    
    exp = get_available_expiries(mdf)
    print("get_current_month_options avail expires:\n{}".format(exp))
    
    mdf = get_options_by_month_step("BANKNIFTY", 0)
    #print("get_options_by_month_step(0):\n{}".format(mdf))
    exp = get_available_expiries(mdf)
    print("get_options_by_month_step(0) avail expires:\n{}".format(exp))
    
    mdf = get_options_by_month_step("BANKNIFTY", 1)
    #print("get_options_by_month_step(1):\n{}".format(mdf))
    exp = get_available_expiries(mdf)
    print("get_options_by_month_step(1) avail expires:\n{}".format(exp))
    
    mdf = get_options_by_month_step("BANKNIFTY", 2)
    #print("get_options_by_month_step(2):\n{}".format(mdf))
    exp = get_available_expiries(mdf)
    print("get_options_by_month_step(2) avail expires:\n{}".format(exp))
    
    mdf = get_options_by_month_step("BANKNIFTY", 3)
    #print("get_options_by_month_step(3):\n{}".format(mdf))
    exp = get_available_expiries(mdf)
    print("get_options_by_month_step(3) avail expires:\n{}".format(exp))
    
    mdf = get_options_by_month_step("BANKNIFTY", 4)
    #print("get_options_by_month_step(4):\n{}".format(mdf))
    exp = get_available_expiries(mdf)
    print("get_options_by_month_step(4) avail expires:\n{}".format(exp))