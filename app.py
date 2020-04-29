from flask import *
from datetime import datetime
import shopeeCrawler as service
app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    data = "Success"
    return data

@app.route('/shopeeCrawler')
def shopeeCrawler():
    keywords = str(request.args.get('keywords'))
    page = str(request.args.get('page'))
    result = service.shopeeSearch(keywords,page)
    return result

@app.route('/test')
def test():
    result = service.test()
    return result


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)