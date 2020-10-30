FROM python:3.9

COPY update-proxy requirements.txt /app/
RUN pip3 install --no-cache-dir -r /app/requirements.txt

ENTRYPOINT ["/app/update-proxy.py"]
