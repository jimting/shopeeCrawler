# Shopee Crawler

### 先備知識：
1. Docker
2. Python
3. 認識HTML與JSON
4. 認識API與知道如何使用Python的Flask(讓程式成為API的方法)

---

蝦皮的商品百百種，是否有個商品你每天都要查他？(例如最近的Switch)
**找看有沒有人上傳新商品這件事情，實在是太麻煩惹**

### 動機：寫一個自動幫我看有沒有人上傳新商品的爬蟲api

---

以下分為3個步驟。
1. pull這個專案：https://github.com/jimting/shopeeCrawler
2. 將他佈署在 你的server 上。
3. 套用在定時執行的程式 或 你寫的bot上。

---

## 1. pull步驟：專案程式碼

此專案有一些檔案，讓我來仔細說明各個檔案在幹麻：

![](https://i.imgur.com/uIcYj2d.png)

1. Dockerfile -> 佈署用的檔案 (dev只是方便開發用 都一樣La)
2. requirements -> 我會需要的套件們列表
3. app -> Python的Flask主程式
4. shopeeCrawler -> 我寫的爬蟲程式

如果想看更詳細的code可以點進去看：
https://colab.research.google.com/drive/1i5FHoSTneFLtS-e45CbnJHR0-7xiIdSL?usp=sharing

### JSON結構
利用一個JSONArray包著爬到的資料們，分別為下面各項。

```JSON
[
{
	"name": "效果升級 DRG 空濾 喇叭嘴 進氣喇叭口 鋁合金輕量化 DRG158 專用 DRG喇叭口 DRG空濾",
	"link": "https://shopee.tw/效果升級-DRG-空濾-喇叭嘴-進氣喇叭口-鋁合金輕量化-DRG158-專用-DRG喇叭口-DRG空濾-i.75158526.3916525269",
	"img": "https://cf.shopee.tw/file/1e4e35e2ca01592dcf8c645837aef5e4_tn",
	"sales_volume": 0,
	"price": "$500",
	"review": 0,
	"ad": false,
	"key": 145,
	"ad_num": 0
},
...
]
```

---

## 2. 若想將他佈署在你的server上

這步驟需要先把docker安裝好，不知道怎麼安裝就Google吧

安裝完輸下面兩個指令：

1. 

```
sudo docker build -t shopee_crawler:01 .
```
2. (記得改一下對外port)
```
sudo docker run -d --name shopee_crawler -e "TZ=Asia/Taipei" -p 你想要的對外port:5000 shopee_crawler:01
```

**看到佈署完成就可以用惹**

---

## 3. 應用層面：套用在你的bot上

舉例來說，我建立了一個bot幫我每天整點都做這件事情，只要有新的商品他就會跟我說。

![](https://i.imgur.com/rU55Fs9.png)

也可以寫一個定時執行的cronjob，讓程式自動幫你檢查是否有新商品。

---

當然，你也可以直接使用我的telegram bot，只要我的樹莓派還建在，他就會活著。

![](https://i.imgur.com/oljalg6.png)

[[點我加好友]](https://t.me/xiao_slave_bot)

[[bot code repo]](https://github.com/jimting/XiaoSlaveBot)
