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

# 設置爬取的關鍵字，及抓到幾頁 (抓前三頁新的就好XD)
# 回傳商品 df
def crawler_shopee_product_info(keyword, page = 3):
	article_arr = []
	host = 'https://shopee.tw'
	
	for i in range(page):
		soup = fetch_page(keyword, i)
		articles = soup.select('[data-sqe="item"]')
		articles_len = len(articles)
		if articles_len == 0 : 
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
				price = article.select('[data-sqe="name"]')[0].next_sibling.text
				ad = False
				#print(str(article))
				if article.select('[data-sqe="ad"]'): 
					ad = True 
				if ad == False : #直接把廣告過濾掉，因為沒有用QQ
					article_arr.append({
						'name': name,
						'link': link,
						'img': img,
						'sales_volume': sales_volume,  # 月銷售量
						'price': price,	 # 單價
						'review': review,  # 評價
						'ad': ad
					})
			except Exception as e:
				print(e)
				print('---')

	df = pd.DataFrame(article_arr, columns=['name', 'link', 'img', 'sales_volume', 'price', 'review', 'ad'])	 # 使用 columns 調整排列順序
	return df
