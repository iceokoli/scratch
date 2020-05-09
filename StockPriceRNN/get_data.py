from argparse import ArgumentParser

import pandas as pd
import requests


def get_args():
    """ Handle Argument parsing"""

    parser = ArgumentParser()
    parser.add_argument("--key", required=True, help="Alpha Vantage Key")
    parser.add_argument("--stock", required=True, help="Ticker")

    args = parser.parse_args()

    return args.key, args.stock


def get_data(key, stock):
    """ Get Data from Alpha Vantage"""

    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={stock}&outputsize=full&apikey={key}"

    r = requests.get(url)
    r.raise_for_status()

    df = pd.DataFrame.from_dict(r.json()["Time Series (Daily)"], orient="index")

    df.columns = [i.split(" ")[1] for i in df.columns]

    return df


if __name__ == "__main__":

    key, stock = get_args()

    df = get_data(key, stock)

    df.to_csv(f"{stock}.csv")
