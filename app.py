from flask import Flask, jsonify, request
from flask_cors import CORS
import numpy as np
import pandas as pd

import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return "<h1>Hello Flask!</h1>"

@app.route('/crawler_shopee')
def shopee():
    import json

    if 'keyword' in request.args:
        keyword = request.args['keyword']
    else:
        keyword = '筆記型電腦'

    # keyword = '筆記型電腦'
    shopee_product_ad = crawler_shopee_product_ad(keyword)
    shopee_product_info = crawler_shopee_product_info(keyword)

    for i in range(len(shopee_product_ad)):
        product_ad = shopee_product_ad.iloc[i]['name']
        shopee_product_info.loc[shopee_product_info['name'] == product_ad, 'ad'] = True
      
    ad_num = len(shopee_product_ad)
    print(keyword + '有 {} 個廣告'.format(ad_num))
    shopee_product_info['sales_volume'] = shopee_product_info['sales_volume'].astype('int')
    shopee_product_info = shopee_product_info.sort_values(by='sales_volume', ascending=False)
    shopee_product_info['key'] = range(1, len(shopee_product_info) + 1) # 增加 index 欄位
    shopee_product_info['ad_num'] = ad_num

    return shopee_product_info.to_json(orient='records', force_ascii=False)
    # return json.dumps([{
    #     'ad_num': ad_num,
    #     'data': shopee_product_info.to_json(orient='records', force_ascii=False)
    # }])
    # return keyword

# 取得頁面html資料
def fetch_page(keyword = '', page = 0):
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions
    from selenium.webdriver.common.by import By
    from bs4 import BeautifulSoup
    import time
    import os
    import pymysql.cursors
    import re

    # 給 heroku 使用
    chrome_options = webdriver.ChromeOptions()
    chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("window-size=1920,1080")
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)

    # 本地開發使用
    # options = Options()
    # options.add_argument("window-size=1920,1080")
    # options.add_argument("--headless")  # 不要開啟瀏覽器
    # # options.add_argument('--no-sandbox')  # 以最高权限运行
    # # 谷歌文档提到需要加上这个属性来规避bug
    # options.add_argument('--disable-gpu')
    # #设置不加载图片
    # options.add_argument("blink-settings=imagesEnabled=false")
    # driver = webdriver.Chrome('./chromedriver',options=options)
    # driver.maximize_window()  # 瀏覽器視窗設為最大

    url = 'https://shopee.tw/search?keyword={0}&page={1}&sortBy=sales'.format(keyword, page)
    print('url = ', url)

    driver.get(url)

    # 等待選單內容出現
    element = WebDriverWait(driver, 5).until(
        expected_conditions.presence_of_element_located((By.CLASS_NAME, "shopee-search-item-result__item"))
    )

    # 頁面往下滑動
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    # 取得內容
    soup = BeautifulSoup(driver.page_source, 'lxml')
    
    driver.close()
    return soup
        
# 從html取出商品array
def get_article_arr(page_html):
    article_arr = []
    host = 'https://shopee.tw'
    ad_articles = page_html.select('[data-sqe="ad"]')
    ad_articles_len = len(ad_articles)

    for article in ad_articles:
        try:
            article = article.parent.parent.parent.parent.parent.parent  # 回到 .shopee-search-item-result__item 那層
            name = article.select('[data-sqe="name"]')[0].text
            ad = True if len(article.select('[data-sqe="ad"]')) > 0 else False
            article_arr.append({
                'name': name,
                'ad': ad
            })
        except Exception as e:
            print(e)
            print('---')
            
    return article_arr

# 設置爬取的關鍵字，及從第幾頁開始爬
# 回傳商品 df
def crawler_shopee_product_ad(keyword = '', page = 0):
    is_fetch_next_page = True # 判斷是否繼續爬下一頁
    df_article_total_arr = pd.DataFrame([])
    
    while is_fetch_next_page:
        page_html = fetch_page(keyword, page)
        article_arr = get_article_arr(page_html)
        df_article_arr = pd.DataFrame(article_arr)
        df_article_total_arr = pd.concat([df_article_total_arr, df_article_arr], ignore_index=True)
        if len(df_article_arr) < 10:
            is_fetch_next_page = False
        page += 1

    return df_article_total_arr

# 設置爬取的關鍵字，及從第幾頁開始爬
# 回傳商品 df
def crawler_shopee_product_info(keyword = '', page = 1):
    import pandas as pd
    import re
    
    article_arr = []
    host = 'https://shopee.tw'
    
    for i in range(page):
        url = 'https://shopee.tw/search?keyword={0}&page={1}&sortBy=sales'.format(keyword, i)
        print(url)
        headers = {
            'user-agent': 'Googlebot'
        }
        resp = requests.get(url, headers=headers) 
        soup = BeautifulSoup(resp.text, 'lxml')

        articles = soup.select('.shopee-search-item-result__item')
        for article in articles:
            name = article.select('[data-sqe="name"]')[0].text
            link = host + article.select('a')[0]['href']
            img = article.select('a > div > div > img')[0]['src']
            sales_volume = '0' if article.select('[data-sqe="rating"]')[0].next_sibling.text == '' else article.select('[data-sqe="rating"]')[0].next_sibling.text
            sales_volume = re.findall(r'\d+', sales_volume)[0]
            review = len(article.select('.shopee-rating-stars__stars .shopee-rating-stars__star-wrapper'))
            price = article.select('[data-sqe="name"]')[0].next_sibling.text.replace('$', '').replace(',', '')
            if len(price.split(' - ')) != 1:
                price = (int(price.split(' - ')[0]) + int(price.split(' - ')[1])) / 2
            monthly_revenue = float(sales_volume) * float(price)

            article_arr.append({
                'name': name,
                'link': link,
                'img': img,
                'sales_volume': sales_volume,  # 月銷售量
                'price': price,  # 單價
                'monthly_revenue': monthly_revenue,  # 月收加總
                'review': review,  # 評價
                'ad': False
            })

    df = pd.DataFrame(article_arr, columns=['name', 'link', 'img', 'sales_volume', 'price', 'monthly_revenue', 'review', 'ad'])  # 使用 columns 調整排列順序
    return df

if __name__ == '__main__':
  app.config["DEBUG"] = True
  app.config["JSON_AS_ASCII"] = False
  app.run()
