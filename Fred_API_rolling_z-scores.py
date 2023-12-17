

"""
will need to give reasoning for why I want to monitor and plot Zscores of [SavingsRate FedFunds CPI and sp500]. 
Do I learn anything useful?
"""

#Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import scipy.stats as stats

plt.style.use('fivethirtyeight')
color_pal = plt.rcParams["axes.prop_cycle"].by_key()["color"]

import fredapi as FA

api_key_file = pd.read_csv('..//api_key_file.csv')
my_key = api_key_file['api_key'][0]
fred = FA.Fred(my_key)


##############################################################################
##############################################################################

"""
Below Blocks use Fred API to pull different datasets from FRED database.

Search function: looks for datasets by name. 
Can sort by popularity. Can be done by changing the order_by setting. 
Create variables containing a series of data.
"""

##############################################################################

"""
Sticky Price Consumer Price Index (CPI):

The Sticky Price Consumer Price Index (CPI) is calculated from a subset of goods 
and services included in the CPI that change price relatively infrequently. 
Because these goods and services change price relatively infrequently, 
they are thought to incorporate expectations about future inflation to a greater 
degree than prices that change on a more frequent basis. 
One possible explanation for sticky prices could be the costs firms incur when changing price.

"""

CPI_search = fred.search("CORESTICKM159SFRBATL", order_by='popularity')
CPI = fred.get_series(series_id = 'CORESTICKM159SFRBATL')

##############################################################################
"""
Personal Savings Rate:

Personal saving as a percentage of disposable personal income (DPI), 
frequently referred to as "the personal saving rate," 
is calculated as the ratio of personal saving to DPI.
Personal saving is equal to personal income less personal outlays and personal taxes; 
it may generally be viewed as the portion of personal income that is used either to 
provide funds to capital markets or to invest in real assets such as residences.

"""

savings_search = fred.search('PSAVERT', order_by= 'popularity' )
SavingsRate = fred.get_series(series_id = 'PSAVERT')

##############################################################################

"""
Federal Funds effective Rate:

The Federal Open Market Committee (FOMC) meets eight times a year to determine 
the federal funds target rate. As previously stated, 
this rate influences the effective federal funds rate through open market operations 
or by buying and selling of government bonds (government debt).(2) More specifically, 
the Federal Reserve decreases liquidity by selling government bonds, 
thereby raising the federal funds rate because banks have less liquidity 
to trade with other banks.

"""

FedFunds = fred.get_series(series_id = 'FEDFUNDS')

##############################################################################

"""
Including S&P500
"""
## look up S&P 500 and retrieve series with fred api
sp500_search = fred.search('S&P 500', order_by= 'popularity' )
sp500 = fred.get_series(series_id = 'SP500')

## turn sp500 series to data frame with date as first column after index
sp500_df = sp500.to_frame().reset_index()
sp500_df.rename(columns={"index":"Date"},inplace=True)

## Filter for the first of each month to align with Concat_Rates date format
filtered_sp500 = sp500_df.loc[sp500_df['Date'].dt.day == 1]

## Convert Date back to index so that I can append to Concat_Rates DataFrame by index
filtered_2_sp500 = filtered_sp500.set_index('Date')

## Rename data column as sp500 to avoid double column assignment
filtered_2_sp500.rename(columns={0: "sp500"}, inplace=True)

##############################################################################


#Concatanate rates above
concat_rates = pd.concat([SavingsRate, FedFunds, CPI, filtered_2_sp500], axis="columns")
#rename columns 
concat_rates.rename(columns={0: 'Savings Rate', 1: 'Federal Funds Rate', 2: 'CPI'}, inplace=True)

### https://medium.com/nerd-for-tech/dealing-with-missing-data-using-python-3fd785b77a05
### Backfill NaNs for sp500 strategy below works 
### but it makes more sense to filter in the concat dataframe.
concat_rates["sp500"] = concat_rates["sp500"].fillna(method='bfill')

##############################################################################
##############################################################################

"""
below variable will be used to create up-to-date rates from each FredAPI data refresh
"""

#Filter 2 dataframe to date 2013 to match sp500 start date
filtered2_concat_rates = concat_rates.loc['2013-01-01 00:00:00': ]


##############################################################################
##############################################################################

### filtering rates to start from 2013
Compare_rates1 = filtered2_concat_rates.copy()
Compare_rates = Compare_rates1.loc['2013-01-01 00:00:00':] ##"2022-11-01 00:00:00"

### As mentioned above, I decided to compute rolling Zscores 
Compare_Rolling_Zscore = Compare_rates.sub(Compare_rates.rolling(window=12).mean()).div(Compare_rates.rolling(window=12).std())

### Plotting Zscores
Compare_Rolling_Zscore.plot(figsize=(10,5), title='Comparing Rolling Z-scores (1-yr. Window)', lw=1)

##############################################################################
##############################################################################

#### Run Descriptive Analyses
mean_rates = Compare_rates.mean()
mean_rolling = Compare_Rolling_Zscore.mean()
print()
print("Mean: Raw Rates \n")
print(mean_rates, "\n")
print("Mean: Rolling Zscores \n")
print(mean_rolling)


print()


#### Correlation
corr_rates = Compare_rates.corr()
print('------------------------------')
print("Correlation: Raw Rates")
print(corr_rates)
print('------------------------------')    
    
print()


### Variance of trend lines

var_fed = FedFunds.var()
std_fed = FedFunds.std()
print("Variance of Fed Funds: ", var_fed)
print("Standard Deviation: ", std_fed)
print()

var_cpi = CPI.var()
std_cpi = CPI.std()
print("Variance of CPI: ", var_cpi)
print("Standard Deviation: ", std_cpi)
print()

var_savings = SavingsRate.var()
std_savings = SavingsRate.std()
print("Variance of Savings Rate: ", var_savings)
print("Standard Deviation: ", std_savings)
print()

var_sp500 = filtered_2_sp500.var()
std_sp500 = filtered_2_sp500.std()
print("Variance of S&P 500: ", var_sp500)
print("Standard Deviation: ", std_sp500)
print()



### https://www.bloomberg.com/opinion/articles/2022-06-19/niall-ferguson-fed-s-powell-is-blundering-on-inflation-rate-hikes
"""
After reading article above by Naill Ferguson, I should cut the data sets into sections.
Each Section should be split based on different FED chairs OR split by eras (president/world events). Maybe I'll do this...

"""
