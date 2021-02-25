#python script for analyzing data from kiva 


import pandas as pd
import numpy as np
import datetime
import boto3
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter, date2num
import seaborn as sns
import scipy.stats as stats

s3 = boto3.client('s3')
bucket = 'kiva-data'
file_name = 'loans.csv'

#reads in 10k-row subset of dataframe
obj = s3.get_object(Bucket= bucket, Key=file_name) 
test_df = pd.read_csv(obj['Body'], nrows=10000) 

#first pass high level EDA
#loan.columns
#loan.info()
#loan.describe()

#Clean up:

#converting string representations of time to Datetime objects
loan['posted_datetime'] = pd.to_datetime(loan['POSTED_TIME'])
loan['raised_datetime'] = pd.to_datetime(loan['RAISED_TIME'])

#creates loan_speed column as difference between raised and posted datetimes
loan['loan_speed'] = loan['raised_datetime']-loan['posted_datetime']

#represents time to raising loan in number of days (for matplotlib)
loan['loanspeed_days'] = loan['loan_speed'] / pd.Timedelta(hours=24)

#drops na values
loan.dropna(subset=['raised_datetime'], inplace=True)

#creates loan_year column 
loan['loan_year'] = [loan['raised_datetime'][x].year for x in loan.index]

def count_borrowers(lst):
    if type(lst) != float:
        return len(lst.split(','))
    else:
        return 1

loan['borrower_n'] = loan['BORROWER_GENDERS'].apply(count_borrowers)

#reads in csv of purchasing power parity values from world bank
#first four rows are skipped to avoid irrelevant metadata
ppp = pd.read_csv('../data/world_bank_ppp.csv', skiprows=4, index_col='Country Name')

#Check for spelling difference between country names in loan data and county names in ppp data
ppp.reset_index(inplace=True)

#set all countries names to lower case 
loan['COUNTRY_NAME'] = [c.lower() for c in loan['COUNTRY_NAME']]
ppp['Country Name'] = [c.lower() for c in ppp['Country Name']]

#returns list of countries that are not matches between the data sets
for c in set(loan['COUNTRY_NAME']):
    match_tup = (c, difflib.get_close_matches(c, ppp['Country Name'], cutoff=1))
    if match_tup[1] == []:
        print(match_tup[0])

#Only 8 out of 82 countries are not matches. Most of the remaining difference are due to political
#differences in naming, rather than failure to do a fuzzy match. 
ppp = ppp.rename(index={'west bank and gaza':'palestine', 'congo, rep':'congo', 'myanmar ':'myanmar (burma)',
'yemen, rep.':'yemen', 'lao pdr':'lao people''s democratic republic',
'congo, dem. rep.':'the democratic republic of the congo', 'egypt arab rep.': 'egypt'})

ppp.set_index('Country Name', inplace=True)
ppp.index

#creates list with country name and loan year from loan data
holder = []
for c,y in zip(loan['COUNTRY_NAME'], loan['loan_year']):
    holder.append([c,y])

#selects appropriate ppp values from ppp data for each country and loan_year
#if loan year is not found, algorithm will search back up to 2 years for most recent ppp
for i in range(len(holder)):
    if holder[i][0] not in ppp.index:
        holder[i].append(np.nan)
    elif np.isnan(ppp.loc[holder[i][0], str(holder[i][1])]):
        if (ppp.loc[holder[i][0], str(holder[i][1]-1)]):
            holder[i].append(ppp.loc[holder[i][0], str(holder[i][1]-1)])
        elif (ppp.loc[holder[i][0], str(holder[i][1]-2)]):
            holder[i].append(ppp.loc[holder[i][0], str(holder[i][1]-2)])
        else:    
            holder[i].append(np.nan)
    else:
        holder[i].append(ppp.loc[holder[i][0],str(holder[i][1])])
        
#Creates ppp value in loan datafarme
loan['ppp'] = [holder[c][2] for c in range(len(holder))]

#drops na values 
loan['ppp'].dropna(inplace=True)

#creates ppp_val column as product of ppp and loan_amount
loan['ppp_val'] = loan['ppp'] * loan['LOAN_AMOUNT']

#analysis:

#gender
loanspeed_m = loan['loanspeed_days'][loan['BORROWER_GENDERS']=='male']
loanspeed_f = loan['loanspeed_days'][loan['BORROWER_GENDERS']=='female']

mx = np.mean(loanspeed_m)
mf = np.mean(loanspeed_f)

fig, ax = plt.subplots(figsize=(14,9))
ax.hist(loanspeed_m, bins=30, alpha=.5, label='Days to raise loan, male')
ax.hist(loanspeed_f, bins=30, alpha=.5, label='Days to raise loan, female')
ax.legend(loc='upper right')
ax.set_xlabel('Days to Raise Loan')
ax.set_ylabel('Number of Loans')
ax.set_title('Histogram for Number of Days to Raise Loan, for male and female samples')

stats.mannwhitneyu(loanspeed_m, loanspeed_f)

#geography
#Loops through loanspeeds of all countries and compares them against all other global countries

for x in set(loan['COUNTRY_NAME']):
    if stats.ttest_ind(loan['loanspeed_days'][loan['COUNTRY_NAME']==x], loan['loanspeed_days']
                       [loan['COUNTRY_NAME']!=x],
                       alternative='two-sided')[1] < .05:
        
        print("Loans in {country}, average of {mean} days to raise loan".format(country=x,
                                                            mean=np.mean(loan['loanspeed_days']
                                                                         [loan['COUNTRY_NAME']==x])))
    else:
        None

#sector analysis
for x in set(loan['SECTOR_NAME']):
    if stats.ttest_ind(loan['loanspeed_days'][loan['SECTOR_NAME']==x], loan['loanspeed_days']
                       [loan['loanspeed_days']!=x],
                       alternative='two-sided')[1] < .05:
        
        print("Loans in {sector}, average of {mean} days to raise loan".format(sector=x,
                                                            mean=np.mean(loan['loanspeed_days']
                                                                         [loan['SECTOR_NAME']==x])))
    else:
        None


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