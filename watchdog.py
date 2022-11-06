import sqlite3
import requests
import re
import time
import random
import logging
import pandas as pd
from datetime import datetime

from config import DB_ADDRESS_WATCHDOG



# price request function
def perekrestok_finder(source_url):
    """
    Parse Perekrestok page, find information about the item and return name and price
    """
    
    import requests
    import re
    
    res = requests.get(source_url)
    if not res:
        raise ValueError("Connection problems")      
    elif res.status_code != 200:
        raise ValueError(f"Non-200 request code - {res.status_code}")
    else:
        price = re.findall('<div class="price-new">(.*?)</div>' ,res.text)[0]
        title = re.findall('<title data-react-helmet="true">(.*?) - купить с .*? в Перекрёстке</title>', res.text)[0]
        price = re.sub(",", ".", price[:-2])
        if title and price:
            return title, price
        else:
            raise ValueError("Problems with parsing price or title")
        
        
if __name__ == "__main__":
    
    logging.basicConfig(filename='watchdog.log', format='%(asctime)s %(message)s', level=logging.INFO)
    
    # read data from DB
    con = sqlite3.connect(DB_ADDRESS_WATCHDOG)
    cur = con.cursor()
    logging.debug("Database read urls: open connection")
    cur.execute('''SELECT id, url FROM info''')
    db_info = cur.fetchall()
    con.close()
    logging.debug("Database read urls: close connection")
    
    
    # get data from the site
    # in case of error write blank lines
    data = []
    for ID, url in db_info:
        try:
            name, price = perekrestok_finder(url.strip())
            price = price.replace(" ", "")
        except Exception as err:
            logging.error("Site parser error: can't obtain data for %s, %s", url, err)
            name, price = None, None
        print(ID, name, price)
        data.append({
            'id': ID,
            'price': price,
            'date': datetime.now().strftime("%m-%d-%Y %H:%M:%S") # ISO8601
        })
        time.sleep(random.randint(1,10))
    logging.info("Prices of %s items from %s were fetched successfully", len([i for i in data if i['price']]), len(db_info))
    
    # write prices to DB and read table for stats
    con = sqlite3.connect(DB_ADDRESS_WATCHDOG)
    cur = con.cursor()
    logging.debug("Database write prices: open connection")
    for entry in data:
        cur.execute('''INSERT INTO prices (id, datetime, price) VALUES (:id, :date, :price)''', entry)
    con.commit()
    prices=pd.read_sql_query('SELECT * FROM prices', con, parse_dates=True)
    con.close()
    logging.debug("Database write prices: close connection")
    
    
    # calculate and write stats   
    prices['datetime'] = pd.to_datetime(prices['datetime'])
    prices['price'] = pd.to_numeric(prices['price'])
    mean_price_and_date=prices.groupby(['id']).agg({'price':lambda x: x.mean(skipna=True), 'datetime':'max'})
    stats=mean_price_and_date.merge(prices, how='left', on=['id', 'datetime'], suffixes=['_mean', '_last'])
    stats['abs_profit'] = (stats['price_mean'] - stats['price_last']).round(2)
    stats['relt_profit'] = (stats['abs_profit'] / stats['price_mean']).round(2)
    stats['price_mean'] = stats['price_mean'].round(2)
#     print(stats)
    con = sqlite3.connect(DB_ADDRESS_WATCHDOG)
    stats.to_sql('stats', con, if_exists='replace', index=False)
    con.close()
    
    logging.info("The database has been updated successfully")
        