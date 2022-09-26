import os
import sys
import csv
import datetime
import datetime as dt
from fpdf import FPDF, YPos, XPos

startTime = dt.datetime.now()
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
fileDir = os.path.join(ROOT_DIR, 'data')


def main():
    file_dir = get_path()
    if file_dir != "":
        records = get_data(file_dir)
    else:
        records = get_data(fileDir)
    create_pdf(records)


def get_path():
    file_dir = ""
    if len(sys.argv) > 1:
        print("File path entered\n")
        fn = sys.argv[1]
        if os.path.exists(fn):
            file_dir = os.path.dirname(fn)
            print(os.path.basename(fn))
        else:
            print("Invalid file path entered\n--trying with default file path\n\n")
    else:
        print("No file path entered\n--trying with default file path\n\n")
    return file_dir


def get_data(file_dir):
    try:
        with open(os.path.join(file_dir, 'TRADE.csv'), 'r') as file:
            csvreader = csv.reader(file)
            trade_header = next(csvreader)
            trade_records = [row for row in csvreader]

        with open(os.path.join(file_dir, 'EX_TRADE.csv'), 'r') as file:
            csvreader = csv.reader(file)
            ex_trade_header = next(csvreader)
            ex_trade_records = [row for row in csvreader]

    except FileNotFoundError:
        print("CSV files not found at directory: " + file_dir)
        sys.exit()

    return trade_records, ex_trade_records, trade_header, ex_trade_header


def create_pdf(records):
    trade_records = records[0]
    ex_trade_records = records[1]

    total_value_of_buys: float = 0
    total_value_of_sells: float = 0
    length_of_longest_comment: int = 0
    longest_comment: str = ''
    first_trade_start_time: datetime = ''
    last_trade_start_time: datetime = ''
    firms_with_trade_volume: {str: float} = {}

    trade_count: int = len(trade_records)
    for row in trade_records:
        if len(row[7]) > length_of_longest_comment:
            length_of_longest_comment = len(row[7])
            longest_comment = row[7]
        if row[0] < first_trade_start_time or first_trade_start_time == '':
            first_trade_start_time = row[0]
        if row[0] > last_trade_start_time or last_trade_start_time == '':
            last_trade_start_time = row[0]
        if row[2] in firms_with_trade_volume:
            firms_with_trade_volume[row[2]] += float(row[3]) * float(row[4])
        if row[2] not in firms_with_trade_volume:
            firms_with_trade_volume[row[2]] = float(row[3]) * float(row[4])
        if row[1] == 'B':
            total_value_of_buys += float((row[3])) * float((row[4]))
        elif row[1] == 'S':
            total_value_of_sells += float((row[3])) * float((row[4]))

    ex_trade_count: int = len(ex_trade_records)
    for row in ex_trade_records:
        if row[1] < first_trade_start_time or first_trade_start_time == '':
            first_trade_start_time = row[1]
        if row[1] > last_trade_start_time or last_trade_start_time == '':
            last_trade_start_time = row[1]
        if row[3] in firms_with_trade_volume:
            firms_with_trade_volume[row[3]] += float(row[4]) * float(row[5])
        if row[3] not in firms_with_trade_volume:
            firms_with_trade_volume[row[3]] = float(row[4]) * float(row[5])
        if row[2] == 'BUY_':
            total_value_of_buys += float((row[4])) * float((row[5]))
        elif row[2] == 'SELL':
            total_value_of_sells += float((row[4])) * float((row[5]))

    datetime_format = '%Y-%m-%d %H:%M:%S.%f'
    first_trade_start_time: datetime = dt.datetime.strptime(first_trade_start_time, datetime_format)
    last_trade_start_time: datetime = dt.datetime.strptime(last_trade_start_time, datetime_format)
    trade_interval = (last_trade_start_time - first_trade_start_time).total_seconds()

    total_number_of_unique_firms = len(firms_with_trade_volume)

    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.add_font('Mono', '', ROOT_DIR + '/fonts/monospace.medium.ttf')
    pdf.set_font('Mono', '', 20)
    pdf.cell(0, 10, 'Trade Summary', new_x=XPos.CENTER, new_y=YPos.NEXT)
    pdf.set_font('Mono', '', 14)
    pdf.cell(0, 10, 'Number of trades: ' + str(trade_count), new_x=XPos.LEFT, new_y=YPos.NEXT)
    pdf.cell(0, 10, 'Number of ex trades: ' + str(ex_trade_count), new_x=XPos.LEFT, new_y=YPos.NEXT)
    pdf.cell(0, 10, 'Total value of buy trades: ' + str(total_value_of_buys), new_x=XPos.LEFT, new_y=YPos.NEXT)
    pdf.cell(0, 10, 'Total value of sell trades: ' + str(total_value_of_sells), new_x=XPos.LEFT, new_y=YPos.NEXT)
    pdf.cell(0, 10, 'Length of longest comment: ' + str(length_of_longest_comment), new_x=XPos.LEFT, new_y=YPos.NEXT)
    pdf.cell(0, 10, 'Longest comment: ' + longest_comment, new_x=XPos.LEFT, new_y=YPos.NEXT)
    pdf.cell(0, 10, 'Trade interval: ' + str(trade_interval) + ' seconds', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(5)
    pdf.set_font('Mono', '', 20)
    pdf.cell(0, 10, 'List of Firms', new_x=XPos.CENTER, new_y=YPos.NEXT)
    pdf.set_font('Mono', '', 14)
    pdf.cell(0, 10, 'Total number of firms: ' + str(total_number_of_unique_firms), new_x=XPos.LEFT, new_y=YPos.NEXT)
    for firm in firms_with_trade_volume:
        pdf.cell(0, 10, str(firm), new_x=XPos.LEFT, new_y=YPos.NEXT)
    pdf.ln(5)
    pdf.set_font('Mono', '', 20)
    pdf.cell(0, 10, 'Firm Summary', new_x=XPos.CENTER, new_y=YPos.NEXT)
    pdf.set_font('Mono', '', 14)
    pdf.cell(0, 10, 'Firm Name   : Trade Volume', new_x=XPos.LEFT, new_y=YPos.NEXT)
    pdf.cell(0, 10, '--------------------------------', new_x=XPos.LEFT, new_y=YPos.NEXT)
    for firm in firms_with_trade_volume:
        pdf.cell(0, 10, firm + ': ' + str(firms_with_trade_volume[firm]), new_x=XPos.LEFT, new_y=YPos.NEXT)
    pdf.output('report.pdf')

    print("Execution Completed")
    print("Execution Time: " + str((dt.datetime.now() - startTime).total_seconds()) + " seconds")


if __name__ == '__main__':
    main()
