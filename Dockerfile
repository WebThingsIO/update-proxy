FROM python:3.7

RUN pip3 install sanic==18.12 sanic_compress sanic-cors requests
COPY update-proxy.py /update-proxy.py

ENTRYPOINT ["/update-proxy.py"]
