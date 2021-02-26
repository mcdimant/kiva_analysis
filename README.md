# Kiva Analysis

## Introduction

This project uses exploratory data analysis (EDA) to understand what factors impact how quickly borrowers raise money for microfinance loans. "Microfinance" refers to a system of relatively small loans (typically < $5000 USD), made to individuals or small groups in developing countries to promote entrepreneurship or activity in various economic sectors. This project uses data from Kiva, one of the largest and most open microfinance insitutions to use web-based crowd-funding to finance its loans. On Kiva, borrowers have a web-page describing themselves and what they intend to use the loan for, allowing prospective lenders to lend a portion (or all) of the loan amount requested. Kiva makes available a large number of fields on each loan, and this analysis is interested in understanding what impact gender,  and geography have on how quickly a loan is raised.


## Data Sources

### Loan Data
Kiva makes available [data snapshots](https://www.kiva.org/build/data-snapshots), archived nightly, featuring historical data on loans in CSV format. This project used data current as of 14 FEB 2021. The loans.csv files takes up 3.45 gigabytes on my local hard disk, and has 1,979,345 rows of data (representing nearly 2 million unique loans).  

Below is a screenshot of a row of raw data. Each record contains 34 fields, that give a rich description of the loan (amount, timing, sector), borrower metadata (location, gender, language), and a text field with the borrower's own description of their aims:

![](images/kiva_raw_data.png)


### Purchashing Power Parity 
This project also read in a [csv of data from the World Bank](https://data.worldbank.org/indicator/PA.NUS.PRVT.PP) on Purchasing Power Parity (PPP) across countries to make more meaningful comparisons of loan amounts. In other words, a $500 loan may get you wildly different amounts of goods and services between countries, so multiplying the value of a loan in USD against that country's PPP value for the year of it's loan allows one to compare the value of loans between different countries more meaningfully. 

## Computing
Given the size of the data, the .py script reads in 10k rows of the loans.csv to more more efficiently develop functions and code. I ran the completed script on an AWS EC2 instance (t2 2x large) using the full loan data set (stored in an S3 bucket). 

## Data Cleaning and Wrangling
Besides the removal of na values and changing string representations of time to datetime objects, the most important wrangling was related to calculated fields, described below (See .py script for additional detail):

* loanspeed_days = calculated as the difference in days (stored as float) between "raised_time" (time when borrower raised 100% of the loan) and "posted_time" (time when loan was posted to Kiva)

* borrower_gender = the original csv had a list of genders for each borrower in the loan; the new column collapses gender to a binary (male,female); loans with mixed gender borrowers were removed. 

* borrower_n = the number of borrowers comprising the loan 

* ppp = the Purchasing Power Parity index for the loan's country and year, based on World Bank Data. If the World Bank dataset did not have the ppp for that exact year, then the closet was found. Countries for which no PPP index existed were removed from the dataset.

* loan_adj = the value of the loand after adjusting for purchasing power parity. This was equal to the value of the loan * ppp (for that country, in that year)

## Data Analysis
While many factors may influence the amount of time it takes for a borrower to raise a loan, this analysis focuses on whether **gender** and **geography** have a significant impact on the amount of time it takes for borrowers to raise a loan. 

First, let's look at some basic descriptives of the amount of time it takes to raise money for a loan before stratifying this variable:

Here's an image, taken from a 10k row sub-sample of the full data set, plotting loan amount against time taken to raise the loan. 
![](images/scatterplot.png)


### Gender
A brief look at the histogram for how long it took men vs women to raise their loan shows that: a) the distributions do not appear normal and b) the means appear quite different.  

![](images/gender_histobox_aws1.png)

Therefore, to test the null hypothesis that gender has no bearing on the amount of time it takes borrowers to raise a loan, I used a Mann-Whitney test, with an alpha level of .05, which returned a p-value of 4.326*10^-66 - so we can confidently reject the null hypothesis. As for interpretation, there may be many reasons why women appear to raise loans more quickly than men. It could be that the majority of donors are women, or that female borrowers, ipso facto, are seen as more personally sympathetic than male borrowers, or that female borrowers describe their loans differently than men in ways that are more engaging to borrowers. Many potential explanations are testable and fertile areas for further research. 

### Geography

The full dataset includes 77 countries, so the analysis developed a function to automate the process. The null hypothesis is that geography, interpreted here at the country level, has no bearing on how quickly borrowers from a given country are able to raise loans, with the alternative hypothesis that borrowers from X country are faster or slower than all other countries in raising loans. Here is the process that the analysis took:
*   1. Was country's distribution large enough (minimum 100 records per country)? 
*   2. Was country's distribution normal? (Used Shapiro-Wilks to test for this with an alpha of .01)
    * 2a. If normal, then proceed to independent T-test between Country X and data from all other countries
    * 2b. If not normal, perform Mann-Whitney test between Country X and data from all other countries
*   3. Return the results in a list

Iterating through the set of countries and some Pandas wrangling produces the following table showing mean loan size, alpha levels, normality, p-values, and significance for each country for the above hypotheses:

Given the frequency of "significant" results, several comments can be made:
* For very large samples (many in this case where tens or hundreds of thousands of records), the Mann-Whitney test may be more sensitive to significance. 
* Geography may actually be a significant factor in how quickly loans are raised. There are many potential interperations available - it could be that lender familiariaty with the country is largely a function of geography,
or that geography serves as a kind of proxy for stereotypes or images in lender minds that impact willingness to fund a loan. 

|id |country                             |mean days to raise loan|alpha_shapiro|alpha-ttest|alpha_mannwhitney|p value                |size_n           |normal    |significance  |
|---|------------------------------------|-----------------------|-------------|-----------|-----------------|-----------------------|-----------------|----------|--------------|
|0  |indonesia                           |8.93132690124573       |0.01         |0.01       |0.01             |1.1447355944210215e-290|Sufficient size  |Not normal|Significant   |
|1  |solomon islands                     |13.822281921525487     |0.01         |0.01       |0.01             |1.0059253372163046e-32 |Sufficient size  |Not normal|Significant   |
|2  |south sudan                         |4.701965344233696      |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|3  |bhutan                              |16.09929398148148      |0.01         |0.01       |0.01             |                       |Insufficient size|n/a       |n/a           |
|4  |azerbaijan                          |22.134986655541354     |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|5  |burundi                             |15.126655604037754     |0.01         |0.01       |0.01             |6.154734664916294e-40  |Sufficient size  |Not normal|Significant   |
|6  |myanmar (burma)                     |16.85677669680614      |0.01         |0.01       |0.01             |6.489336842005581e-164 |Sufficient size  |Not normal|Significant   |
|7  |ukraine                             |8.298506512438086      |0.01         |0.01       |0.01             |2.6926488236110434e-168|Sufficient size  |Not normal|Significant   |
|8  |senegal                             |14.233829788599213     |0.01         |0.01       |0.01             |9.529233247007523e-33  |Sufficient size  |Not normal|Significant   |
|9  |tanzania                            |10.863651606631969     |0.01         |0.01       |0.01             |3.78040523904042e-99   |Sufficient size  |Not normal|Significant   |
|10 |benin                               |9.70942516875823       |0.01         |0.01       |0.01             |3.7617003297421115e-131|Sufficient size  |Not normal|Significant   |
|11 |liberia                             |5.848066732916055      |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|12 |georgia                             |14.619878454776673     |0.01         |0.01       |0.01             |5.122009113216602e-42  |Sufficient size  |Not normal|Significant   |
|13 |nigeria                             |9.681284646808805      |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|14 |costa rica                          |13.833184066139705     |0.01         |0.01       |0.01             |1.252035588888891e-45  |Sufficient size  |Not normal|Significant   |
|15 |papua new guinea                    |2.9384733371559633     |0.01         |0.01       |0.01             |1.0773142863504725e-67 |Sufficient size  |Not normal|Significant   |
|16 |honduras                            |13.70249754745612      |0.01         |0.01       |0.01             |1.3880430894203088e-295|Sufficient size  |Not normal|Significant   |
|17 |nicaragua                           |14.935810510175443     |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|18 |samoa                               |15.738065096331693     |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|19 |belize                              |3.951092455183494      |0.01         |0.01       |0.01             |4.603827146160287e-42  |Sufficient size  |Not normal|Significant   |
|20 |sri lanka                           |2.4785015081369246     |0.01         |0.01       |0.01             |1.8118650779796822e-87 |Sufficient size  |Not normal|Significant   |
|21 |lao people's democratic republic    |5.866707966959765      |0.01         |0.01       |0.01             |3.1246925462826117e-114|Sufficient size  |Not normal|Significant   |
|22 |somalia                             |9.08073951705009       |0.01         |0.01       |0.01             |6.0008940643596006e-05 |Sufficient size  |Not normal|Significant   |
|23 |ecuador                             |12.00098895945373      |0.01         |0.01       |0.01             |4.2077989918500785e-16 |Sufficient size  |Not normal|Significant   |
|24 |tonga                               |9.118386323376704      |0.01         |0.01       |0.01             |5.238407926735623e-20  |Sufficient size  |Not normal|Significant   |
|25 |israel                              |9.459281406936597      |0.01         |0.01       |0.01             |0.055533021752784274   |Sufficient size  |Not normal|Not signifcant|
|26 |mauritania                          |2.9006944444444445     |0.01         |0.01       |0.01             |                       |Insufficient size|n/a       |n/a           |
|27 |rwanda                              |12.341861709569761     |0.01         |0.01       |0.01             |1.5892944431234847e-06 |Sufficient size  |Not normal|Significant   |
|28 |fiji                                |14.611644692314782     |0.01         |0.01       |0.01             |2.4984570242423673e-47 |Sufficient size  |Not normal|Significant   |
|29 |mexico                              |10.50911712000201      |0.01         |0.01       |0.01             |3.993450927989569e-53  |Sufficient size  |Not normal|Significant   |
|30 |ghana                               |7.605034367039916      |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|31 |brazil                              |15.082783985819976     |0.01         |0.01       |0.01             |1.871313075296295e-31  |Sufficient size  |Not normal|Significant   |
|32 |the democratic republic of the congo|14.4663813824411       |0.01         |0.01       |0.01             |3.414392340530089e-79  |Sufficient size  |Not normal|Significant   |
|33 |lebanon                             |16.09189735313168      |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|34 |vietnam                             |12.821077621950574     |0.01         |0.01       |0.01             |5.3167536787684463e-45 |Sufficient size  |Not normal|Significant   |
|35 |united states                       |34.40414011330341      |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|36 |kyrgyzstan                          |18.89852724529167      |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|37 |peru                                |10.369852898987107     |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|38 |egypt                               |11.979076477045227     |0.01         |0.01       |0.01             |3.8127863761080664e-08 |Sufficient size  |Not normal|Significant   |
|39 |zimbabwe                            |11.683772889865498     |0.01         |0.01       |0.01             |1.953713077921353e-12  |Sufficient size  |Not normal|Significant   |
|40 |colombia                            |19.343819623181673     |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|41 |timor-leste                         |12.996932896838842     |0.01         |0.01       |0.01             |2.223956594440506e-30  |Sufficient size  |Not normal|Significant   |
|42 |chile                               |5.711525660410692      |0.01         |0.01       |0.01             |3.001652739835011e-61  |Sufficient size  |Not normal|Significant   |
|43 |yemen                               |14.809316798043413     |0.01         |0.01       |0.01             |1.2790358232241254e-59 |Sufficient size  |Not normal|Significant   |
|44 |guam                                |46.18214699074074      |0.01         |0.01       |0.01             |                       |Insufficient size|n/a       |n/a           |
|45 |puerto rico                         |30.1952806372549       |0.01         |0.01       |0.01             |6.313015199089573e-44  |Sufficient size  |Not normal|Significant   |
|46 |bosnia and herzegovina              |3.274028025249756      |0.01         |0.01       |0.01             |2.5625819514100717e-139|Sufficient size  |Not normal|Significant   |
|47 |botswana                            |0.5990509259259259     |0.01         |0.01       |0.01             |                       |Insufficient size|n/a       |n/a           |
|48 |bulgaria                            |9.804744860326428      |0.01         |0.01       |0.01             |0.001708565418855198   |Sufficient size  |Not normal|Significant   |
|49 |togo                                |9.725762581061721      |0.01         |0.01       |0.01             |2.480435821511249e-232 |Sufficient size  |Not normal|Significant   |
|50 |armenia                             |20.470117728654223     |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|51 |kenya                               |14.947823776458268     |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|52 |guatemala                           |13.73302175324933      |0.01         |0.01       |0.01             |1.511941994592241e-116 |Sufficient size  |Not normal|Significant   |
|53 |mali                                |15.200509499735393     |0.01         |0.01       |0.01             |3.022813615809627e-172 |Sufficient size  |Not normal|Significant   |
|54 |canada                              |5.69259837962963       |0.01         |0.01       |0.01             |                       |Insufficient size|n/a       |n/a           |
|55 |india                               |9.605483446311755      |0.01         |0.01       |0.01             |6.62617561557167e-101  |Sufficient size  |Not normal|Significant   |
|56 |vanuatu                             |35.96345196759259      |0.01         |0.01       |0.01             |                       |Insufficient size|n/a       |n/a           |
|57 |thailand                            |6.555501715265867      |0.01         |0.01       |0.01             |1.06830566795252e-34   |Sufficient size  |Not normal|Significant   |
|58 |cambodia                            |10.120237983940873     |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|59 |panama                              |6.122887731481482      |0.01         |0.01       |0.01             |6.517486174555032e-19  |Sufficient size  |Not normal|Significant   |
|60 |paraguay                            |10.505080797930118     |0.01         |0.01       |0.01             |2.6524531240457117e-151|Sufficient size  |Not normal|Significant   |
|61 |philippines                         |9.495682225672725      |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|62 |namibia                             |8.575602202581369      |0.01         |0.01       |0.01             |                       |Insufficient size|n/a       |n/a           |
|63 |zambia                              |9.463066765136018      |0.01         |0.01       |0.01             |1.3195184352494824e-40 |Sufficient size  |Not normal|Significant   |
|64 |uruguay                             |6.853148148148148      |0.01         |0.01       |0.01             |                       |Insufficient size|n/a       |n/a           |
|65 |dominican republic                  |10.737334021428126     |0.01         |0.01       |0.01             |4.151594702987655e-21  |Sufficient size  |Not normal|Significant   |
|66 |mozambique                          |14.891809337146087     |0.01         |0.01       |0.01             |9.880036442134574e-110 |Sufficient size  |Not normal|Significant   |
|67 |sierra leone                        |10.82215953374243      |0.01         |0.01       |0.01             |1.7944081014376718e-55 |Sufficient size  |Not normal|Significant   |
|68 |uganda                              |12.165272786596056     |0.01         |0.01       |0.01             |9.356191154709359e-98  |Sufficient size  |Not normal|Significant   |
|69 |chad                                |2.919952755009108      |0.01         |0.01       |0.01             |                       |Insufficient size|n/a       |n/a           |
|70 |pakistan                            |15.27758386277156      |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|71 |mongolia                            |10.562275638517715     |0.01         |0.01       |0.01             |5.279830549232648e-109 |Sufficient size  |Not normal|Significant   |
|72 |nepal                               |3.4831917183374115     |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|73 |kosovo                              |17.285241199110438     |0.01         |0.01       |0.01             |7.161997624242812e-126 |Sufficient size  |Not normal|Significant   |
|74 |moldova                             |12.64271561348448      |0.01         |0.01       |0.01             |0.03630421344775717    |Sufficient size  |Not normal|Not signifcant|
|75 |cote d'ivoire                       |3.5244574499411074     |0.01         |0.01       |0.01             |5.299243433812152e-65  |Sufficient size  |Not normal|Significant   |
|76 |bangladesh                          |5.027654320987654      |0.01         |0.01       |0.01             |                       |Insufficient size|n/a       |n/a           |
|77 |lesotho                             |3.6015439111789327     |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|78 |turkey                              |4.595407193058215      |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|79 |el salvador                         |18.375557811282306     |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|80 |palestine                           |14.436172197834953     |0.01         |0.01       |0.01             |5.68121372229704e-117  |Sufficient size  |Not normal|Significant   |
|81 |burkina faso                        |10.032404901060946     |0.01         |0.01       |0.01             |2.6931002055620326e-25 |Sufficient size  |Not normal|Significant   |
|82 |tajikistan                          |16.84978866856197      |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|83 |suriname                            |19.662124112239475     |0.01         |0.01       |0.01             |7.381829396853697e-33  |Sufficient size  |Not normal|Significant   |
|84 |china                               |7.329100355054303      |0.01         |0.01       |0.01             |0.0015884003898880322  |Sufficient size  |Not normal|Significant   |
|85 |bolivia                             |17.536696275486975     |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|86 |jordan                              |16.81320706866017      |0.01         |0.01       |0.01             |0.0                    |Sufficient size  |Not normal|Significant   |
|87 |madagascar                          |9.645645650676512      |0.01         |0.01       |0.01             |1.8902987556698254e-13 |Sufficient size  |Not normal|Significant   |
|88 |gaza                                |-381.02980324074076    |0.01         |0.01       |0.01             |                       |Insufficient size|n/a       |n/a           |
|89 |saint vincent and the grenadines    |11.881797598379631     |0.01         |0.01       |0.01             |                       |Insufficient size|n/a       |n/a           |
|90 |malawi                              |6.8879796026548235     |0.01         |0.01       |0.01             |2.5042835485654154e-117|Sufficient size  |Not normal|Significant   |
|91 |cameroon                            |12.133736833022072     |0.01         |0.01       |0.01             |1.9627967502390376e-12 |Sufficient size  |Not normal|Significant   |
|92 |iraq                                |18.03528542448553      |0.01         |0.01       |0.01             |1.753344598314033e-97  |Sufficient size  |Not normal|Significant   |
|93 |afghanistan                         |8.028448573010431      |0.01         |0.01       |0.01             |4.394214229155451e-161 |Sufficient size  |Not normal|Significant   |
|94 |congo                               |8.101115465109473      |0.01         |0.01       |0.01             |1.1000535531741562e-28 |Sufficient size  |Not normal|Significant   |
|95 |haiti                               |10.540532287649471     |0.01         |0.01       |0.01             |0.15895632455180475    |Sufficient size  |Not normal|Not signifcant|
|96 |south africa                        |7.163141411817969      |0.01         |0.01       |0.01             |1.7797286453544275e-18 |Sufficient size  |Not normal|Significant   |
|97 |albania                             |16.14120571436262      |0.01         |0.01       |0.01             |1.477478718224667e-129 |Sufficient size  |Not normal|Significant   |


## Further Research
Additional avenues of research include:

* Stratifying country results by region to see if regional patterns tell a story 
* Comparing country names to their prevalance in the media to test the theory that greater media mention of 'country X' promotes faster loan raising. "Prevalance in the media" could be gauged by data from Google Trends. 
* Stratifying data by other factors, such as loan sector, attributes of the loan description, tags for the loan. 