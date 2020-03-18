# Download tick from Dukascopy
This script downloads tick data from [Dukascopy](https://www.dukascopy.com/swiss/english/home/).
The candlestick csv can be imported by MT4.

## Files
* download_tick_from_dukascopy.py
    * download tick data as...
        * tick
        * candlestick (date format is yyyy-mm-dd hh:mm:ss)


* ticks_to_scale.py (omake)
    * convert tick data csv to candlestick(date_format = 'yyyy-mm-dd hh:mm:ss')


## Prerequisite
* Python3


## Prepare
1. `$ python3 -v venv venv`
1. `$ . venv/bin/activate`
1. `$ pip install -r requirements.txt`


## Usage
```
Usage: python download_tick_from_dukascopy.py [options] <symbol> <start: yyyy-mm-dd> <end: yyyy-mm-dd>

Options:
  -h, --help     show this help message and exit
  -c time_scale  download as candlestick. ex: 1min, 1H, 1D. if not specified, download as tick.
  -d output_dir  output directory. default="./"
```
