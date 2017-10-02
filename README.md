**Real-time stock data collector

multi_thread.py is a demo of real-time stock price collector.
There are three major classes in this script.
1. Producer: Send request to sina stock server and get response, then put the response into a common queue and share it with Consumer
2. Consumer: Retrieve the real time data from the queue, then decode, split and parse the data and store them into files on disc at interval
3. Analyzer: Real time analyzer, print the sum of buy volume and sell volumn of each stock at each time 
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Before running, please set the values of global variables from line 16 to line 46.
data_dir: directory of data files
raw_ticker_file: path of ticker list file
ticker_file:  designate a path to generate a file that contains the list of available stocks.(This is for the case that not all stocks in raw_ticker_file are supported by sina)
collect_interval: Producer sends consecutive requests at this time interval (in seconds)
collect_length: Total time length of each execution (in seconds). (Two hours each time, from 9:30 to 11:30, 13:00 to 15:00)
collect_times: Number of requests needs to be send
write_interval: Consumer stores the real time data into hard disc after this number of rounds (in rounds)
field_length: Number of stats we can get
field_shift: = 1 since the first element is not needed
fields: To understand the meaning of each field, please refer to http://blog.csdn.net/simon803/article/details/7784682
isField: You can choose to store the data by setting the corresponding position 'True'. Currently 'current price', 'date' and 'time' are selected
extrafields: Additional factor or parameters will be defined in this vector. Note: this is only a convenient structure for developers to further add factors, it shouldn't be changed by users.
datestring: Date in string format, Beijing Time. Do not change this line unless you want to name the csv file in a different way.
paramstring: will be used in naming the csv files. Do not change this line unless you want to name the csv file in a different way.
url_prefix: prefix of request
P_num: thread number of Producer
C_num: thread number of Consumer
group_size: We devide the stock universe into groups, each containing this number of stocks. The purpose of this is to avoid getting responses that are too long to parse. Having no idea about why, 75 seems to be the maximum number of each group that will bring the parsing time lower than 0.01 sec. When the group_size goes to 76, the parsing time goes to around 20 seconds. You can test this using multi_thread_datastructure.py.
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Data Structure:
1. Producer and Consumer share a queue. Producer puts one element into the queue each time after it gets response from the server, and Consumer gets one element each time to parse it. 
After parsing, the piece of record of stock A at time t, denoted by R_At, is a vector of N elements [currentprice, date, time, ... ](N depends on how many factors you selected in isField at from line 32 to line 38). Suppose there are three stocks A, B, C, then the record for time t in main memory is [R_At, R_Bt, R_Ct], where R_At, R_Bt, and R_Ct are all vectors.
2. Consumer and Analyzer share another queue. Consumer puts one element into the queue each time after it parse the response, and Analyzer gets one element each time to anaylze it. 
Different to the data structure used for data storing, every single piece of data shared between Consumer and Analyzer is a python dictionary whose keys are the ticker of the stock and whose value are factor values of that single time. We may need to store the piece of data of previous time to illustrate the trend. 
3. In analyzer, we simply calculate the sum of buy volume and sell volume, i.e. b10 + b2 + b3 + b4 + b5, and s10 + s2 + s3 + s4 + s5 and print out. 
