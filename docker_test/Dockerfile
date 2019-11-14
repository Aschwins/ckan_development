FROM ubuntu

RUN apt-get -y update \ 
    && apt-get -y upgrade python3 \
    && apt-get -y install python3-pip

COPY app .
COPY requirements.txt .
RUN pip3 install -r requirements.txt

RUN ls

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8 FLASK_APP=app.py FLASK_ENV=development

CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]

# docker build . -t flask-example

# docker run -p 5000:5000 flask-example