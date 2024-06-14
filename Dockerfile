FROM python:3.12.2

WORKDIR /w2a-scraper/app

COPY config/requirements.txt config/requirements.txt
RUN pip3 install -r config/requirements.txt

COPY . .

ENV FLASK_APP=src.app
ENV FLASK_ENV=development

EXPOSE 5000

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]