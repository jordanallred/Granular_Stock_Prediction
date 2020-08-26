from alpha_vantage.timeseries import TimeSeries
from Data_Utils import stocks_dict, write_csv, read_csv, add_column, identify_extrema
from os import listdir, mkdir, remove, removedirs
from os.path import isdir, dirname, abspath
from shutil import copy
from time import time, sleep
from datetime import datetime

stocks_file = dirname(abspath(__file__)) + "/Live Data/"
download_file = dirname(abspath(__file__)) + "/Live Data Download/"


def stockchart(symbol):
    ts = TimeSeries(key=premium_key, output_format='pandas')
    data, meta_data = ts.get_intraday(symbol=symbol, interval='1min')
    print(data)
    date = []
    time = []
    from datetime import time as dt
    for info in data.axes[0]:
        if dt(hour=9, minute=30) <= info.time() <= dt(hour=16):
            date.append(str(info.date()))
            time.append(('0' + str(info.hour) if info.hour < 10 else str(info.hour)) +
                        ('0' + str(info.minute) if info.minute < 10 else str(info.minute)))

    date.reverse()
    time.reverse()

    close = list(data['4. close'])
    volume = list(data['5. volume'])
    write_data = [['Date', 'Time', 'Price', 'Volume']]
    check_date = date[0]
    for index in range(len(date)):
        if date[index] != check_date:
            if not isdir(download_file):
                mkdir(download_file)

            if not isdir(download_file + stocks_dict[symbol]):
                mkdir(download_file + stocks_dict[symbol])

            write_csv(download_file + stocks_dict[symbol] + "/" +
                      check_date.replace('-', '_') + ".csv", write_data)
            write_data.clear()
            write_data.append(['Date', 'Time', 'Price', 'Volume'])
            write_data.append([check_date.replace('-', ''), time[index].strip(':'),
                               str(close[index]), str(volume[index])])
            check_date = date[index]
        else:
            write_data.append([check_date.replace('-', ''), time[index].strip(':'),
                               str(close[index]), str(volume[index])])


def download_historical_data(max_tries = 10):
    failure = True
    stock_keys = list(stocks_dict.keys())
    tries = 0
    while failure:
        failure = False
        remove_keys = []
        start = time()
        for download_number, symbol in enumerate(stock_keys):
            if (download_number + 1) % downloads_per_minute == 0:
                download_time = time() - start
                if download_time < 60:
                    sleep(60 - download_time)
                start = time()
            download = True
            try:
                stockchart(symbol)
            except KeyError:
                download = False
                failure = True
                continue
            finally:
                if download:
                    remove_keys.append(symbol)
                print("Downloading " + symbol.upper() + (" successful" if download else " failed"))
        for to_remove in remove_keys:
            stock_keys.remove(to_remove)
        tries += 1
        if tries == max_tries:
            break

    add_percent_change(1)
    add_percent_change(5)
    add_percent_change(15)
    add_percent_change(30)
    add_percent_change(60)
    add_decisions()

    if not isdir(stocks_file):
        mkdir(stocks_file)
    for directory in listdir(download_file):
        if not isdir(download_file + directory):
            continue
        if not isdir(stocks_file + directory):
            mkdir(stocks_file + directory)
        for file in listdir(download_file + directory):
            copy(download_file + directory + "/" + file, stocks_file + directory + "/" + file)
            remove(download_file + directory + "/" + file)
        removedirs(download_file + directory)


def add_percent_change(minutes: int):
    company_directory = listdir(download_file)
    for company in company_directory:
        if not isdir(download_file + company):
            continue
        day_directory = listdir(download_file + company)
        for day in day_directory:
            day_dataset = read_csv(download_file + company + "/" + day)
            price_index = -1
            for line in day_dataset:
                if str(line).__contains__('Price'):
                    price_index = line.index('Price')
                if price_index < 0:
                    print('check for price')
                    exit(-1)
            change_list = []
            change_list += [str(0)] * minutes
            for index in range(1 + minutes, len(day_dataset)):
                percent_change = 100 * ((float(day_dataset[index][price_index]) -
                                         float(day_dataset[index - minutes][price_index])) /
                                        float(day_dataset[index - minutes][price_index]))
                change_list.append(str(percent_change))
            add_column(str(minutes) + "-minute Percent Change", change_list, download_file + company + "/" + day)


def add_decisions():
    for company in listdir(download_file):
        if not isdir(download_file + company):
            continue
        for day in listdir(download_file + company):
            maxima_x, maxima_y, minima_x, minima_y, length, prices = \
                identify_extrema(download_file + company + '/' + day, 2, 0)
            decisions = []
            for point in range(length):
                if minima_x.__contains__(point):
                    decisions.append('buy')
                elif maxima_x.__contains__(point):
                    decisions.append('sell')
                else:
                    decisions.append('hold')

            buy, sell, hold = [], [], []
            buy_x, sell_x, hold_x = [], [], []
            for price in range(len(prices)):
                point = prices[price]
                if decisions[price] is 'buy':
                    buy.append(float(point))
                    buy_x.append(price)
                elif decisions[price] is 'sell':
                    sell.append(float(point))
                    sell_x.append(price)
                elif decisions[price] is 'hold':
                    hold.append(float(point))
                    hold_x.append(price)
                else:
                    print('Problem with decisions. Check array.')
                    exit(-1)
            add_column('Decision', decisions, download_file + company + '/' + day)


def live_stock_data(symbol: str):
    response = api.get("https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/" + symbol.upper() + "?apiKey=" + polygon_key).json()
    return {
        'price': response['ticker']['lastTrade']['p'],
        'volume': response['ticker']['day']['v']
    }


def collect_live_data():
    def live_percent_change(minutes: int, write_data: list):
        price_index = None
        for line in write_data:
            if str(line).__contains__('Price'):
                price_index = line.index('Price')
                break
            if price_index is None:
                raise Exception("There is no price column in write data.")

        index = len(write_data) - 1
        if index <= minutes:
            percent_change = 0
        else:
            percent_change = 100 * ((float(write_data[index][price_index]) -
                                     float(write_data[index - minutes][price_index])) /
                                    float(write_data[index - minutes][price_index]))
        return percent_change

    def live_add_decisions(write_data: list):
        maxima_x, maxima_y, minima_x, minima_y, length, prices = \
            identify_extrema(day_dataset=write_data, minutes=2, verbose=0)
        decisions = []
        for point in range(length):
            if minima_x.__contains__(point):
                decisions.append('buy')
            elif maxima_x.__contains__(point):
                decisions.append('sell')
            else:
                decisions.append('hold')


    start_volume = {}
    write_data = {}
    stock_keys = list(stocks_dict.keys())
    minute = datetime.now().minute.real
    for symbol in stock_keys:
        data = live_stock_data(symbol)
        start_volume[symbol] = data['volume']
        write_data[symbol] = [['Date', 'Time', 'Price', 'Volume', '1-minute Percent Change', '5-minute Percent Change',
                       '15-minute Percent Change', '30-minute Percent Change', '50-minute Percent Change']]

    while True:
        if datetime.now().minute.real != minute:
            for symbol in stock_keys:
                data = live_stock_data(symbol)
                date = datetime.now().strftime('%Y%m%d')
                time = datetime.now().strftime('%H%M')
                price = str(data['price'])
                volume = str(start_volume[symbol] - data['volume'])
                write_data[symbol].append([date, time, price, volume])
                write_data[symbol][-1].append(str(live_percent_change(1, write_data[symbol])))
                write_data[symbol][-1].append(str(live_percent_change(5, write_data[symbol])))
                write_data[symbol][-1].append(str(live_percent_change(15, write_data[symbol])))
                write_data[symbol][-1].append(str(live_percent_change(30, write_data[symbol])))
                write_data[symbol][-1].append(str(live_percent_change(60, write_data[symbol])))
                live_add_decisions(write_data[symbol])
                write_csv(stocks_file + stocks_dict[symbol] + "/" + datetime.now().strftime('%Y_%m_%d') + ".csv", write_data[symbol])
                print(stocks_file + stocks_dict[symbol] + "/" + datetime.now().strftime('%Y_%m_%d') + ".csv")
                start_volume[symbol] = data['volume']
            minute = datetime.now().minute.real
            print()


if __name__ == '__main__':
    collect_live_data()
