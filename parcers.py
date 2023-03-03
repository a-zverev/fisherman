from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from config import USER_AGENT
from config import accio_price_tags


# There are parcers for different online shops.
# ARGS: url, debug=False
# url. Use an URL as the unput. Validate them first - parcers trust you.
# debug. If debug, parcer will save a screenshot and html content of the site. Both will be owerwritten by next parcer call
#
# There are no specific exeptions rising right now - catch wide non-specific exception during parcing
#
# RES: dict with keys: url, title, is_avaliable, is_onsale, price

    
def perekrestok_parcer(url, debug=False):
    """
    Parce perekrestok
    """
    
    res = {} # url, title, is_avaliable, is_onsale, price
    
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1024,768')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument(USER_AGENT)
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    
    # confirm, if the item is an alcohol
    element = driver.find_element(By.CLASS_NAME, "adult-modal-button")
    if element.is_displayed():
        element.click()

    res['url'] = driver.current_url
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    if debug:
        url_id = str(driver.current_url)[-7:]
        driver.save_screenshot(f'debug/perekrestok_debug_{url_id}.png')
        with open(f'debug/perekrestok_debug_{url_id}.html', 'w') as file:
            file.write(driver.page_source)
            
    driver.close()
    
    res['title'] = soup.title.text[:-42].strip()
    res['is_onsale'] = False
    if "Этот товар закончился" not in soup.text:
        res['is_avaliable'] = True
        res['price'] = float(
            soup.body.find("div", {"class": "product-panel"}).find("div", {"class": "price-new"}).
            text[:-2].
            replace(",", ".")
        )
        if soup.body.find("div", {"class": "product-panel"}).find("div", {"class": "price-old"}):
            res['is_onsale'] = True     
    else:
        res['is_avaliable'] = False
    return res


def ozon_parser(url, debug=False):
    """
    Parce Ozon
    """
    
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1024,768')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument(USER_AGENT)
    
    driver = webdriver.Chrome(options=options)
    driver.get(url)
        
    if debug:
        driver.save_screenshot('ozon_debug.png')
        with open('ozon_debug.html', 'w') as file:
            file.write(html_content)
        
    html_content = driver.page_source
    url = driver.current_url
    driver.close()
    soup = BeautifulSoup(html_content, 'html.parser')  
    res = {} # url, title, is_avaliable, is_onsale, price
    
    if "товар закончился" and "не доставляется" not in soup.text:
        
        # Ozon price tags are dynamic. Damn them! How I get ones? 
        # While I'm not in Ozon payroll, I don't want them to know :)
        tags = accio_price_tags(soup)
        
        # two tags mean item on sale. for example, "yn9 y9n"
        # one tag means regular price
        res['is_onsale'] = len(tags) > 1
        
        if debug:
            print(tags)
        
        res['url'] = url.split("?")[0][:-1]
        res['title'] = soup.h1.text.strip()
        res['is_avaliable'] = True
        res['price'] = float(soup.find("span", {"class": tags[0] if res['is_onsale'] else tags}).
                                 text[:-2].
                                encode('ascii', 'ignore')
                                )
    else:
        res['is_avaliable'], res['is_onsale'] = False, False
        res['price'], res['title'], res['url'] = None, None, None
    return res