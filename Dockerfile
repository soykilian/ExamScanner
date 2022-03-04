#docker container run -d \
# -it \
# -p 5000:5000 \
# --name lector-plantillas \
# mguarinos/lector-plantillas \
# python3 server.py \
# "pruebasSDG2@gmail.com" \
# "manolete" \
# "smtp.gmail.com" \
# 465

#docker build -t mguarinos/lector-plantillas .

FROM python:3.8-buster

EXPOSE 5000

RUN pip3 install \
  requests \
  numpy \
  opencv-contrib-python-headless \
  Flask \
  Flask-Cors \
  Flask-AutoIndex \
  pandas

WORKDIR /app
COPY . .

CMD python server.py
