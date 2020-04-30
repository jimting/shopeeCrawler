FROM shopee_crawler:latest
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN chmod 755 chromedriver
CMD python app.py