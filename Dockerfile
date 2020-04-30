FROM shopee_crawler:latest
COPY . /app
WORKDIR /app
RUN chmod 755 chromedriver
CMD python app.py