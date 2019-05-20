import os
import sys

import pandas as pd


def write_csv(df):
    csv = df.to_csv(header=None, date_format= float_format='%.05f')
    sys.stdout.write(csv)


def main():

    if len(sys.argv) < 3:
        sys.stderr.write('Usage: python {} <ticks csv file> <time scale>\n'.format(os.path.basename(__file__)))
        sys.stderr.write('\ttime series: ex. 1min, 1H, 1D, etcetc...')
        exit(1)

    ticks_file = sys.argv[1]
    time_scale = sys.argv[2]

    df_prev = None

    df_chunks = pd.read_csv(
        ticks_file,
        index_col='Date',
        names=['Date', 'Ask', 'Bid', 'AskVolume', 'BidVolume'],
        dtype={'Date': 'object', 'Ask': 'float', 'Bid': 'float', 'AskVolume': 'int', 'BidVolume': 'int'},
        usecols=['Date', 'Bid'],
        parse_dates=['Date'],
        chunksize=10**5)

    for df in df_chunks:

        if df_prev is None:
            df_prev = df
            continue

        prev_year = df_prev.index[-1].year
        prev_month = df_prev.index[-1].month

        df_same_month = df.get(f'{prev_year}-{prev_month}')

        if df_same_month is not None:
            df_prev = df_prev.append(df_same_month)
            df_future_month = df.drop(df_same_month.index)
        else:
            df_future_month = df

        if df_future_month.size > 0:
            df_ohlc = df_prev.resample(time_scale).ohlc()
            write_csv(df_ohlc)
            df_prev = df_future_month

    if df_prev.size > 0:
        df_ohlc = df_prev.resample(time_scale).ohlc()
        write_csv(df_ohlc)


if __name__ == '__main__':
    main()
