from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

import pandas as pd
import re
import requests
import time

def shopeeSearch (keyword) :

	shopee_product_info = crawler_shopee_product_info(keyword)

	shopee_product_info['sales_volume'] = shopee_product_info['sales_volume'].astype('int')
	shopee_product_info = shopee_product_info.sort_values(by='sales_volume', ascending=False)
	shopee_product_info['key'] = range(1, len(shopee_product_info) + 1) # 增加 index 欄位
	shopee_product_info['ad_num'] = 0

	return shopee_product_info.to_json(orient='records', force_ascii=False)

def shopeeDeepSearch (keyword) :
	shopee_product_info = deep_crawler_shopee_product_info(keyword)

	shopee_product_info['sales_volume'] = shopee_product_info['sales_volume'].astype('int')
	shopee_product_info = shopee_product_info.sort_values(by='sales_volume', ascending=False)
	shopee_product_info['key'] = range(1, len(shopee_product_info) + 1) # 增加 index 欄位
	shopee_product_info['ad_num'] = 0

	return shopee_product_info.to_json(orient='records', force_ascii=False)

def fetch_page(keyword, page):
  url = 'https://shopee.tw/search?keyword='+keyword+"&page="+str(page)+"&sortBy=ctime"
  headers = {
      'User-Agent': 'Googlebot',
      'From': ''
  }

  r = requests.get(url,headers=headers,allow_redirects=True)
  print(r.status_code)
  print(r.history)
  print(r.url)

  soup = BeautifulSoup(r.text, 'html.parser')
  return soup

# 設置爬取的關鍵字，及從第幾頁開始爬
# 回傳商品 df
def crawler_shopee_product_info(keyword, page = 20):
	article_arr = []
	host = 'https://shopee.tw'
	
	for i in range(page):
		soup = fetch_page(keyword, i)
		articles = soup.select('[data-sqe="item"]')
		articles_len = len(articles)
		if articles_len < 10 : 
			print('last page')
			break
		for article in articles:
			try:
				name = article.select('[data-sqe="name"] > div')[0].text
				link = host + article.select('a')[0]['href']
				img = article.select('a > div > div > img')[0]['src']
				sales_volume = '0' if article.select('[data-sqe="rating"]')[0].next_sibling.text == '' else article.select('[data-sqe="rating"]')[0].next_sibling.text
				sales_volume = re.findall(r'\d+', sales_volume)[0]
				review = len(article.select('.shopee-rating-stars__stars .shopee-rating-stars__star-wrapper'))
				price = article.select('[data-sqe="name"]')[0].next_sibling.text.replace('$', '').replace(',', '')
				ad = False
				if len(article.select('[data-sqe="ad"]')) > 0 : 
					ad = True 
				if len(price.split(' - ')) != 1:
					price = (int(price.split(' - ')[0]) + int(price.split(' - ')[1])) / 2
				monthly_revenue = float(sales_volume) * float(price)

				article_arr.append({
					'name': name,
					'link': link,
					'img': img,
					'sales_volume': sales_volume,  # 月銷售量
					'price': price,	 # 單價
					'monthly_revenue': monthly_revenue,	 # 月收加總
					'review': review,  # 評價
					'ad': ad
				})
			except Exception as e:
				print(e)
				print('---')

	df = pd.DataFrame(article_arr, columns=['name', 'link', 'img', 'sales_volume', 'price', 'monthly_revenue', 'review', 'ad'])	 # 使用 columns 調整排列順序
	return df

# 深度搜尋 設定頁數為100頁
def deep_crawler_shopee_product_info(keyword, page = 100):
	article_arr = []
	host = 'https://shopee.tw'
	
	for i in range(page):
		soup = fetch_page(keyword, i)
		articles = soup.select('[data-sqe="item"]')
		articles_len = len(articles)
		if articles_len < 10 : 
			print('last page')
			break
		for article in articles:
			try:
				name = article.select('[data-sqe="name"] > div')[0].text
				link = host + article.select('a')[0]['href']
				img = article.select('a > div > div > img')[0]['src']
				sales_volume = '0' if article.select('[data-sqe="rating"]')[0].next_sibling.text == '' else article.select('[data-sqe="rating"]')[0].next_sibling.text
				sales_volume = re.findall(r'\d+', sales_volume)[0]
				review = len(article.select('.shopee-rating-stars__stars .shopee-rating-stars__star-wrapper'))
				price = article.select('[data-sqe="name"]')[0].next_sibling.text.replace('$', '').replace(',', '')
				ad = False
				if len(article.select('[data-sqe="ad"]')) > 0 : 
					ad = True 
				if len(price.split(' - ')) != 1:
					price = (int(price.split(' - ')[0]) + int(price.split(' - ')[1])) / 2
				monthly_revenue = float(sales_volume) * float(price)
				
				if(!ad) #直接把廣告過濾掉，因為沒有用QQ
				{
					article_arr.append({
						'name': name,
						'link': link,
						'img': img,
						'sales_volume': sales_volume,  # 月銷售量
						'price': price,	 # 單價
						'monthly_revenue': monthly_revenue,	 # 月收加總
						'review': review,  # 評價
						'ad': ad
					})
				}
			except Exception as e:
				print(e)
				print('---')

	df = pd.DataFrame(article_arr, columns=['name', 'link', 'img', 'sales_volume', 'price', 'monthly_revenue', 'review', 'ad'])	 # 使用 columns 調整排列順序
	return df