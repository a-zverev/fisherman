import sqlite3
import re
import time
import random
import logging
import pandas as pd
from datetime import datetime

import parcers
from config import DB_ADDRESS_WATCHDOG

 
        
if __name__ == "__main__":
    
    logging.basicConfig(filename='watchdog.log', format='%(asctime)s %(message)s', level=logging.INFO)
    
    # read data from DB
    con = sqlite3.connect(DB_ADDRESS_WATCHDOG)
    cur = con.cursor()
    logging.debug("Database read urls: open connection")
    cur.execute('''SELECT id, url FROM items_info''')
    db_info = cur.fetchall()
    con.close()
    logging.debug("Database read urls: close connection")
    
    
    # get data from the site
    data = []
    for ID, url in db_info:
        try:
            res = parcers.perekrestok_parcer(url.strip())
            price = res['price']
        except Exception as err:
            logging.error("The parser error: can't obtain data for %s, %s", url, err)
            continue
        if res["is_avaliable"]:
            data.append({
                'id': ID,
                'price': price,
                'date': datetime.now().strftime("%m-%d-%Y %H:%M:%S"), # ISO8601
                'is_onsale': res['is_onsale']
            })
        time.sleep(random.randint(1,4))
    logging.info("Prices of %s items from %s were fetched successfully", len(data), len(db_info))
    
    # write prices to DB and read table for stats
    con = sqlite3.connect(DB_ADDRESS_WATCHDOG)
    cur = con.cursor()
    logging.debug("Database write prices: open connection")
    for entry in data:
        cur.execute('''INSERT INTO prices (id, datetime, price, is_onsale) VALUES (:id, :date, :price, :is_onsale)''', entry)
    con.commit()
    prices=pd.read_sql_query('SELECT id, datetime, price FROM prices', con, parse_dates=True)
    con.close()
    logging.debug("Database write prices: close connection")
    
    
    # calculate and write stats   
    prices['datetime'] = pd.to_datetime(prices['datetime'])
    prices['price'] = pd.to_numeric(prices['price'])
    mean_price_and_date=prices.groupby(['id']).agg({'price':lambda x: x.mean(skipna=True), 'datetime':'max'})
    stats=mean_price_and_date.merge(prices, how='left', on=['id', 'datetime'], suffixes=['_mean', '_last'])
    stats['abs_profit'] = (stats['price_mean'] - stats['price_last']).round(2)
    stats['relt_profit'] = (1 - (stats['abs_profit'] / stats['price_mean'])).round(2)
    stats['price_mean'] = stats['price_mean'].round(2)
    
    logging.debug("Database write stats: open connection")
    con = sqlite3.connect(DB_ADDRESS_WATCHDOG)
    stats.to_sql('stats', con, if_exists='replace', index=False)
    con.close()
    logging.debug("Database write stats: close connection")
    
    logging.info("The database has been updated successfully")
        