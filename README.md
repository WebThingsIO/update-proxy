# update-proxy

This is the server used to proxy gateway releases from GitHub.

## Usage

```sh
pip install sanic sanic-gzip requests
pip install --pre 'sanic-cors>0.9.99'
./update-proxy.py [port]
```

## Data Stored

The only data stored by this server is the user-agent, which, when coming from
the gateway, is something like:
```
mozilla-iot-gateway/0.6.0
```
