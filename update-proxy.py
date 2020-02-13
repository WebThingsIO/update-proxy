#!/usr/bin/env python3

"""
Update proxy server.

This server reads a list of releases from GitHub and serves them back to the
gateway.
"""

from collections import deque
from sanic import Sanic
from sanic.response import json as response_json
from sanic_cors import CORS
from sanic_gzip import Compress
from threading import RLock, Thread
import argparse
import requests
import time


_DEFAULT_PORT = 80
_DEFAULT_UPSTREAM = 'https://api.github.com/repos/mozilla-iot/gateway/releases'

_REFRESH_TIMEOUT = 60
_LIST = None
_LOCK = RLock()
_REQUESTS = deque()


def update_list(repo):
    """
    Update the list.

    This will pull the list of releases from the repo periodically.

    repo -- the GitHub repo
    """
    global _LIST

    while True:
        # Pull the latest release list
        try:
            r = requests.get(repo)
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
app = Sanic('update-proxy')
CORS(app)
compress = Compress()


# Serve the list
@app.route('/releases')
@compress.compress()
async def get_list(request):
    """Get the release list."""
    ua = request.headers.get('User-Agent', None)
    _REQUESTS.append((time.time(), ua))

    with _LOCK:
        return response_json(_LIST)


# Analytics route
@app.route('/releases/analytics')
@compress.compress()
async def analytics(request):
    """Return some analytics."""
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
    return response_json(requests)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Update proxy server for WebThings Gateway'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=_DEFAULT_PORT,
        help='port for server',
    )
    parser.add_argument(
        '--upstream',
        type=str,
        default=_DEFAULT_UPSTREAM,
        help='URL of release list',
    )
    args = parser.parse_args()

    t = Thread(target=update_list, args=(args.upstream,))
    t.daemon = True
    t.start()

    # Wait for the list to be populated before starting the server
    while _LIST is None:
        time.sleep(.1)

    app.run(host='0.0.0.0', port=args.port)
