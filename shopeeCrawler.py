from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import time

def shopeeSearch (keyword) :

	shopee_product_info = crawler_shopee_product_info(keyword)

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
	driver.maximize_window()

	# 等待選單內容出現
	time.sleep(5)

	# 頁面往下滑動
	driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
	time.sleep(5)

	# 取得內容
	soup = BeautifulSoup(driver.page_source, 'lxml')
	
	driver.close()
	return soup

# 設置爬取的關鍵字，及從第幾頁開始爬
# 回傳商品 df
def crawler_shopee_product_info(keyword, page = 20):
	import pandas as pd
	import re
	
	article_arr = []
	host = 'https://shopee.tw'
	
	for i in range(page):
		soup = fetch_page(keyword, i)
		articles = soup.select('[data-sqe="item"]')
		articles_len = len(articles)
		if articles_len < 20 : 
			break
		for article in articles:
			try:
				name = article.select('[data-sqe="name"] > div')[0].text
				link = host + article.select('a')[0]['href']
				#img = article.select('a > div > div > img')[0]['src']
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
					#'img': img,
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