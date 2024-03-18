# US_CO2_Emissions

Dash app for SARIMA model of US CO2 emissions by energy sector

## \*GitHub README in Progress\*

Link to Dashboard: https://usemissions.herokuapp.com/

This dashboard displays a SARIMA (Seasonal Autoregressive Integrated Moving Average) Time Series Model of yearly total United States Greenhouse Gas Emissions in CO2e, or Carbon Dioxide Equivalent Value. Carbon dioxide equivalent or CO2e means the number of metric tons of CO2 emissions with the same global warming potential as one metric ton of another greenhouse gas.

## Code and Resources Used

**Python Version**: 3.8.10

**Packages**: pandas, numpy, matplotlib, seaborn, requests, statsmodel, dash, plotly, itertools, logging, os, sqlalchemy, apscheduler

**CO2 Emission Forecast with Python (Seasonal ARIMA) - Notebook for Guidance**: https://www.kaggle.com/code/berhag/co2-emission-forecast-with-python-seasonal-arima

**How to Use the Environmental Protection Agency’s (EPA’s) API to pull Data, Using Python**: https://techrando.com/2019/07/04/how-to-use-the-environmental-protection-agencys-epas-api-to-pull-data/

## Data Collection

The data used is sourced from the United States Environmental Protection Agency's Envirofacts Data Servcice API. It provides a single access point for those interested in data on environmental activities having to do with water, land, and air, aggregated by address, ZIP code, city, county, and other geographics.

Since I was interested in Greenhouse Gas emissions data, my tables of interests were the following:

- PUB_DIM_FACILITY
- PUB_FACTS_SECTOR_GHG_EMISSION
- PUB_DIM_GHG
- PUB_DIM_SECTOR
- PUB_DIM_SUBSECTOR

Using these tables, I was able to construct a dataset of different greenhouse gases with a timeframe from 2010 - 2020. The records of emissions are aggregated by city, county, state, and energy sector, along with geospatial information like latitude and longitude. A screenshot of the data is attached here:

>INSERT IMAGE HERE<

## Data Storage

When first conducting this project, I wanted to try out using SQL to make the project a bit more interesting since I usually use Python. So I decied to use an Amazon Web Services EC2 instance to host a Postgres database. Even though I wouldn't end up keeping the database after the end of this project, the process of setting this up helped solidify learnings from previous coursework in Database Management & Analytics and allowed me to brush up on my cloud skills.

## Initial SQL Analysis

**Notebook for Database Interaction**: https://colab.research.google.com/drive/15QjdAQ5H5mmBsxblzt72vXlDdovYAdlU#scrollTo=97dHYqJT2Y81

After connecting to the data in a Google Colab Notebook instance, I investigated some basic questions using SQL, which were the following: 

*1. How do states compare when it comes to CO2 emissions?*

*2. How have CO2 emissions increased or decreased throughout the years in the US?*

*3. What is the most common Gas type?*

To summarize, I found that Texas, Louisiana, California, Illinois, and Indiana had the highest amount of GHG emissions, while DC, Vermont, New Hampshire, South Dakota, & Rhode Island had the least. I also found that the year 2017 had the most amount of emissions, 2012 had the least, and the most commmon emission in the US is CO2 gas, or carbon dioxide.

## EDA

![alt text](https://github.com/MarcelinoV/US_CO2_Emissions/blob/main/imgs/GHG_emissions_distribution.jpg "Histogram of GHG Emissions 2010-2020")

I began the Exploratory Data Analysis by getting summary measures to familiarize myself more with the data, such as null analysis, distribution, and descriptive statistics. GHG Emissions between 2010 and 2020 have a right skewed distribution, and this holds true even after controlling for year. This means that the mean and median of the emissions are far apart, which could mean the data has high variance. 

![alt text](https://github.com/MarcelinoV/US_CO2_Emissions/blob/main/imgs/gas_code_distribution.jpg "Disitribution of GHG Emissions by Gas Code")

GHG emissions are also 95% made up of three types of gas, CO2, CH4, and N2O, despite there being eight other types of gas in the data. The most interesting insight to me from this phase is which energy sectors emit the most GHG emissions. According to the following visual, the majority of greenhouse gas emissions is sourced from three sectors: Petroleum Product Suppliers, Power Plants, and Natural Gas and Natural Gas Liquids Suppliers. 

![alt text](https://github.com/MarcelinoV/US_CO2_Emissions/blob/main/imgs/energy_sector_emission_distribution.jpg "Distribution of GHG Emissions by Energy Sector")

Similar to the gas code distribution, this finding is a scenario where the Pareto Principle applies. These three sectors only make up 23% of the dataset in terms of records, yet make up 84% of GHG emissions in the dataset. This means that a majority GHG emissions produced in the United States in this timeframe boil down to only three sectors when there are 15 total. This insight would help guide my analysis going forward.

## Data Preparation for Time Series

## Model Building

## Model Evaluation

## Production and Deployment using Dash & Heroku

