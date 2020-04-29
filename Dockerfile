FROM python:3.6
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN chmod 755 chromedriver
RUN apt-get update
RUN apt-get install -y chromium-driver
CMD python app.py