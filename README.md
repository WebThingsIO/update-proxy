# update-proxy

This is the server used to proxy gateway releases from GitHub.

## Usage

```sh
pip3 install -r requirements.txt
./update-proxy.py
```

## Data Stored

The only data stored by this server is the user-agent, which, when coming from
the gateway, is something like:
```
webthings-gateway/1.0.0 (linux-arm; linux-raspbian)
```
