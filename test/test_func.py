import json

"""   scrape   """
import requests
from bs4 import BeautifulSoup
import urllib

"""   origins   """

MERCARI = "https://www.mercari.com"
RAKUMA = "https://fril.jp"

players = {
    "CR7": {"team": "Ubentus", "number": 7, "nation": "Portugees", "position": "FW"},
    "Messi": {"team": "FCBarcelona", "number": 10, "nation": "Argentina", "position": "FW"},
    "Ibra": {"team": "AC Milan", "number": 11, "nation": "Sweden", "position": "FW"}
}

SC_HEADERS = {
    #"Origin": "https://www.mercari.com",
    #"Remote-Host": "localhost",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "no-cors",
    "Sec-Fetch-Site": "cross-site",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
    #"Referrer": "https://www.mercari.com/",
}

MER_CAT = ["-", "1-", "2-", "3-", "4-", "5-", "1328-", "6-", "1328-79", "1027-", "7-", "8-", "1318-", "9-", "10-112", "10-929", "10-929", "10-"]

RAK_CAT = ["", "10001", "10005", "10003", "10009", "10007", "10007", "10004", "10013", "10008", "10006", "10014", "10011", "10010", "1125", "1126", "1510", "10002"]

MER_SOLD = ["", "status_trading_sold_out=1", "status_on_sale=1"]

RAK_SOLD = ["", "&transaction=soldout", "&transaction=selling"]

"""   functions   """

def player_list():
    items = players
    return items
    
def search_history():
    pass

###########################
#      generate param     #
###########################

def mer_params(**kwargs):
    
    cat = int(kwargs.get("category"))
    sold = int(kwargs.get("sold"))
    
    cat_list = MER_CAT[cat].split("-")
    
    narrow = {
        "category_root": cat_list[0],
        "category_child": cat_list[1],
        "is_sold": MER_SOLD[sold],
    }
    
    return narrow
    
    
def rak_params(**kwargs):
    
    cat = int(kwargs.get("category"))
    sold = int(kwargs.get("sold"))
    
    narrow = {
        "category_id": RAK_CAT[cat],
        "transaction": RAK_SOLD[sold],
    }
    
    return narrow

###########################
#       scrape func       #
###########################

# scrape mercari
def mer_scrape(url_):
    lst_ = []
    headers = {
        "User-Agent": "Mozilla/.... Chrome/.... Safari/...."
    }
    #info = requests.get(url_, headers=headers)
    
    info = requests.get(url_, headers=SC_HEADERS, timeout=(3.0, 7.5))
    
    soup = BeautifulSoup(info.text, 'html.parser')
    
    for item in soup.select("section > a", limit=20):

        link_ = item.get("href")
        link_ = str(link_)
        name = item.find(class_="items-box-name").string
        price = item.find(class_="items-box-price").string
        
        sold = False
        if item.find(class_="item-sold-out-badge") is not None:
            sold = True
        
        dict_ = {
            "href": MERCARI + link_,
            "name": name,
            "price": price,
            "sold": sold,
        }
        lst_.append(dict_)
    
    return lst_
    
# scrape rakuma
def rak_scrape(url_):
    lst_ = []
    headers = {
        "User-Agent": "Mozilla/.... Chrome/.... Safari/...."
    }
    info = requests.get(url_, headers=headers)
    
    soup = BeautifulSoup(info.text, 'html.parser')
    
    for item in soup.select(".item-box", limit=20):
        dict_ = {}
        
        p_ = item.select("p", class_=".item-box__item-name")[0]
        a_ = p_.select("a")[0]
        name = a_.select("span")[0].string
        link_ = a_.get("href")
        
        price_p = item.select("p", class_="item-box__item-price")[1]
        price_span = price_p.select("span")[1].string
        
        sold = False
        if item.find(class_="item-box__soldout_ribbon") is not None:
            sold = True
        
        dict_ = {
            "href": link_,
            "name": name,
            "price": price_span,
            "sold": sold,
        }
        lst_.append(dict_)
    
    return lst_
    
def yahoo_scrape(url_):
    lst_ = []
    
    headers = {
        "User-Agent": "Mozilla/.... Chrome/.... Safari/...."
    }
    info = requests.get(url_, headers=headers)
    
    soup = BeautifulSoup(info.text, 'html.parser')
    
    for item in soup.select(".Product__detail", limit=20):
        det = item.select(".Product__titleLink")[0]
        link_ = det.get("href")
        name = det.string
        price_el = item.select(".Product__priceValue")[0]
        price = price_el.string
        
        dict_ = {
            "href": link_,
            "name": name,
            "price": price,
            "sold": False,
        }
        
        lst_.append(dict_)
        
    return lst_
    
###########################
#      generate list      #
###########################
    
# generate mercari list
def mercari_list(keyword_, **kwargs):
    keyword = urllib.parse.quote(keyword_)
    # spaceを+に変換
    keyword = keyword.replace("%20", "+")
    
    # narrow down dict
    narrow = mer_params(**kwargs)

    target_url = f'{MERCARI}/jp/search/?sort_order=&keyword={keyword}&category_root={narrow["category_root"]}&category_child={narrow["category_child"]}&brand_name=&brand_id=&size_group=&price_min=&price_max=&{narrow["is_sold"]}'
    
    lst = mer_scrape(target_url)
    return lst
    
# generate rakuma list
def rakuma_list(keyword_, **kwargs):
    keyword = urllib.parse.quote(keyword_)
    #target_url = "".join([RAKUMA, '/search/', keyword])
    
    # narrow down dict
    narrow = rak_params(**kwargs)
    
    target_url = f'{RAKUMA}/s?query={keyword}&category_id={narrow["category_id"]}{narrow["transaction"]}'
    
    lst = rak_scrape(target_url)
    return lst
    
# general yahoo list
def yahoo_list(keyword_):
    keyword = urllib.parse.quote(keyword_)
    # spaceを+に変換
    keyword = keyword.replace("%20", "+")
    
    target_url = "https://auctions.yahoo.co.jp/search/search?aq=-1&auccat=&ei=utf-8&fr=auc_top&oq=&p={}&sc_i=&tab_ex=commerce".format(keyword)
    lst = yahoo_scrape(target_url)
    
    return lst
    
def scrape_all(keyword_, **kwargs):
    
    dict_ = {
        "mercari": mercari_list(keyword_, **kwargs),
        "rakuma": rakuma_list(keyword_, **kwargs),
        "yahoo": yahoo_list(keyword_),
    }
    return dict_

def lambda_handler(event, context):
    OperationType = event["OperationType"]
    
    try:
        if OperationType == "LIST_PLAYERS":
            return {
                'statusCode': 200,
                'headers': {
                    "Content-Type": 'application/json',
                    "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",
                    "Access-Control-Allow-Methods": "POST, OPTION, GET",
                    "Access-Control-Allow-Origin": "*"
                },
                'body': json.dumps(player_list())
            }
        elif OperationType == "RAK_LIST":
            keyword_ = event["Keys"]["keyword"]
            narrowdown = event["Keys"]["narrowdown"]
            return rakuma_list(keyword_, **narrowdown)
        elif OperationType == "MER_LIST":
            keyword_ = event["Keys"]["keyword"]
            narrowdown = event["Keys"]["narrowdown"]
            return mercari_list(keyword_, **narrowdown)
        elif OperationType == "SCRAPE":
            keyword_ = event["Keys"]["keyword"]
            narrowdown = event["Keys"]["narrowdown"]
            return scrape_all(keyword_, **narrowdown)
        elif OperationType == "YAHOO_LIST":
            keyword_ = event["Keys"]["keyword"]
            return yahoo_list(keyword_)
            
    except Exception as e:
        print("Error: ")
        print(e)