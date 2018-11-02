#!/usr/bin/env python3

from collections import deque
from sanic import Sanic
from sanic.response import json
from sanic_compress import Compress
from sanic_cors import CORS
from threading import RLock, Thread
import requests
import time


_REFRESH_TIMEOUT = 60
_UPSTREAM = 'https://api.github.com/repos/mozilla-iot/gateway/releases'
_LIST = None
_LOCK = RLock()
_REQUESTS = deque()


# Refresh the release list every 60 seconds
def update_list():
    global _LIST

    while True:
        # Pull the latest release list
        try:
            r = requests.get(_UPSTREAM)
            if r.status_code == 200:
                with _LOCK:
                    _LIST = r.json()

            # Clear out old items from the request list
            one_day_ago = time.time() - (24 * 60 * 60)
            while len(_REQUESTS) > 0:
                req = _REQUESTS.popleft()
                if req[0] >= one_day_ago:
                    _REQUESTS.appendleft(req)
                    break
        except Exception as e:
            print(e)
            pass

        # Sleep for a bit to avoid Github's rate limiting
        time.sleep(_REFRESH_TIMEOUT)


# Create the sanic app
app = Sanic()
Compress(app)
CORS(app)


# Serve the list
@app.route('/releases')
async def get_list(request):
    _REQUESTS.append((time.time(), request.headers.get('User-Agent', None)))

    with _LOCK:
        return json(_LIST)


# Analytics route
@app.route('/releases/analytics')
async def analytics(request):
    requests = {}
    total = 0
    for req in _REQUESTS:
        ua = req[1]
        if ua not in requests:
            requests[ua] = 1
        else:
            requests[ua] += 1

        total += 1

    requests['total'] = total
    return json(requests)


if __name__ == '__main__':
    t = Thread(target=update_list)
    t.daemon = True
    t.start()

    # Wait for the list to be populated before starting the server
    while _LIST is None:
        time.sleep(.1)

    app.run(host='0.0.0.0', port=80)
