from flask import *
from datetime import datetime
import shopeeCrawler as service
app = Flask(__name__)


@app.route('/')
def index():
    data = "Success"
    return data

@app.route('/shopeeCrawler')
def shopeeCrawler():
    keywords = str(request.args.get('keywords'))
    result = service.shopeeSearch(keywords)
    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)