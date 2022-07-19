import sqlite3
import requests
import re
import time
import random
import logging
from datetime import datetime



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
    
    logging.basicConfig(filename='watchdog.log', format='%(asctime)s %(message)s', level=logging.DEBUG)
    
    ### request and write data (old one, in csv-table) ###
    data = []
    current_datetime = datetime.now().strftime("%d/%m/%Y|%H:%M")
    
    with open("Grocery.txt", 'r') as items:
        for item in items.readlines():
            try:
                data.append(perekrestok_finder(item.strip()))
            except Exception as err:
                error_info = f"{type(err).__name__} was raised: {err}"
                data.append([error_info, error_info])
            time.sleep(random.randint(1,10))
    with open ("price_db.csv", "a") as db:
        db.write(current_datetime + "\t" + "\t".join([str(i[0]) for i in data]) + '\n')
        db.write(current_datetime + "\t" + "\t".join([str(i[1]) for i in data]) + '\n')
        
    ### request and write data with style (in SQLite database) ###
    
    # read data from DB
    con = sqlite3.connect('/home/alexey/Experiments/Fisherman_Bot/fisherman/fisherman.db')
    cur = con.cursor()
    logging.debug("Database read urls: open connection")
    cur.execute('''SELECT id, url FROM info''')
    db_info = cur.fetchall()
    con.close()
    logging.debug("Database read urls: close connection")
    
    
    # get data from the site
    data = []
    for ID, url in db_info:
        try:
            name, price = perekrestok_finder(url.strip())
        except Exception as err:
            logging.error("Site parser error: can't obtain data for %s, %s", url, err)
            continue
        print(ID, name)
        data.append({
            'id': ID,
            'price': price,
            'date': datetime.now().strftime("%m-%d-%Y %H:%M:%S") # ISO8601
        })
        time.sleep(random.randint(1,10))
    logging.info("Prices of %s items from %s were fetched successfully", len(data), len(db_info))
    
    # write prices to DB
    con = sqlite3.connect('/home/alexey/Experiments/Fisherman_Bot/fisherman/fisherman.db')
    cur = con.cursor()
    logging.debug("Database write prices: open connection")
    for entry in data:
        cur.execute('''INSERT INTO prices (id, datetime, price) VALUES (:id, :date, :price)''', entry)
    con.commit()
    con.close()
    logging.debug("Database write prices: close connection")
        