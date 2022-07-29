import sqlite3
import pandas as pd

def create_table():

    # connection object

    conn = None

    try: 
        conn = sqlite3.connect(r'database\co2_emissions.sqlite')

    except:
        print('Connection not established.')

    # cursor object

    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS Emissions(
                    ID INTEGER PRIMARY KEY,
                    LATITUDE NUMERIC NULL,
                    LONGITUDE NUMERIC NULL,
                    CITY VARCHAR(60) NOT NULL,
                    STATE VARCHAR(60) NOT NULL,
                    ZIP VARCHAR(10) NOT NULL,
                    COUNTY VARCHAR(60) NULL,
                    ADDRESS1 TEXT NULL,
                    YEAR INTEGER NOT NULL,
                    PARENT_COMPANY TEXT NULL,
                    SECTOR_NAME TEXT NOT NULL,
                    SUBSECTOR_DESC TEXT NOT NULL,
                    GAS_CODE VARCHAR(10) NOT NULL,
                    CO2E_EMISSION NUMERIC NULL
            )''')

    # test
    # c.execute('SELECT * FROM EMISSIONS')

    # rows = c.fetchall()

    # for row in rows[:500]:
    #     print(row)

    return conn
    # c.execute("SELECT * FROM sqlite_master WHERE type='table';")
    # print(c.fetchall())



def insert_data(df, conn):

    test = pd.read_sql_query("SELECT * from Emissions", conn)

    if len(test) == 0:

        df.to_sql(name='Emissions', con=conn, if_exists='append', index=False)

        print('Data Inserted!')

    else:
        print('Data Present')

    conn.close()

def load_data():

    # connection object

    conn = None

    try: 
        conn = sqlite3.connect(r'database\co2_emissions.sqlite')

    except:
        print('Connection not established.')

    with conn as conn:

        data = pd.read_sql('SELECT * FROM EMISSIONS', conn)

        if len(data) == 0:
            
            data = pd.read_pickle(r'database/backup.pkl')

    return data


def api_call():
    
    import pandas as pd
    import io
    import requests

    # define desired tables

    tables = ['PUB_DIM_FACILITY', 'PUB_FACTS_SECTOR_GHG_EMISSION',
              'PUB_DIM_GHG', 'PUB_DIM_SECTOR', 'PUB_DIM_SUBSECTOR']

    # define empty data dictionary

    data = {}

    # get and merge data

    for name in tables:

        url= f'https://enviro.epa.gov/enviro/efservice/{name}/csv'

        result = requests.get(url).content
        df = pd.read_csv(io.StringIO(result.decode('utf-8')),
                        engine='python', encoding='utf-8', error_bad_lines=False)

        # add recovered data to dictionary

        data[name] = df

    # merge pub_dim_facility with pub_facts_sector

    # print(data['PUB_FACTS_SECTOR_GHG_EMISSION'])
    # print(data['PUB_DIM_FACILITY'])

    final_df = pd.merge(data['PUB_DIM_FACILITY'], data['PUB_FACTS_SECTOR_GHG_EMISSION'],
                       left_on=['FACILITY_ID', 'YEAR'],
                       right_on=['FACILITY_ID', 
                                 'YEAR'], how='inner')

    # merge final_df with pub_dim_ghg

    final_df = pd.merge(final_df, data['PUB_DIM_GHG'],
                        left_on=['GAS_ID'],
                        right_on=['GAS_ID'], how='inner')

    # merge final_df with pub_dim_sector

    final_df = pd.merge(final_df, data['PUB_DIM_SECTOR'],
                        left_on=['SECTOR_ID'],
                        right_on=['SECTOR_ID'], how='inner')

    # merge final_df with pub_dim_subsector

    final_df = pd.merge(final_df, data['PUB_DIM_SUBSECTOR'],
                        left_on=['SUBSECTOR_ID'],
                        right_on=['SUBSECTOR_ID'], how='inner')

    # subset columns of interests

    final_df = final_df[['LATITUDE', 'LONGITUDE',
                         'CITY', 'STATE',
                         'ZIP', 'COUNTY', 
                         'ADDRESS1', 'YEAR',
                         'PARENT_COMPANY', 'SECTOR_NAME',
                         'SUBSECTOR_DESC', 'GAS_CODE', 
                         'CO2E_EMISSION']]
    
    return final_df



def update_data(response, data=None):
    
    # connection object

    conn = None

    try: 
        conn = sqlite3.connect(r'database\co2_emissions.sqlite')

    except:
        print('Connection not established.')

    with conn as conn:

        data = pd.read_sql('SELECT * FROM EMISSIONS', conn)


    # check if new data already in database
    
    keys = list(response.columns.values)
    i1 = data.set_index(keys).index
    i2 = response.set_index(keys).index
    map_ = response[~i2.isin(i1)] # rows where response = database exactly

    print('Number of new rows:', len(map_))
    print('Duplicates in database', data.duplicated().sum())

    if len(map_) > 10: # if there are more than 10 new records, update database

        new = response.drop_duplicates(keep='last')
        
        new.to_sql(name='Emissions', con=conn, if_exists='append', index=False)
        
       # return new
    
    else:
        
        print('No new data, deleting response.')
        del response

