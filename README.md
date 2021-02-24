# Kiva Analysis
=========
## Introduction

This project uses exploratory data analysis (EDA) to understand what factors impact how quickly borrowers raise money for microfinance loans. "Microfinance" refers to a system of relatively small loans (typically < $5000 USD), made to individuals or small groups in developing countries to promote entrepreneurship or activity in various economic sectors. This project uses data from Kiva, one of the largest and most open microfinance insitutions to use web-based crowd-funding to finance its loans. On Kiva, borrowers have a web-page describing themselves and what they intend to use the loan for, allowing prospective lenders to lend a portion (or all) of the loan amount requested. Kiva makes available a large number of fields on each loan, and this analysis is interested in understanding what impact gender, loan sector (i.e, agriculture, industry, etc), and geography have on how quickly a loan is raised.


## Data Sourcing
Kiva makes available [data snapshots](https://www.kiva.org/build/data-snapshots), archived nightly, featuring historical data on loans in CSV format. This project used data current as of 14 FEB 2021. The loans.csv files takes up 3.45 gigabytes on my local hard disk, and has 1,979,345 rows of data (representing nearly 2 million unique loans).  

This project also read in a csv of data from the World Bank on [Purchasing Power Parity (PPP)](https://data.worldbank.org/indicator/PA.NUS.PRVT.PP) across countries to make more meaningful comparisons of loan amounts. (More on this in Data Cleaning)

## Data Computing
Given the size of the data, the .py script reads in 10k rows of the loans.csv so I could more efficiently develop functions and code. Once the script was ready, I then ran it on an Amazon EC2 instance usin the full loan data set (stored in an S3 bucket). 

## Data Cleaning
Since the primary area of interest w

## Data Analysis

