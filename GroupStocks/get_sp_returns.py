import pandas as pd
import requests
import logging
from argparse import ArgumentParser
import random
import time
from retry import retry

def get_args():
    ''' Handle Argument parsing'''

    parser = ArgumentParser()
    parser.add_argument('--year', required=True)
    parser.add_argument('--key', required=True, help='Alpha Vantage Key')
    parser.add_argument('--stocks', required=False, help='Number of Stocks')
    parser.add_argument('--start', required=False, help='Only use if mode is Sequential')
    parser.add_argument('--mode', required=True, choices=['Random', 'Sequential'])
    parser.add_argument('--output', required=False, help='output csv will sp500_returns_{}.csv')

    args = parser.parse_args()

    if args.stocks:
        stocks = int(args.stocks)
    else:
        stocks = args.stocks

    return args.year, args.key, stocks, args.mode, int(args.start) if args.start else 0, args.output


class CustomError(Exception):
    pass


def form_output(year):
    ''' Create the template for the output datafrmae'''
    
    return pd.date_range(
        start = f'{year}-01-01',
        end = f'{year}-12-31',
        freq = 'B',
        name = 'Date'
    ).to_frame().reset_index(drop=True)


def pick_symbols(no_stocks, mode, start):
    ''' Pick random symbols from the list of S&P 500 stocks'''

    sp_500 = pd.read_csv('s&p.csv')[['Symbol', 'Sector']].to_dict(orient='records')

    if no_stocks and mode=='Random':
        return random.choices(sp_500, k=no_stocks)
    elif no_stocks and mode=='Sequential':
        return sp_500[start:start+no_stocks]
    else:
        return sp_500

@retry(CustomError, tries=2, delay=120) # Should handle limit requests
def get_returns(sym, sec, key):
    ''' Calculate returns of stock from data pulled from Alpha Vantage'''
    
    stk = f'{sym}_{sec}'
    logging.info(f'Getting Prices for {sym}')
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={sym}&outputsize=full&apikey={key}'
    r = requests.get(url)
    r.raise_for_status()

    if list(r.json().keys())[0] == 'Error Message':
        logging.info(f'{sym} does not exist, SKIPPING')
        return pd.DataFrame()
    elif list(r.json().keys())[0] == 'Note':
        raise CustomError
    else:
        df = pd.DataFrame.from_dict(r.json()['Time Series (Daily)'], orient='index')
        df[stk] = df['4. close'].astype('float64').pct_change()
        df = df.reset_index().rename(columns={'index': 'Date'})
        df.Date = pd.to_datetime(df.Date)
        return df[['Date', stk ]]


if __name__ == "__main__":

    logging.basicConfig(
        format='%(asctime)s:%(levelname)s: - %(message)s',
        level=logging.INFO
    )
    
    year, key, no_stocks, mode, start, file_ext = get_args()
    if file_ext:
        filename = f'sp500_returns_{file_ext}.csv'
    else:
        filename = 'sp500_returns.csv'
    output = form_output(year)
    symbols = pick_symbols(no_stocks, mode, start)
    
    for sym in symbols:
        rtn = get_returns(sym['Symbol'], sym['Sector'], key)
        if rtn.empty:
            continue
        else:
            output = output.merge(rtn, on='Date', how='left')
            output.fillna(0).to_csv(filename, index=False)
    
    logging.info('Written file to csv')
    

    

    
