from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

import time
import base64
import json
import requests
import pandas as pd

def shopeeSearch (keyword) :

	#shopee_product_ad = crawler_shopee_product_ad(keyword)
	shopee_product_info = crawler_shopee_product_ad(keyword)

	# for i in range(len(shopee_product_info)):
		# product_ad = shopee_product_ad.iloc[i]['name']
		# shopee_product_info.loc[shopee_product_info['name'] == product_ad, 'ad'] = True
	  
	#ad_num = len(shopee_product_ad)
	# print(keyword + '有 {} 個廣告'.format(ad_num))
	shopee_product_info['sales_volume'] = shopee_product_info['sales_volume'].astype('int')
	shopee_product_info = shopee_product_info.sort_values(by='sales_volume', ascending=False)
	shopee_product_info['key'] = range(1, len(shopee_product_info) + 1) # 增加 index 欄位
	shopee_product_info['ad_num'] = 0

	return shopee_product_info.to_json(orient='records', force_ascii=False)

def fetch_page (keyword, page) :
	options = Options()
	options.headless = True
	options.add_argument("--no-sandbox")
	options.add_argument("--disable-dev-shm-usage")
	driver = Chrome(chrome_options=options)

	url = 'https://shopee.tw/search?keyword={0}&page={1}&sortBy=sales'.format(keyword, page)
	print('url = ', url)

	driver.get(url)

	# 等待選單內容出現
	element = WebDriverWait(driver, 5).until(
		expected_conditions.presence_of_element_located((By.CLASS_NAME, "shopee-search-item-result__item"))
	)

	# 頁面往下滑動
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	time.sleep(5)

	# 取得內容
	soup = BeautifulSoup(driver.page_source, 'lxml')
	
	driver.close()
	return soup
	
# 從html取出商品array
def get_article_arr(page_html):
	article_arr = []
	host = 'https://shopee.tw'
	ad_articles = page_html.select('[data-sqe="item"]')
	ad_articles_len = len(ad_articles)

	for article in ad_articles:
		try:
			article = article.parent.parent.parent.parent.parent.parent	 # 回到 .shopee-search-item-result__item 那層
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
def crawler_shopee_product_ad(keyword, page = 0):
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
def crawler_shopee_product_info(keyword, page = 1):
	import pandas as pd
	import re
	
	article_arr = []
	host = 'https://shopee.tw'
	
	for i in range(page):
		# url = 'https://shopee.tw/search?keyword={0}&page={1}&sortBy=sales'.format(keyword, i)
		# print(url)
		# headers = {
		#	 'user-agent': 'Googlebot'
		# }
		# resp = requests.get(url, headers=headers) 
		soup = fetch_page(keyword, i)

		articles = soup.select('[data-sqe="item"]')
		for article in articles:
			try:
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
					'price': price,	 # 單價
					'monthly_revenue': monthly_revenue,	 # 月收加總
					'review': review,  # 評價
					'ad': False
				})
			except Exception as e:
				article_arr.append({
					'name': e,
					'link': "沒有link",
					'img': "錯誤用的img-src",
					'sales_volume': 999,  # 月銷售量
					'price': 999,	 # 單價
					'monthly_revenue': 999,	 # 月收加總
					'review': 5,  # 評價
					'ad': False
				})
				print(e)
				print('---')

	df = pd.DataFrame(article_arr, columns=['name', 'link', 'img', 'sales_volume', 'price', 'monthly_revenue', 'review', 'ad'])	 # 使用 columns 調整排列順序
	return df
