FROM python:3.8

RUN pip3 install sanic sanic-gzip requests
RUN pip3 install --pre 'sanic-cors>0.9.99'
COPY update-proxy.py /update-proxy.py

ENTRYPOINT ["/update-proxy.py"]
