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


"""   functions   """

def player_list():
    items = players
    return items
    
def search_history():
    pass

# scrape mercari
def mer_scrape(url_):
    lst_ = []
    headers = {
        "User-Agent": "Mozilla/.... Chrome/.... Safari/...."
    }
    info = requests.get(url_, headers=headers)
    
    soup = BeautifulSoup(info.text, 'html.parser')
    
    for item in soup.select("section > a", limit=20):

        link_ = item.get("href")
        link_ = str(link_)
        name = item.find(class_="items-box-name").string
        price = item.find(class_="items-box-price").string
        
        dict_ = {
            "href": MERCARI + link_,
            "name": name,
            "price": price,
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
    
    for item in soup.select(".item-box__text-wrapper", limit=20):
        dict_ = {}
        
        p_ = item.select("p", class_=".item-box__item-name")[0]
        a_ = p_.select("a")[0]
        name = a_.select("span")[0].string
        link_ = a_.get("href")
        
        price_p = item.select("p", class_="item-box__item-price")[1]
        price_span = price_p.select("span")[1].string
        
        
        dict_ = {
            "href": link_,
            "name": name,
            "price": price_span,
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
        }
        
        lst_.append(dict_)
        
    return lst_
    
# generate mercari list
def mercari_list(keyword_):
    keyword = urllib.parse.quote(keyword_)
    # spaceを+に変換
    keyword = keyword.replace("%20", "+")
    target_url = "".join([MERCARI, '/jp/search/', '?keyword=', keyword])
    
    lst = mer_scrape(target_url)
    return lst
    
# generate rakuma list
def rakuma_list(keyword_):
    keyword = urllib.parse.quote(keyword_)
    target_url = "".join([RAKUMA, '/search/', keyword])
    
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
    
def scrape_all(keyword_):
    
    dict_ = {
        "mercari": mercari_list(keyword_),
        "rakuma": rakuma_list(keyword_),
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
            return rakuma_list(keyword_)
        elif OperationType == "MER_LIST":
            keyword_ = event["Keys"]["keyword"]
            return mercari_list(keyword_)
        elif OperationType == "SCRAPE":
            keyword_ = event["Keys"]["keyword"]
            return scrape_all(keyword_)
        elif OperationType == "YAHOO_LIST":
            keyword_ = event["Keys"]["keyword"]
            return yahoo_list(keyword_)
            
    except Exception as e:
        print("Error: ")
        print(e)