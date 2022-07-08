import requests
import re
import time
import random
from datetime import datetime

# price request function
def perekrestok_finder(source_url):
    """
    Parse Perekrestok page, find information aboutitem and return name and price
    """
    
    import requests
    import re
    
    res = requests.get(source_url)
    if not res:
        return None, None        
    elif res.status_code == 200:
        # print(res.text)
        price = re.findall('<div class="price-new">(.*?)</div>' ,res.text)[0]
        title = re.findall('<title data-react-helmet="true">(.*?) - купить с .*? в Перекрёстке</title>', res.text)[0]
        price = re.sub(",", ".", price[:-2])
        return title, price
    else:
        raise ValueError(f"Non-200 request code - {res.status_code}")
        
        
# request and write data
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