#!/usr/bin/env python3

"""Test the update proxy server."""

from urllib.request import Request, urlopen
import json
import os
import subprocess
import sys
import time


def start_server():
    """Start up the proxy server."""
    args = [
        sys.executable,
        os.path.realpath(os.path.join(os.path.dirname(__file__), 'update-proxy.py')),  # noqa
        '--port',
        '8080',
    ]

    if 'UPSTREAM' in os.environ:
        args.extend(['--upstream', os.environ['UPSTREAM']])

    return subprocess.Popen(args, stdout=sys.stdout, stderr=sys.stderr)


def request_list():
    """
    Request the release list from the server.

    Returns the list.
    """
    url = 'http://localhost:8080/releases'
    r = Request(url, headers={'Accept': 'application/json'})
    f = urlopen(r)
    return json.load(f)


def test():
    """Test the server output."""
    releases = request_list()

    assert len(releases) > 0

    release = releases[0]

    assert 'prerelease' in release and type(release['prerelease']) is bool
    assert 'draft' in release and type(release['draft']) is bool
    assert 'tag_name' in release and release['tag_name']
    assert 'assets' in release and len(release['assets']) > 0

    for asset in release['assets']:
        assert 'browser_download_url' in asset


if __name__ == '__main__':
    # Start the server
    p = start_server()

    # Wait a few seconds for things to start up
    time.sleep(5)

    # Test
    test()

    # Kill the server
    p.terminate()
