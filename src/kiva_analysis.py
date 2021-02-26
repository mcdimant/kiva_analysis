#python script for analyzing data from kiva 


import pandas as pd
import numpy as np
import datetime
import boto3
from matplotlib import pyplot as plt
from matplotlib.dates import DateFormatter, date2num
import seaborn as sns
import scipy.stats as stats
import difflib
import re

s3 = boto3.client('s3')

loan_obj = s3.get_object(Bucket= 'kiva-data', Key='loans.csv') 
loan = pd.read_csv(loan_obj['Body']) 
print('Loaded loan data succesfully!')

ppp_obj = s3.get_object(Bucket= 'kiva-data', Key='world_bank_ppp.csv')
ppp = pd.read_csv(ppp_obj['Body'], skiprows=4)
print('Loaded ppp data successfully!')
print('Loaded all data succesfully!')

#first pass high level EDA
loan.info()
loan.describe()

#Clean up of loan data:

def datetime_cleanup():
    #Converstion of str representations of datetime to datetime objects
    #Creation of new features to support analysis, dropping na values 

    loan['posted_datetime'] = pd.to_datetime(loan['POSTED_TIME'])
    loan['raised_datetime'] = pd.to_datetime(loan['RAISED_TIME'])
    loan['loan_speed'] = loan['raised_datetime']-loan['posted_datetime']
    loan['loanspeed_days'] = loan['loan_speed'] / pd.Timedelta(hours=24)
    loan.dropna(subset=['raised_datetime'], inplace=True)
    loan['loan_year'] = [loan['raised_datetime'][x].year for x in loan.index]

datetime_cleanup()


def count_borrowers(lst):
    #uses number of items in gender column to gauge number of borrowers
    if type(lst) != float:
        return len(lst.split(','))
    else:
        return 1


loan['borrower_n'] = loan['BORROWER_GENDERS'].apply(count_borrowers)

#Function that returns gender state of loan, as male/female/mixed. This is necessary
#because the 'BORROWER_GENDERS' column is a string with the gender for each borrower
def gender_clean(lst):
    if re.findall('\\bmale\\b', str(lst)) and re.findall('\\bfemale\\b', str(list)):
        return 'mixed'
    elif not re.findall('\\bfemale\\b', str(lst)):
        return 'male'
    else:
        return 'female'

loan['gender_clean'] = loan['BORROWER_GENDERS'].apply(gender_clean)

#clean up of ppp data:

def ppp_clean(ppp):
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
    #differences in naming; it is faster to manually rename this handful: 
    ppp = ppp.rename(index={'west bank and gaza':'palestine', 'congo, rep':'congo', 'myanmar ':'myanmar (burma)',
    'yemen, rep.':'yemen', 'lao pdr':'lao people''s democratic republic',
    'congo, dem. rep.':'the democratic republic of the congo', 'egypt arab rep.': 'egypt'})

    ppp.set_index('Country Name', inplace=True)

ppp_clean(ppp)

def get_ppp_values(ppp, loan):

    ppp.set_index('Country Name', inplace=True)

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

    return holder

holder = get_ppp_values(ppp, loan)

def add_ppp_values(loan, holder):
    #Creates ppp value in loan datafarme
    loan['ppp'] = [holder[c][2] for c in range(len(holder))]

    #drops na values 
    loan['ppp'].dropna(inplace=True)

    #creates ppp_val column as product of ppp and loan_amount
    loan['loan_adj'] = loan['ppp'] * loan['LOAN_AMOUNT']

    return loan 

add_ppp_values(loan, holder)

#analysis:

#overview of loanspeed (amount of time taken to raise loan)

fig, ax = plt.subplots(2,figsize=(12,8))
ax[0].hist(loan['loanspeed_days'], bins=200, label='histogram',)
ax[0].set_title('Histogram of Amount of Time to Raise Loan (Days)')
ax[0].set_xlabel('Days To Raise Loan')
ax[0].set_ylabel('Frequency')
ax[0].set_xbound(0,400)
ax[1].boxplot(loan['loanspeed_days'], vert=False)
ax[1].set_title('Box Plot for Amount of Time to Raise Loan')
ax[1].set_xlabel('Days to Raise Loan')
plt.tight_layout()
plt.show()
plt.savefig('../images/loan_histobox1.png')


#gender
loanspeed_m = loan['loanspeed_days'][loan['BORROWER_GENDERS']=='male']
loanspeed_f = loan['loanspeed_days'][loan['BORROWER_GENDERS']=='female']

mean_male = np.mean(loanspeed_m)
mean_female = np.mean(loanspeed_f)

fig, ax = plt.subplots(figsize=(14,9))
ax.hist(loanspeed_m, bins=100, alpha=.5, label='Days to raise loan, male')
ax.axvline(mean_male, alpha=.8, linestyle='--', label='male mean {c}'.format(c=round(mean_male,2)))
ax.axvline(mean_female, alpha=.8, linestyle='--', color='orange', label='female mean {f}'.format(f=round(mean_female,2)))
ax.hist(loanspeed_f, bins=100, alpha=.5, label='Days to raise loan, female')
ax.set_xbound(0,100)
ax.legend(loc='upper right')
ax.set_xlabel('Days to Raise Loan')
ax.set_ylabel('Number of Loans')
ax.set_title('Histogram for Number of Days to Raise Loan, for male and female samples')
plt.savefig('../images/gender_histobox_aws1.png')

#A quick visual of the histogram for male and female loanspeed shows that neither
#appears to be normally distributed, so a Mann-Whitney test is more appropriate 
#for gauging statistical significance:
mw_gender = stats.mannwhitneyu(loanspeed_m, loanspeed_f)

print("P-value {p} is far below alpha level of .05, so we reject null hypo.".format(p=mw_gender[1]))
#geography

'''
This function takes as in input a country (c), the alpha levels for the shapiro-wilks,
t-test, and mann whitney test, along with the dataframe itself (loan). For a country's 
given distribution for time to raise loans, the function returns the normality of that
distribution along with the results of the appropriate significant test
'''
def geo_analyzer(c, a_shapiro, a_ttest, a_mw, loan):
    c_loan = loan.loc[loan['COUNTRY_NAME']==c, 'loanspeed_days']
    if len(c_loan) > 100:
        size_n = 'Sufficient size'
        if stats.shapiro(c_loan)[1] < a_shapiro:
            normal = 'Not normal'
            p_mw = stats.mannwhitneyu(c_loan, loan.loc[loan['COUNTRY_NAME']!=c, 'loanspeed_days'])[1]
            if p_mw < a_mw:
                significance = 'Significant'
            else:
                significance = 'Not signifcant'
        else:
            normal = 'Normal'
            p_ttest = stats.ttest(c_loan, loan.loc[loan['COUNTRY_NAME']==c, 'loanspeed_days'])[1]
            if p_ttest < a_ttest:
                significance = 'Significant'
            else:
                significance = "Not significant"
    else:
        size_n = "Insufficient size"
        size_n = "Insufficient size"
        significance = 'n/a'
    return [c, a_shapiro, a_ttest, a_mw, size_n, normal, significance]

#run geo_analyzer for each country and construct dataframe 
big_list = []
for c in set(loan['COUNTRY_NAME']):
    row = geo_analyzer(c, .01, .01, .01, loan)
    big_list.append(row)

sig_df = pd.DataFrame(big_list, columns = ['country', 'alpha_shapiro', 'alpha-ttest', 
                                      'alpha_mannwhitney', 'size_n', 'normal', 'significance'])

print(sig_df)


#function to stop EC2 instance at end of script 
#def stop_EC2_instance(instance_id, region='us-west-2'):
#    ec2 = boto3.resource('ec2', region_name=region)
#    ec2.instances.filter(InstanceIds=[instance_id]).stop()