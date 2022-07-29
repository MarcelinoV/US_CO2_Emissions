import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint, adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
import warnings
warnings.filterwarnings('ignore')
import itertools

def preprocess(data):

    # data formatting 

    data.columns = [i.lower() for i in data.columns]

    time_df = data.sort_index()

    time_df.drop_duplicates(inplace=True)

    time_df.dropna(subset=['co2e_emission'], inplace=True)

    emissions = time_df.groupby(['sector_name',
                pd.Grouper('year')])['co2e_emission'].sum().unstack(level=0)

    # Converting the index as date

    # emissions.index = emissions.index.astype('int')
    # emissions.index = pd.to_datetime(emissions.index, format='%Y')

    return emissions

# create test stationary functions: plot and test

def test_stationary_plot(df):
    
    rol_mean = df.rolling(window=2, center=False).mean()
    rol_std = df.rolling(window=2, center=False).std()
    
    plt.plot(df, color='blue', label='Original Data')
    plt.plot(rol_mean, color='red', label='Rolling Mean')
    plt.plot(rol_std, color='black', label='Rolling Std')
    
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    
    plt.xlabel('Time in Years', fontsize=10)
    plt.ylabel('Total Emissions', fontsize=10)
    plt.legend(loc='best', fontsize=10)
    plt.title('Rolling Mean & Standard Deviation', fontsize=10)
    plt.show();
    
def test_stationary_adfuller(df, alpha=0.01):
    
    ts_test = adfuller(df, autolag='AIC')
    ts_test_output = pd.Series(ts_test[0:4], index=['Test Statistic',
                                                    'p-value',
                                                    '# Lags Used',
                                                    '# Observations Used'])
    
    for key, value in ts_test[4].items():
        ts_test_output['Critical Value {}'.format(key)] = value
        
    print(ts_test_output)
    
    
    if ts_test[1] <= alpha:
        print("Strong evidence against the null hypothesis, reject the null hypothesis. Data has no unit root, hence it is stationary")
    
    else:
        print("Weak evidence against null hypothesis, time series has a unit root, indicating it is non-stationary ")
        
    return ts_test[1] <= alpha

def time_series_grid_search(series):
    
    p = d = q = range(0,2)

    pdq = list(itertools.product(p,d,q))

    pdq_x_QDQs = [(x[0], x[1], x[2], 2) for x in pdq]
    
    import warnings
    warnings.filterwarnings('ignore')
    
    metrics = []

    for param in pdq:
        for seasonal_param in pdq_x_QDQs:
            try:
                mod = sm.tsa.statespace.SARIMAX(series,
                                                order=param,
                                                seasonal_order=seasonal_param,
                                                enforce_stationarity=True,
                                                enforce_invertibility=False)
                results=mod.fit()
                metrics.append((param, seasonal_param, results.aic))

            except:
                continue
    
    sorted_metrics = sorted(metrics, key=lambda x:x[2], reverse=False)

    return sorted_metrics[0]


def sector_co2_forecast(data, col):
    
    # pandas dataframe and string as inputs
    
    # get data
    
    series = data[col]
    
    # interpolate
    
    series.interpolate(method='spline', order=5, inplace=True)
    
    # test
    
    tested_series = test_stationary_adfuller(series)
    

    if not tested_series:
        while True:

            # try moving average
            print('Moving Average')
            moving_avg = series.rolling(2).mean()
            series_mov_avg = series - moving_avg
            series_mov_avg.dropna(inplace=True)
            
            tested_series = test_stationary_adfuller(series_mov_avg)

            if tested_series:
                tested_series = series_mov_avg
                break
 
            
            # try exponential moving average
            print('Exponential Moving Average')
            exp_moving_avg = series.ewm(halflife=2).mean()
            series_exp_avg = series - exp_moving_avg
            series_exp_avg.dropna(inplace=True)
            
            tested_series = test_stationary_adfuller(series_exp_avg)
            
            if tested_series:
                tested_series = series_exp_avg
                break
   
            
            # try first order differencing
            print('First Order Differencing')
            series_first_diff = series - series.shift(1)
            series_first_diff.dropna(inplace=True)

            tested_series = test_stationary_adfuller(series_first_diff)
            
            if tested_series:
                tested_series = series_first_diff
                break


            # try seasonal differencing
            print('Seasonal Differencing')
            series_seasonal_diff = series - series.shift(2)

            # test
            tested_series = test_stationary_adfuller(series_seasonal_diff.dropna(inplace=False))
            
            if tested_series:
                tested_series = series_seasonal_diff
                break      

                
            # try seasonal first differencing
            print('Seasonal First Differencing')
            series_seasonal_first_diff = series_seasonal_diff - series_seasonal_diff.shift(1)

            # test

            tested_series = test_stationary_adfuller(series_seasonal_first_diff.dropna(inplace=False))
            if tested_series:
                tested_series = series_seasonal_first_diff
                break
                
                
            # try decomposition
            print('Decomposition')
            decomposition = seasonal_decompose(series, period=1)
            
            resid = decomposition.resid
            
            series_decompose = resid
            series_decompose.dropna(inplace=True)
            
            tested_series = test_stationary_adfuller(series_decompose)
            
            if tested_series:
                tested_series = series_decompose
                break
                
                
            # try log transform
            print('Log Transformation')
            
            series_log = np.log(series)
            tested_series = test_stationary_adfuller(series_log)
            
            if tested_series:
                tested_series = series_log
                break
                
                
            # default to regular series if no transformations succeed
            
            if not tested_series:
                tested_series = series
                break

    else:
        tested_series = series

    # grid search
    
    parameters = time_series_grid_search(tested_series)
    
    # fit model
    
    model = sm.tsa.statespace.SARIMAX(tested_series,
                                 order=parameters[0],
                                 seasonal_order=parameters[1],
                                 enforce_stationarity=True,
                                 enforce_invertibility=False)
    # fit model

    results = model.fit()

    return results
        

def integrity_check(data):


    # find columns that will be unavailable for modeling

    unused = []
    
    # interpolation test, if m<k column not usuable
    for col in data.columns:

        try:
        
            data[col].interpolate(method='spline', order=5, inplace=True)

        except:

            unused.append(col)

    return unused