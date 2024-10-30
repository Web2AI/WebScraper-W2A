FROM python:3.12.2

RUN useradd -m flask
USER flask

WORKDIR /w2a-scraper/app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

ENV FLASK_APP=app
ENV FLASK_ENV=development

EXPOSE 5000

WORKDIR /w2a-scraper/app/src

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]