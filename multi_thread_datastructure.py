# -*- coding: utf-8 -*-
"""
Created on Thu Jul 30 21:06:59 2015

@author: fantasie
"""
import urllib
import time
import csv

#%%
field_length = 31
field_shift = 1
fields = ['Open', 'Yclose', 'Curprice', 'High', 'Low',\
          'b1', 's1', 'Volume', 'Amount', 'b10', \
          'b11', 'b2', 'b20', 'b3', 'b30',\
          'b4', 'b40', 'b5', 'b50', 's10',\
          's11', 's2', 's20', 's3', 's30',\
          's4', 's40', 's5', 's50', 'Date',\
          'Time']
isField = [False, False, True, False, False,\
            False, False, False, False, False,\
            False, False, False, False, False,\
            False, False, False, False, False,\
            False, False, False, False, False,\
            False, False, False, False, True,\
            True]
            
#ticker = 'sh601006,sh601001'
data_dir = 'Data/'
ticker_file = '75stocks.csv'
#%%
if __name__ == '__main__':
    stocklist_reader = csv.reader(file(data_dir + ticker_file, 'rb')) 
    tickers = ''
    stocklist = []
    for name in stocklist_reader:
        tickers = tickers + name[0] + ','
        stocklist.append(name[0])
    
    header = []
    headerindex = []
    for i in range(field_length):
        if isField[i] == True:
            header.append(fields[i])
            headerindex.append(i)
    start = time.clock()
    
#%%
    record_ll = []
    f = urllib.urlopen("http://hq.sinajs.cn/list=" + tickers)
    print "Request time: ", time.clock() - start
    start = time.clock()
    p = f.read().decode('gbk')
    print "Decoding time: ", time.clock() - start
    start = time.clock()
    b = p.strip().split('\n')
    print "Split time: ", time.clock() - start
    start = time.clock()
    for r in b:
        print r
        s = r.split(',')
        rec = []
        for index in headerindex:
            rec.append(s[index+field_shift])
        record_ll.append(rec)
#        print 'current price: ', rec
    print "Parsing time: ", time.clock() - start
    start = time.clock()
    
#    for i in range(len(stocklist)):
#        writer = csv.writer(open(data_dir + stocklist[i] + '.csv', 'a+b'))
#        if i == 0:
#            writer.writerow(header)
#        writer.writerow(record_ll[i])
#        del writer
#    print "Writing time: ", time.clock() - start
#%%
    end = time.clock()
    print "Writein time: ", end - start

