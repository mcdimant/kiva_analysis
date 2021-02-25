# Kiva Analysis

## Introduction

This project uses exploratory data analysis (EDA) to understand what factors impact how quickly borrowers raise money for microfinance loans. "Microfinance" refers to a system of relatively small loans (typically < $5000 USD), made to individuals or small groups in developing countries to promote entrepreneurship or activity in various economic sectors. This project uses data from Kiva, one of the largest and most open microfinance insitutions to use web-based crowd-funding to finance its loans. On Kiva, borrowers have a web-page describing themselves and what they intend to use the loan for, allowing prospective lenders to lend a portion (or all) of the loan amount requested. Kiva makes available a large number of fields on each loan, and this analysis is interested in understanding what impact gender, loan sector (i.e, agriculture, industry, etc), and geography have on how quickly a loan is raised.


## Data Sourcing

### Loan Data
Kiva makes available [data snapshots](https://www.kiva.org/build/data-snapshots), archived nightly, featuring historical data on loans in CSV format. This project used data current as of 14 FEB 2021. The loans.csv files takes up 3.45 gigabytes on my local hard disk, and has 1,979,345 rows of data (representing nearly 2 million unique loans).  

### Purchashing Power Parity 
This project also read in a [csv of data from the World Bank](https://data.worldbank.org/indicator/PA.NUS.PRVT.PP) on Purchasing Power Parity (PPP) across countries to make more meaningful comparisons of loan amounts. In other words, a $500 loan may get you wildly different amounts of goods and services between countries, so multiplying the value of a loan in USD against that country's PPP value for the year of it's loan allows one to compare the value of loans between different countries more meaningfully. 

## Data Computing
Given the size of the data, the .py script reads in 10k rows of the loans.csv so I could more efficiently develop functions and code. I ran the compelted script on an Amazon EC2 instance using the full loan data set (stored in an S3 bucket). 

## Data Cleaning and Wrangling
Besides the removal of na values and changing string representations of time to datetime objects, the most important wrangling was related to calculated fields:

* loanspeed_days = calculated as the difference in days (stored as float) between "raised_time" (time when loan was compeltely raised) and "posted_time" (time when loan was posted to kiva)

* borrower_gender = the original csv had a list of genders for each borrower in the loan; the new column collapses gender to a binary (male,female); loans with mixed gender borrowers were removed. 

* borrower_n = the number of borrowers comprising the loan 

* ppp = the Purchasing Power Parity index for the loan's country and year, based on World Bank Data. If the World Bank dataset did not have the ppp for that exact year, then the closet was found. Countries for which no PPP index existed were removed from the dataset.

* loan_adjusted = the value of the loand after adjusting for ppp. This was equal to the value of the loan * ppp (for that country, in that year)

## Data Analysis


