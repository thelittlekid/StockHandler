# -*- coding: utf-8 -*-
"""
Created on Fri Aug 07 10:43:15 2015

@author: fantasie
"""
from Queue import Queue
import urllib
import threading
import time
import datetime
import csv
from os import path

#%% Global Variables
data_dir = 'Data/'
raw_ticker_file = '100stocks_raw.csv' # raw ticker file
ticker_file = '100stocks.csv' # tickers that are available after test
collect_interval = 2 # seconds，can't be 0!
collect_length = 2*60*60 # runs for 2 hours each time 
collect_times = collect_length/collect_interval
write_interval = 20 # pieces of records
# Select Fields you need by setting 'True' in the corresponding position
field_length = 31
field_shift = 1
fields = ['Open', 'Yclose', 'Curprice', 'High', 'Low',\
          'b1', 's1', 'Volume', 'Amount', 'b10', \
          'b11', 'b2', 'b20', 'b3', 'b30',\
          'b4', 'b40', 'b5', 'b50', 's10',\
          's11', 's2', 's20', 's3', 's30',\
          's4', 's40', 's5', 's50', 'Date',\
          'Time'] #http://blog.csdn.net/simon803/article/details/7784682
isField = [False, False, True, False, False,\
            False, False, False, False, True,\
            True, True, False, True, False,\
            True, False, True, False, True,\
            True, True, False, True, False,\
            True, False, True, False, True,\
            True]
extrafields = ['Analyzingtime']
url_prefix = "http://hq.sinajs.cn/list=" # Please don't change this
P_num = 0 #Thread number, please don't change this
C_num = 1
datestring = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime('%Y%m%d')
paramstring = '_' + str(collect_interval) + 's_' + datestring
group_size = 75

#%% Local functions are defined below:
# Read the stock list from local csv file
def readStocklist(t_num):
    # 75 is the limit of stock number, stocklist cannot be larger than 75
    # otherwise the program will be much slower in decoding
    stocklist = csv.reader(file(data_dir + ticker_file, 'rb')) 
    if t_num == P_num: # Producer needs a string of tickers
        tickers_vec = []        
        tickers_component = ''
        count = 0
        for name in stocklist:
            tickers_component = tickers_component + name[0] + ','
            count = count + 1
            if count == group_size:
                tickers_vec.append(tickers_component)
                count = 0
                tickers_component = ''
        if 0 < count < group_size:
            tickers_vec.append(tickers_component)
        return tickers_vec

    elif t_num == C_num: # Consumer needs a list of tickers
        tickerlist = []
        for name in stocklist:
            ticker = name[0]
            if ticker.startswith('sh'):
                ticker = ticker + '.ss'
            elif ticker.startswith('sz'):
                ticker = ticker + '.sz'
            ticker = ticker[2:]
            tickerlist.append(ticker)
        return tickerlist
    else:
        return None
    
# Check the availability of stock universe and generate stock list file
def genActiveStockFile():
    reader = csv.reader(file(data_dir + raw_ticker_file, 'rb'))
    tickers_vec, tickerlist = [], []
    tickers = ''
    count = 0
    for name in reader:
        tickerlist.append(name)
        tickers = tickers + name[0] + ','
        count = count + 1
        if count == group_size:
            tickers_vec.append(tickers)
            tickers, count = '', 0
    if 0 < count < group_size:
        tickers_vec.append(tickers)
        
    actlist = []
    t_index = 0
    for tickers in tickers_vec:
        for i in range(5):
            try:
                f = urllib.urlopen(url_prefix + tickers)
                break;
            except Exception, e:
                print e, "Failed in generating active list, retrying..."
        p = f.read().decode('gbk')
        b = p.strip().split('\n')
        for i in range(len(b)):
            if b[i].find(','):
                actlist.append(tickerlist[i+t_index])
        t_index = t_index + group_size
    writer = csv.writer(open(data_dir + ticker_file, 'wb'))
    writer.writerows(actlist)
    del writer
    print "Active stock list generated!"
    
#%% Thread classes
# Producer thread
class Producer( threading.Thread ):
    def __init__( self, t_name, queue):
        threading.Thread.__init__( self, name = t_name )
        self.data = queue
    def run( self ):
        print "Producer Start"
        tickers_vec = readStocklist(P_num)
        for i in range(collect_times):
            print "Producer:", i
            share_PC = []            
            for tickers in tickers_vec:
                try:
                    f = urllib.urlopen(url_prefix + tickers)
                    share_PC.append(f)
                except Exception, e:
                    print e
                    share_PC.append(0)
            self.data.put(share_PC)
            time.sleep(collect_interval)
            
# Consumer thread
class Consumer( threading.Thread ):
    def __init__(self, t_name, queue, oqueue):
        threading.Thread.__init__(self, name=t_name)
        self.data = [queue, oqueue]
    
    # Get the header/field list
    def getHeader(self):
        header = []
        headerindex = []
        for i in range(field_length):
            if isField[i] == True:
                header.append(fields[i])
                headerindex.append(i) 
        for item in extrafields:
            header.append(item)
        return header, headerindex   
    
    # Formulate the realtime database using python dictionary
    def formRTDB(self, actlist, header):
        record_db = {}
        for stock in actlist:
            if path.exists(data_dir + stock + paramstring + '.csv'):
                record_db[stock] = []
            else:
                record_db[stock] = [header]
        return record_db
    
    # Write the data in to files
    def storeDB(self, record_db):
        for stock in record_db.keys():
            try:
                writer = csv.writer(open(data_dir + stock + paramstring + '.csv', 'a+b'))
                writer.writerows(record_db[stock])
            except Exception, e:
                print e
            record_db[stock][:] = []
        del writer
        print 'data was stored in csv file.'
    
    # Parser for data record
    def dataParser(self, s, headerindex):
        rec = []
        for index in headerindex:
            rec.append(s[index+field_shift])
            analyzetime = time.strftime('%H:%M:%S')
            rec.append(analyzetime)
        return rec
            
    def run(self):
        print "Consumer start"
        tickerlist = readStocklist(C_num)
        header, headerindex = self.getHeader() 
        record_db = self.formRTDB(tickerlist, header) # used for csv writing
        count = 0
        for i in range(collect_times):
            share_PC = self.data[0].get()
            print 'length of share_PC:', len(share_PC)
            share_CA = {}
            f_index = 0
            for f in share_PC:
                try:
                    p = f.read().decode('gbk')
                except Exception, e:
                    print e
                    continue
                rtdata_l = p.strip().split('\n')
                for j in range(len(rtdata_l)):
                    s = rtdata_l[j].split(',')
                    rec = []
                    for index in headerindex:
                        rec.append(s[index+field_shift])
                    analyzetime = time.strftime('%H:%M:%S')
                    rec.append(analyzetime)
                    record_db[tickerlist[j + f_index]].append(rec)
                    share_CA[tickerlist[j + f_index]] = rec
                f_index = f_index + group_size
            self.data[1].put(share_CA)
            count = count + 1
            print "Consumer:", i
            if count == write_interval:
                self.storeDB(record_db)
                count = 0
        print "Consumer finish"

# Analyzer thread
class Analyzer(threading.Thread):
    global stats_header 
    stats_header = ['Decision Time', 'BuyVolume', 'SellVolume']
    def __init__(self, t_name, oqueue):
        threading.Thread.__init__(self, name=t_name)
        self.data = oqueue
    
    def getVolIndices(self):
        buyIndices = []
        sellIndices = []
        SeqNum = 0
        for i in range(field_length):
            if isField[i] == True:                
                if i in [9, 11, 13, 15, 17]:
                    buyIndices.append(SeqNum)
                elif i in [19, 21, 23, 25, 27]:
                    sellIndices.append(SeqNum)
                SeqNum = SeqNum + 1
        return buyIndices, sellIndices
        
    def calcBuySellVol(self, rt_data, buyIndices, sellIndices):
        buyV, sellV = 0, 0
        for i in buyIndices:
            buyV = buyV + int(rt_data[i])
        for i in sellIndices:
            sellV = sellV + int(rt_data[i])
        return buyV, sellV

    def run(self):  
#        stats_db = {}
#        last_data = {}
        buyIndices, sellIndices = self.getVolIndices()
        for i in range(collect_times):
            realtime_data = self.data.get()
            if isinstance(realtime_data, int):
                continue
            for stock in realtime_data.keys():                
                buyVol, sellVol = self.calcBuySellVol(realtime_data[stock], buyIndices, sellIndices)
                decisiontime = time.strftime('%H:%M:%S')                
                rec = [decisiontime, buyVol, sellVol]  
                print stock, ":", rec
#                stats_db[stock].append(rec)
#            last_data = realtime_data
#            if i != 0:
            print 'length of realtime_data:', len(realtime_data)
            print 'Analyzer:', i
        print "%s: %s finished!" % (time.ctime(), self.getName())
            
#%% Main thread
def main():
    start = time.clock()
    queue = Queue()
    oqueue = Queue()   
    producer = Producer('Pro.', queue)
    consumer = Consumer('Con.', queue, oqueue)
    analyzer = Analyzer('Anl.', oqueue)
    genActiveStockFile()
    try:
        producer.start()
        consumer.start()
        analyzer.start()
        producer.join()
        consumer.join()
        analyzer.join()
    except KeyboardInterrupt, e:
        raise e
    print 'All thread terminate!'
    end = time.clock()
    print end - start
    
if __name__ == '__main__':
    main()
    
