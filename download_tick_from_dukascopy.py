import lzma
import optparse
import os
import struct
from datetime import datetime, timedelta
from urllib import request
from urllib.error import HTTPError

# 3rd party modules
import pandas as pd


def tokenize(buffer):
    token_size = 20
    token_count = int(len(buffer) / token_size)
    tokens = list(map(lambda x: struct.unpack_from('>3I2f', buffer, token_size * x), range(0, token_count)))
    return tokens


def normalize_tick(symbol, day, time, ask, bid, ask_vol, bid_vol):
    date = day + timedelta(milliseconds=time)

    # TODO 網羅する。この通過ペア以外も有るかも
    if any(map(lambda x: x in symbol.lower(), ['usdrub', 'xagusd', 'xauusd', 'jpy'])):
        point = 1000
    else:
        point = 100000

    return [date, ask/point, bid/point, round(ask_vol * 1000000), round(bid_vol * 1000000)]


# 一日分のtickをDL(DL → decomp → tokenize → normalize)
def download_ticks(symbol, day):
    url_prefix='https://datafeed.dukascopy.com/datafeed'

    ticks_day = []
    for h in range(0, 24):
        file_name = f'{h:02d}h_ticks.bi5'
        url = f'{url_prefix}/{symbol}/{day.year:04d}/{day.month-1:02d}/{day.day:02d}/{file_name}'
        print(f'downloading: {url}')

        req = request.Request(url)
        try:
            with request.urlopen(req) as res:
                res_body = res.read()
        except HTTPError:
            print('download failed. continuing..')
            continue

        try:
            data = lzma.decompress(res_body)
        except lzma.LZMAError:
            print('decompress failed. continuing..')
            continue

        tokenized_data = tokenize(data)
        ticks_hour = list(map(lambda x: normalize_tick(symbol, day + timedelta(hours=h), *x), tokenized_data))
        ticks_day.extend(ticks_hour)

    return ticks_day


def format_to_csv_for_ticks(ticks):
    return '\n'.join(map(lambda x: '{},{},{},{},{}'.format(x[0].strftime('%Y-%m-%d %H:%M:%S.%f'), *x[1:]), ticks))+'\n'


def format_to_csv_for_candle(ticks, scale):
    df = pd.DataFrame(ticks, columns=['Date', 'Ask', 'Bid', 'AskVolume', 'BidVolume'])
    df = df.drop(['Ask', 'AskVolume', 'BidVolume'], axis=1)
    df.set_index('Date', inplace=True)

    df_c = df.resample(scale).ohlc()
    csv_str = df_c.to_csv(header=False, date_format = '%Y-%m-%d %H:%M:%S')

    return csv_str


def main():

    parser = optparse.OptionParser(usage='Usage: python {} [options] <symbol> <start: yyyy-mm-dd> <end: yyyy-mm-dd>'.format(os.path.basename(__file__)))
    parser.add_option('-c', action="store", metavar='time_scale', dest="c", help="candlestick. ex: 1min, 1H, 1D")
    parser.add_option('-d', action="store", metavar='output_dir', dest="d", default='./', help="output directory.")

    (options, args) = parser.parse_args()

    if len(args) < 3:
        parser.print_help()
        exit(1)

    symbol = args[0]
    start_date = datetime.strptime(args[1], '%Y-%m-%d')
    end_date = datetime.strptime(args[2], '%Y-%m-%d')
    output_dir = options.d
    output_suffix = f'_{options.c}' if options.c is not None else ''
    output_csv = f'{output_dir}/{symbol}-{start_date.strftime("%Y-%m-%d")}_{end_date.strftime("%Y-%m-%d")}{output_suffix}.csv'

    d = start_date
    with open(output_csv, 'w') as f:
        while d <= end_date:
            ticks_day = download_ticks(symbol, d)

            if options.c is None:
                f.write(format_to_csv_for_ticks(ticks_day))
            else:
                f.write(format_to_csv_for_candle(ticks_day, options.c))

            d += timedelta(days=1)


if __name__ == '__main__':
    main()
