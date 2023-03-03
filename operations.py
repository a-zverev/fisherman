import sqlite3
import requests
import re
import time
import random
from datetime import datetime
# from watchdog import perekrestok_finder
import logging

from config import DB_ADDRESS_OPERATIONS


def add_item_to_database(url, user):
    """
    Add a new item to watchlist of user. Add user and ID to table of users. If the url is not in the items_info table,
    add it to items_info table too.
    """
    
    # get info
    try:
        res = perekrestok_finder(url)
        data = {
            'name': res[0],
            'url': url,
            'user': user
        }
    except Exception as err:
        logging.error("Database write new entry: can't obtain data for %s, %s", url, err)
        return "Parsing_error"
    

    # read data from DB
    con = sqlite3.connect(DB_ADDRESS_OPERATIONS)
    cur = con.cursor()
    logging.debug("Database write new entry: open connection")
    
    # check if this url already in the database
    cur.execute('''SELECT id, url FROM items_info WHERE url = :url''', data)
    if not cur.fetchall():
        cur.execute('''INSERT INTO items_info (url, name) VALUES (:url, :name)''', data)
        logging.info(f"Table ITEMS_INFO write new entry: new item was added to the database: {data['name']}")
    cur.execute('''SELECT id FROM items_info WHERE url = :url''', data)
    data['ID'] = cur.fetchone()[0]
    
    # check, is this user already in the database
    cur.execute('''SELECT id, user FROM monitors WHERE user = :user AND id = :ID''', data)
    if not cur.fetchall():
        cur.execute('''INSERT INTO monitors (id, user) VALUES (:ID, :user)''', data)
        logging.info(f"Table MONITORS write new entry: id {data['ID']} was added for {data['user']}")
        answer = "Added"
    else:
        answer = "Already_exist"
    
    # write entries to DB
    con.commit()
    con.close()
    logging.debug("Database write new entry: close connection")
    
    return answer


def get_list_of_items_on_watch(user):
    """
    Return list of id/names for current user
    """
    
    # read data from DB
    con = sqlite3.connect(DB_ADDRESS_OPERATIONS)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    logging.debug("Database fetch data: open connection")
    
    # select id and names for current user
    cur.execute('''SELECT id, name FROM items_info WHERE id IN (SELECT id FROM monitors WHERE user = ?)''', [user])
    data = cur.fetchall()
    
    # close DB
    con.close()
    logging.debug("Database fetch data: close connection")
    
    return [dict(i) for i in data]

    
def remove_item_from_watch(ID, user):
    """
    Remove id/user from monitors table. If no one watches this ID, remove it completely (from monitors and items_info tables)
    """
    
    data = {
        "ID": ID,
        "user": user
    }
        
    # read data from DB
    con = sqlite3.connect(DB_ADDRESS_OPERATIONS)
    cur = con.cursor()
    logging.debug("Database remove data: open connection")
    
    # is this id in user watch list?
    cur.execute('''SELECT id, user FROM monitors WHERE id = :ID AND user = :user''', data)
    if not cur.fetchone():
        answer = "Not_in_list"
    else:
        cur.execute('''DELETE FROM monitors WHERE id = :ID AND user = :user''', data)
        logging.info(f"Table MONITORS remove data: removed id {ID} for user {user}")
    
        # is this id an orphan now?
        cur.execute('''SELECT id, user FROM monitors WHERE id = :ID''', data)
        if not cur.fetchone():
            cur.execute('''DELETE FROM items_info WHERE id = :ID''', data)
            logging.info(f"Table ITEMS_INFO remove data: id {ID} COMPLETELY REMOVED for all users")
        answer = "Removed"
    
    # close DB
    con.commit()
    con.close()
    logging.debug("Database remove data: close connection")
    return answer


def get_list_of_profits_for_user(user, abs_profit_threshold=10):
    """
    Stat information for . 
     dict with keys - 'id', 'name', 'mean_price', 'datetime' (last date),
                     'price_last', 'abs_profit', 'rel_profit'
    """
    
    # read data from DB
    con = sqlite3.connect(DB_ADDRESS_OPERATIONS)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    logging.debug("Database fetch data: open connection")
    
    # select id and names for current user
    cur.execute('''SELECT * FROM stats 
    LEFT JOIN (SELECT id, name FROM items_info)
    USING (id)
    WHERE id IN (SELECT id FROM monitors WHERE user = ?)
    AND
    abs_profit >= ?
    ORDER BY abs_profit DESC''', [user, abs_profit_threshold])
    data = cur.fetchall()
    
    # close DB
    con.close()
    logging.debug("Database fetch data: close connection")
    
    return [dict(i) for i in data]


def add_demo_for_user(user):
    con = sqlite3.connect(DB_ADDRESS_OPERATIONS)
    cur = con.cursor()
    for i in range(1, 120, 5):
        cur.execute('''INSERT OR IGNORE INTO monitors (id, user) VALUES (:id, :user)''', {'id': str(i), 'user': user})
    con.commit()
    con.close()
    return True