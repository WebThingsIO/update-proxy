FROM python:3.6

RUN pip3 install sanic requests
COPY update-proxy.py /update-proxy.py

ENTRYPOINT ["/update-proxy.py"]
