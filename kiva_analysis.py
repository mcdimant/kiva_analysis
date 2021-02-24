#python script for analyzing data from kiva 


import pandas as pd
import numpy as np
import datetime
import boto3
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter, date2num
import seaborn as sns

s3 = boto3.client('s3')
bucket = 'kiva-data'
file_name = 'loans.csv'

#reads in 10k-row subset of dataframe
obj = s3.get_object(Bucket= bucket, Key= file_name) 
test_df = pd.read_csv(obj['Body'], nrows=10000) 

#reads in csv of purchasing power parity values from world bank
ppp = pd.read_csv('world_bank_PPP.csv', skiprows=4)

#returns dataframe of country names and latest PPP value
def latest_ppp(df):
    holder = {}
    latest_year = 2019
    for c in df['Country Name']:
        while np.isnan(df.at[df.index[df['Country Name']==c][0], str(latest_year)]):
                latest_year = latest_year-1
        holder[c] = df.at[df.index[df['Country Name']==c][0], str(latest_year)]
    
    return holder


#first pass high level EDA
#loan.columns
#loan.info()
#loan.describe()

#Clean up:

#converting string representations of time to Datetime objects
loan['posted_datetime'] = pd.to_datetime(loan['POSTED_TIME'])
loan['raised_datetime'] = pd.to_datetime(loan['RAISED_TIME'])

loan['loan_speed'] = loan['raised_datetime']-loan['posted_datetime']
#loan['loan_speed'].describe()

#represents time to raising loan in number of days (for matplotlib)
loan['loanspeed_days'] = loan['loan_speed'] / pd.Timedelta(hours=24)

#Function for counting number of borrowers from number of entries in gender column 
def count_borrowers(lst):
    if type(lst) != float:
        return len(lst.split(','))
    else:
        return 1

loan['borrower_n'] = loan['BORROWER_GENDERS'].apply(count_borrowers)

#graphs:

#loan_amount vs. loanspeed
fig, ax = plt.subplots()
ax.scatter(loan['loanspeed_days'],loan['LOAN_AMOUNT'], alpha=.5)
plt.show()

#Mean fulfillment speed of loan amounts, sized by n of loan amounts
loan_mean = loan.groupby(['LOAN_AMOUNT'])['loanspeed_days'].mean()
loan_count = loan.groupby(['LOAN_AMOUNT'])['LOAN_AMOUNT'].count()
#loan_count
#grouped.index
fig, ax = plt.subplots(figsize=(13,7))
ax.scatter(loan_mean.index, loan_mean, s=loan_count, alpha=.5)
ax.set_xlabel('Loan Amount')
ax.set_ylabel('Average # of Days to Raise Loan')
ax.set_title('Scatterplot of Average # of Days to Raise Loan by Loan Size, Sized by Number of Loans')


#Uses Seaborn to make violin plot of loanspeed by gender and sector
#First needed to clean gender column of non-binary values 
loan_gclean = loan[(loan['BORROWER_GENDERS'] == 'male') | (loan['BORROWER_GENDERS'] =='female')] 

fig, ax = plt.subplots(figsize=(14,8))
sns.set_theme(style="whitegrid")
ax = sns.violinplot(x='SECTOR_NAME', y="loanspeed_days",
                    hue="BORROWER_GENDERS", data=loan_gclean, palette="muted", split=True
                   )
plt.xticks(rotation=45)
plt.tight_layout()

#function to stop EC2 instance at end of script 
def stop_EC2_instance(instance_id, region='us-west-2'):
    ec2 = boto3.resource('ec2', region_name=region)
    ec2.instances.filter(InstanceIds=[instance_id]).stop()