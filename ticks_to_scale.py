import os
import optparse
import sys

from datetime import datetime

import pandas as pd


def to_csv(df):
    return df.to_csv(header=None, date_format = '%Y-%m-%d %H:%M:%S', float_format='%.05f')


def main():
    parser = optparse.OptionParser(usage='Usage: python {} [options] <ticks csv file> <time scale: 1min, 1H>'.format(os.path.basename(__file__)))
    parser.add_option('-d', action="store", metavar='output_dir', dest="d", default='.', help="output directory.")

    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        exit(1)

    ticks_file = args[0]
    time_scale = args[1]

    output_dir = options.d
    output_suffix = f'_{time_scale}'

    file_name_ext = os.path.basename(ticks_file).split('.')
    file_name = file_name_ext[0]
    file_ext = f'.{file_name_ext[1]}' if len(file_name_ext) > 1 else ''
    output_csv = f'{output_dir}/{file_name}{output_suffix}{file_ext}'

    df_prev = None

    df_chunks = pd.read_csv(
        ticks_file,
        index_col='Date',
        names=['Date', 'Ask', 'Bid', 'AskVolume', 'BidVolume'],
        dtype={'Date': 'object', 'Ask': 'float', 'Bid': 'float', 'AskVolume': 'int', 'BidVolume': 'int'},
        usecols=['Date', 'Bid'],
        parse_dates=['Date'],
        infer_datetime_format=True,
        chunksize=10**6)

    with open(output_csv, 'w') as f:
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
                df_ohlcv = df_ohlc.assign(Volume=df_prev.iloc[:, 0].resample(time_scale).count())
                f.write(to_csv(df_ohlcv))
                df_prev = df_future_month

        if df_prev.size > 0:
            df_ohlc = df_prev.resample(time_scale).ohlc()
            df_ohlcv = df_ohlc.assign(Volume=df_prev.iloc[:, 0].resample(time_scale).count())
            f.write(to_csv(df_ohlcv))


if __name__ == '__main__':
    main()
