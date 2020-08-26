from os import listdir
from os.path import isdir, isfile, dirname, abspath
from os import mkdir
from csv import reader
from matplotlib import pyplot as plt
from numpy import arange, ceil, shape, array, reshape

stocks_dict = {
    'aal': 'american airlines',
    'aapl': 'apple',
    'amd': 'amd',
    'amzn': 'amazon',
    'ba': 'boeing',
    'bac': 'bank of america',
    'ccl': 'carnival',
    'f': 'ford',
    'fb': 'facebook',
    'ge': 'general electric',
    'goog': 'google',
    'intc': 'intel',
    'msft': 'microsoft',
    'nflx': 'netflix',
    'nvda': 'nvidia',
    't': 'att',
    'tsla': 'tesla',
    'twlo': 'twilio',
    'twtr': 'twitter',
    'wfc': 'wells fargo'
}

stocks_file = dirname(abspath(__file__)) + "/Live Data/"
live_data_file = dirname(abspath(__file__)) + "/Live Data/"


def write_csv(file: str, data: list):
    final_data = ""
    for line in data:
        for point in line:
            if line.index(point) == 0:
                final_data += point
            else:
                final_data += (',' + point)
        final_data += ('\n')

    with open(file, 'w+') as open_file:
        open_file.write(final_data)


def read_csv(file: str):
    with open(file, 'r') as open_file:
        csv_reader = reader(open_file)
        write_data = []
        for line in csv_reader:
            write_data.append(line)
    return write_data


def remove_column(name: str):
    company_directory = listdir(stocks_file)

    for company in company_directory:
        day_directory = listdir(stocks_file + company)
        for day in day_directory:
            print(company + "/" + day)
            with open(stocks_file + company + "/" + day, 'r') as open_file:
                csv_reader = reader(open_file)
                write_data = []
                header_to_remove = -1
                for line in csv_reader:
                    if str(line).__contains__('Date'):
                        # header_to_remove = line.index(name, -1)
                        header_to_remove = line.index(name)
                    if header_to_remove < 0:
                        raise Exception(f'{name} is not a legal header name')
                    write_data.append(line[:header_to_remove] + line[header_to_remove + 1:])
            write_csv(stocks_file + company + "/" + day, write_data)


def add_column(name: str, data: list, file: str):
    with open(file, 'r') as open_file:
        write_data = []
        csv_reader = reader(open_file)
        csv_length = 0
        reader_index = 0
        for line in csv_reader:
            if csv_length == 0:
                write_data.append(line + [name])
            else:
                write_data.append(line + [data[reader_index]])
                reader_index += 1
            csv_length += 1

    if len(data) != csv_length - 1:
        raise Exception('Please check input sizes.')

    write_csv(file, write_data)


def add_percent_change(minutes: int):
    company_directory = listdir(stocks_file)
    for company in company_directory:
        day_directory = listdir(stocks_file + company)
        for day in day_directory:
            print(company + "/" + day)
            day_dataset = read_csv(stocks_file + company + "/" + day)
            price_index = -1
            for line in day_dataset:
                if str(line).__contains__('Price'):
                    price_index = line.index('Price')
                if price_index < 0:
                    raise Exception('Please check column \'price\'')
            change_list = []
            change_list += [str(0)] * minutes
            for index in range(1 + minutes, len(day_dataset)):
                percent_change = 100 * ((float(day_dataset[index][price_index]) - float(day_dataset[index - minutes][price_index])) / float(day_dataset[index - minutes][price_index]))
                change_list.append(str(percent_change))
            add_column(str(minutes) + "-minute Percent Change", change_list, stocks_file + company + "/" + day)


def change_header_name(original: str, new: str):
    company_directory = listdir(stocks_file)
    for company in company_directory:
        day_directory = listdir(stocks_file + company)
        for day in day_directory:
            day_dataset = read_csv(stocks_file + company + "/" + day)
            day_dataset[0][day_dataset[0].index(original)] = new
            write_csv(stocks_file + company + "/" + day, day_dataset)


def display_day(file: str):
    day_dataset = read_csv(file)

    price_index = -1
    line = day_dataset[0]
    if str(line).__contains__('Price'):
        price_index = line.index('Price')
        titles = line[price_index:]
    if price_index < 0:
        raise Exception('Please check column \'price\'')
    plot_data = []
    for minute in day_dataset[1:]:
        plot_data.append(minute[price_index:])
    for category in range(len(titles)):
        plot_y = []
        plot_sum = 0
        for data_point in plot_data:
            plot_y.append(float(data_point[category]))
            plot_sum += float(data_point[category])
        average = plot_sum / len(plot_data)
        plt.subplot(ceil(len(titles) / 2), 2, category + 1)
        plt.plot(arange(0, len(plot_y)), plot_y)
        plt.legend([titles[category]])
        if min(plot_y) < 0:
            plt.plot(arange(0, len(plot_y)), [0] * len(plot_y), dashes=[4, 2])
            plt.legend([titles[category]] + ['Zero'])
        plt.yticks(arange((min(plot_y)), (max(plot_y)), step=((max(plot_y) - min(plot_y)) / 5 - 0.01)))
    plt.show()


def display_price(file: str, per_minute: int):
    day_dataset = read_csv(file)

    price_index = -1
    line = day_dataset[0]
    if str(line).__contains__('Price'):
        price_index = line.index('Price')
        titles = line[price_index:]
    if price_index < 0:
        raise Exception('Please check column \'price\'')
    plot_data = []
    for minute in day_dataset[1:]:
        plot_data.append(minute[price_index])
    plot_y = []
    plot_x = []
    plot_sum = 0
    for data_point in range(len(plot_data)):
        if data_point % per_minute == 0:
            plot_x.append(data_point)
            plot_y.append(float(plot_data[data_point]) + 0)
            plot_sum += float(plot_data[data_point])
    average = plot_sum / len(plot_data)
    plt.pause(1)
    plt.plot(plot_x, plot_y)
    plt.legend(['Price'])
    plt.yticks(arange((min(plot_y)), (max(plot_y)), step=((max(plot_y) - min(plot_y)) / 5 - 0.01)))
    plt.show()
    return plot_x, plot_y


def identify_extrema(minutes: int, verbose: int, day_dataset=None, file: str=None):
    if day_dataset == None:
        day_dataset = read_csv(file)

    price_index = -1
    line = day_dataset[0]
    if str(line).__contains__('Price'):
        price_index = line.index('Price')
        titles = line[price_index:]
    if price_index < 0:
        raise Exception('Please check column \'price\'')
    plot_data = []
    for minute in day_dataset[1:]:
        plot_data.append(minute[price_index])
    plot_y = []
    plot_x = []
    for data_point in range(len(plot_data)):
        plot_x.append(data_point)
        plot_y.append(float(plot_data[data_point]))

    maxima_x, minima_x, maxima_y, minima_y = [], [], [], []
    for point in range(len(plot_y) - minutes):
        extrema = 'undetermined'
        for neighbors in range(minutes):
            if extrema == 'undetermined':
                if plot_y[point] < plot_y[point + 1]:
                    extrema = 'increasing'
                elif plot_y[point] > plot_y[point + 1]:
                    extrema = 'decreasing'
                else:
                    break
            else:
                if extrema == 'increasing' and plot_y[point + neighbors] >= plot_y[point + neighbors + 1]:
                    extrema = 'undetermined'
                    break
                if extrema == 'decreasing' and plot_y[point + neighbors] <= plot_y[point + neighbors + 1]:
                    extrema = 'undetermined'
                    break
        if extrema == 'increasing':
            minima_x.append(plot_x[point + minutes // 2])
            minima_y.append(plot_y[point + minutes // 2])
        if extrema == 'decreasing':
            maxima_x.append(plot_x[point + minutes // 2])
            maxima_y.append(plot_y[point + minutes // 2])

    return maxima_x, maxima_y, minima_x, minima_y, len(day_dataset) - 1, plot_data


def add_decisions():
    for company in listdir(stocks_file):
        for day in listdir(stocks_file + company):
            maxima_x, maxima_y, minima_x, minima_y, length, prices = identify_extrema(stocks_file + company + '/' + day, 2, 0)
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
                if decisions[price] == 'buy':
                    buy.append(float(point))
                    buy_x.append(price)
                elif decisions[price] == 'sell':
                    sell.append(float(point))
                    sell_x.append(price)
                elif decisions[price] == 'hold':
                    hold.append(float(point))
                    hold_x.append(price)
                else:
                    raise Exception('Problem with decisions. Check array.')
            add_column('Decision', decisions, stocks_file + company + '/' + day)
            print(stocks_file + company + '/' + day)


def get_dataset(company_name: str):
    company_directory = stocks_file + company_name + "/"
    company_files = listdir(company_directory)
    company_files.sort()
    dataset = []
    for file in company_files:
        data = read_csv(company_directory + file)[1:]
        for index in range(len(data)):
            line = data[index]
            if line[-1] == 'sell':
                data[index][-1] = '-1'
            elif line[-1] == 'hold':
                data[index][-1] = '0'
            elif line[-1] == 'buy':
                data[index][-1] = '1'
            dataset.append(line)
    return dataset


def get_split_dataset_all():
    dataset = []
    for company in listdir(stocks_file):
        dataset.append(get_split_dataset_individual(company))


def get_split_dataset_individual(company_name: str):
    dataset = get_dataset(company_name)
    features, labels = [], []
    for data in dataset:
        features.append([float(number) for number in data[:-1]])
        labels.append(int(data[-1]))
    return features, labels


def get_split_live_dataset_individual(company_name: str):
    dataset = get_test_dataset(company_name)
    features, labels = [], []
    for data in dataset:
        try:
            features.append([float(number) for number in data[:-1]])
        except:
            print(data)
        labels.append(int(data[-1]))
    return features, labels


def data_reshape(X_train, y_train, X_test, y_test):
    return reshape(array(X_train), (shape(X_train)[0], shape(X_train)[1], 1)), reshape(array(y_train), (shape(y_train)[0], 1)), reshape(array(X_test), (shape(X_test)[0], shape(X_test)[1], 1)), reshape(array(y_test), (shape(y_test)[0], 1))


def data_prep(company_name: str):
    dataset_features, dataset_labels = get_split_dataset_individual(company_name)
    features, labels = [], []
    feature_dataset, label_dataset = [], []
    day = None
    minute = 0.0
    for index in range(len(dataset_features)):
        feature = dataset_features[index]
        if day == None:
            day = feature[0]
        if feature[0] == day:
            feature_dataset.append(feature[1:])
            label_dataset.append(dataset_labels[index])
            minute += 1
        else:
            minute = 0.0
            features += feature_dataset
            labels += label_dataset
            feature_dataset.clear()
            label_dataset.clear()
            feature_dataset.append(feature[1:])
            label_dataset.append(dataset_labels[index])
            day = feature[0]
    return array(features), array(labels)


def change_time_format():
    company_directory = listdir(stocks_file)
    for company in company_directory:
        day_directory = listdir(stocks_file + company)
        for day in day_directory:
            print(company + "/" + day)
            day_dataset = read_csv(stocks_file + company + "/" + day)
            time_index = -1
            time = 0
            for line in day_dataset:
                if str(line).__contains__('Time'):
                    time_index = line.index('Time')
                if time_index < 0:
                    raise Exception('Please check column \'time\'')
                if time > 0:
                    line[time_index] = str(time - 1)
                time += 1
            write_csv(stocks_file + company + "/" + day, day_dataset)
    change_header_name('Time', 'Minutes Since Open')


def split_by_day():
    company_directory = listdir(stocks_file)
    for company in company_directory:
        if not isdir(stocks_file + company):
            mkdir(stocks_file + company)
        for file in listdir(stocks_file + company):
            day_data = []
            current_day = ""
            data = read_csv(stocks_file + company + "/" + file)
            date_index = -1
            for line in data:
                if date_index > -1 and line != []:
                    date = line[date_index].split(' ')[0]
                    time = line[date_index].split(' ')[1]
                    del line[date_index]
                    line.insert(date_index, date)
                    line.insert(date_index, time)
                    file_name = date.replace('.', '_')
                    if current_day == "":
                        current_day = date
                    if date != current_day:
                        if not isfile(stocks_file + company + "/" + file_name):
                            print(company + "/" + file_name)
                            write_csv(stocks_file + company + "/" + file_name + ".csv", day_data)
                        day_data.clear()
                        day_data.append(line)
                        current_day = date
                    else:
                        day_data.append(line)

                if str(line).__contains__('Date'):
                    date_index = line.index('Date')
                if date_index < 0:
                    raise Exception('Please check column \'date\'')


def switch_columns(column1: str, column2: str):
    company_directory = listdir(stocks_file)
    for company in company_directory:
        if not isdir(stocks_file + company):
            mkdir(stocks_file + company)
        for file in listdir(stocks_file + company):
            day_data = []
            column1_index, column2_index = -1, -1
            data = read_csv(stocks_file + company + "/" + file)
            for line in data:
                if str(line).__contains__('Date'):
                    column1_index = line.index(column1)
                    column2_index = line.index(column2)
                if column1_index < 0:
                    raise Exception('check for ' + column1)
                if column2_index < 0:
                    raise Exception('check for ' + column2)
                print(line)
                new_column1 = line[column2_index]
                new_column2 = line[column1_index]

                while new_column1.__contains__('.'):
                    new_column1 = new_column1.replace('.', '')
                    # print(new_column1)

                while new_column2.__contains__('.'):
                    new_column2 = new_column2.replace('.', '')
                    # print(new_column2)

                del line[column1_index]
                if new_column1.__contains__('.'):
                    break
                line.insert(column1_index, new_column1)

                del line[column2_index]
                if new_column1.__contains__('.'):
                    break
                line.insert(column2_index, new_column2)
                print(line)
                day_data.append(line)
            write_csv(stocks_file + company + "/" + file, day_data)



