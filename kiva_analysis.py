#python script for analyzing data from kiva 


import pandas as pd
import numpy as np
import datetime

loan = pd.read_csv('./kiva_ds_csv/loans.csv', nrows=10000)

loan.columns
loan.info()
loan.describe()

#subset of loans for dealing with Jordan
jl = loan[loan['COUNTRY_NAME'] == 'Jordan']

#clean up 

#converting string representations of time to datetime objects
sample_time = jl['POSTED_TIME']
a = sample_time[115]
converted = datetime.datetime.strptime(a, '%Y-%m-%d %H:%M:%S.%f +0000')
print(type(converted))

#alternatively 
jl['posted_date'] = pd.to_datetime(jl['POSTED_TIME'])

