import os
import sys
import csv
import datetime
import datetime as dt
from fpdf import FPDF, YPos, XPos

startTime = dt.datetime.now()
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

fn = sys.argv[1]
if os.path.exists(fn):
    ROOT_DIR = os.path.dirname(fn)
    print(os.path.basename(fn))
else:
    print("Invalid file path")
    sys.exit()

if os.path.join(ROOT_DIR, 'TRADE.csv'):
    print("TRADE.csv exists")
else:
    print("TRADE.csv does not exist")
    sys.exit()

if os.path.join(ROOT_DIR, 'EX_TRADE.csv'):
    print("EX_TRADE.csv exists")
else:
    print("EX_TRADE.csv does not exist")
    sys.exit()

totalValueOfBuyTrades: float = 0
totalValueOfSellTrades: float = 0
lengthOfLongestComment: int = 0
longestComment: str = ''
firstTradeStartTime: datetime = ''
lastTradeStartTime: datetime = ''
firmsWithTradeVolume: {str: float} = {}

with open(os.path.join(ROOT_DIR, 'TRADE.csv'), 'r') as file:
    csvreader = csv.reader(file)
    tradeHeader = next(csvreader)
    tradeRecords = [row for row in csvreader]

tradeCount: int = len(tradeRecords)
for row in tradeRecords:
    if len(row[7]) > lengthOfLongestComment:
        lengthOfLongestComment = len(row[7])
        longestComment = row[7]
    if row[0] < firstTradeStartTime or firstTradeStartTime == '':
        firstTradeStartTime = row[0]
    if row[0] > lastTradeStartTime or lastTradeStartTime == '':
        lastTradeStartTime = row[0]
    if row[2] in firmsWithTradeVolume:
        firmsWithTradeVolume[row[2]] += float(row[3]) * float(row[4])
    if row[2] not in firmsWithTradeVolume:
        firmsWithTradeVolume[row[2]] = float(row[3]) * float(row[4])
    if row[1] == 'B':
        totalValueOfBuyTrades += float((row[3])) * float((row[4]))
    elif row[1] == 'S':
        totalValueOfSellTrades += float((row[3])) * float((row[4]))

with open(os.path.join(ROOT_DIR, 'EX_TRADE.csv'), 'r') as file:
    csvreader = csv.reader(file)
    exTradeHeader = next(csvreader)
    exTradeRecords = [row for row in csvreader]

exTradeCount: int = len(exTradeRecords)
for row in exTradeRecords:
    if row[1] < firstTradeStartTime or firstTradeStartTime == '':
        firstTradeStartTime = row[1]
    if row[1] > lastTradeStartTime or lastTradeStartTime == '':
        lastTradeStartTime = row[1]
    if row[3] in firmsWithTradeVolume:
        firmsWithTradeVolume[row[3]] += float(row[4]) * float(row[5])
    if row[3] not in firmsWithTradeVolume:
        firmsWithTradeVolume[row[3]] = float(row[4]) * float(row[5])
    if row[2] == 'BUY_':
        totalValueOfBuyTrades += float((row[4])) * float((row[5]))
    elif row[2] == 'SELL':
        totalValueOfSellTrades += float((row[4])) * float((row[5]))

datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'
firstTradeStartTime: datetime = dt.datetime.strptime(firstTradeStartTime, datetimeFormat)
lastTradeStartTime: datetime = dt.datetime.strptime(lastTradeStartTime, datetimeFormat)
tradeInterval = (lastTradeStartTime - firstTradeStartTime).total_seconds()

totalNumberOfUniqueIds = len(firmsWithTradeVolume)

pdf = FPDF('P', 'mm', 'A4')
pdf.add_page()
pdf.add_font('Mono', '', ROOT_DIR + '/fonts/monospace.medium.ttf')
pdf.set_font('Mono', '', 20)
pdf.cell(0, 10, 'Trade Summary', new_x=XPos.CENTER, new_y=YPos.NEXT)
pdf.set_font('Mono', '', 14)
pdf.cell(0, 10, 'Number of trades: ' + str(tradeCount), new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.cell(0, 10, 'Number of ex trades: ' + str(exTradeCount), new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.cell(0, 10, 'Total value of buy trades: ' + str(totalValueOfBuyTrades), new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.cell(0, 10, 'Total value of sell trades: ' + str(totalValueOfSellTrades), new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.cell(0, 10, 'Length of longest comment: ' + str(lengthOfLongestComment), new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.cell(0, 10, 'Longest comment: ' + longestComment, new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.cell(0, 10, 'Trade interval: ' + str(tradeInterval) + ' seconds', new_x=XPos.LMARGIN, new_y=YPos.NEXT)
pdf.ln(5)
pdf.set_font('Mono', '', 20)
pdf.cell(0, 10, 'List of Firms', new_x=XPos.CENTER, new_y=YPos.NEXT)
pdf.set_font('Mono', '', 14)
pdf.cell(0, 10, 'Total number of unique firms: ' + str(totalNumberOfUniqueIds), new_x=XPos.LEFT, new_y=YPos.NEXT)
for firm in firmsWithTradeVolume:
    pdf.cell(0, 10, str(firm), new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.ln(5)
pdf.set_font('Mono', '', 20)
pdf.cell(0, 10, 'Firm Summary', new_x=XPos.CENTER, new_y=YPos.NEXT)
pdf.set_font('Mono', '', 14)
pdf.cell(0, 10, 'Firm Name   : Trade Volume', new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.cell(0, 10, '--------------------------------', new_x=XPos.LEFT, new_y=YPos.NEXT)
for firm in firmsWithTradeVolume:
    pdf.cell(0, 10, firm + ': ' + str(firmsWithTradeVolume[firm]), new_x=XPos.LEFT, new_y=YPos.NEXT)
pdf.output('report.pdf')

print("Execution Completed")
print("Execution Time: " + str((dt.datetime.now() - startTime).total_seconds()) + " seconds")
