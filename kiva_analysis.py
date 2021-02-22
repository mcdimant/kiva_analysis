#python script for analyzing data from kiva 


import pandas as pd
import numpy as np
import datetime
import boto3


s3 = boto3.client('s3')
bucket = 'kiva-data'
file_name = 'loans.csv'

#reads in 10,000 row subset of dataframe
obj = s3.get_object(Bucket= bucket, Key= file_name) 
test_df = pd.read_csv(obj['Body'], nrows=10000) 

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

loan['posted_datetime'] = pd.to_datetime(loan['POSTED_TIME'])

#function to stop EC2 instance at end of script 
def stop_EC2_instance(instance_id, region='us-west-2'):
    ec2 = boto3.resource('ec2', region_name=region)
    ec2.instances.filter(InstanceIds=[instance_id]).stop()