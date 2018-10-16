#!/usr/bin/env python3

import sys
import json
import sys
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from pprint import pprint
import hashlib
import mimetypes

from rauth import OAuth1Session, OAuth1Service


OAUTH_ORIGIN = 'https://secure.smugmug.com'
REQUEST_TOKEN_URL = OAUTH_ORIGIN + '/services/oauth/1.0a/getRequestToken'
ACCESS_TOKEN_URL = OAUTH_ORIGIN + '/services/oauth/1.0a/getAccessToken'
AUTHORIZE_URL = OAUTH_ORIGIN + '/services/oauth/1.0a/authorize'

API_ORIGIN = 'https://api.smugmug.com'
UPLOAD_ORIGIN = 'https://upload.smugmug.com'


def get_service(config):
    if type(config) is not dict \
            or 'key' not in config \
            or 'secret' not in config\
            or type(config['key']) is not str \
            or type(config['secret']) is not str:
        print('====================================================')
        print('Invalid config.json!')
        print('The expected format is demonstrated in example.json.')
        print('====================================================')
        sys.exit(1)
    return OAuth1Service(
        name='smugmug-oauth-web-demo',
        consumer_key=config['key'],
        consumer_secret=config['secret'],
        request_token_url=REQUEST_TOKEN_URL,
        access_token_url=ACCESS_TOKEN_URL,
        authorize_url=AUTHORIZE_URL,
        base_url=API_ORIGIN + '/api/v2')


def add_auth_params(auth_url, access=None, permissions=None):
    if access is None and permissions is None:
        return auth_url
    parts = urlsplit(auth_url)
    query = parse_qsl(parts.query, True)
    if access is not None:
        query.append(('Access', access))
    if permissions is not None:
        query.append(('Permissions', permissions))
    return urlunsplit((
        parts.scheme,
        parts.netloc,
        parts.path,
        urlencode(query, True),
        parts.fragment))


def get_access_token(service):
    # First, we need a request token and secret, which SmugMug will give us.
    # We are specifying "oob" (out-of-band) as the callback because we don't
    # have a website for SmugMug to call back to.
    rt, rts = service.get_request_token(params={'oauth_callback': 'oob'})

    # Second, we need to give the user the web URL where they can authorize our
    # application.
    auth_url = add_auth_params(
            service.get_authorize_url(rt), access='Full', permissions='Modify')
    print('Go to %s in a web browser.' % auth_url)

    # Once the user has authorized our application, they will be given a
    # six-digit verifier code. Our third step is to ask the user to enter that
    # code:
    sys.stdout.write('Enter the six-digit code: ')
    sys.stdout.flush()
    verifier = sys.stdin.readline().strip()

    # Finally, we can use the verifier code, along with the request token and
    # secret, to sign a request for an access token.
    at, ats = service.get_access_token(rt, rts, params={'oauth_verifier': verifier})

    return at, ats


def get_session():
    try:
        with open('config.json', 'r') as fh:
            config = json.load(fh)
    except IOError as e:
        print('====================================================')
        print('Failed to open config.json! Did you create it?')
        print('The expected format is demonstrated in example.json.')
        print('====================================================')
        sys.exit(1)
        
    service = get_service(config)
    
    # Check if access token is already available in config
    if 'access token' not in config or 'access token secret' not in config:
        at, ats = get_access_token(service)
        # The access token we have received is valid forever, unless the user
        # revokes it.
        # Save access token to config file
        config['access token'], config['access token secret'] = at, ats
        try:
            with open('config.json', 'w') as fh:
                json.dump(config, fh)
        except IOError as e:
            print('====================================================')
            print('Failed to write to config.json! Is it writable?')
            print('Access token:', at)
            print('Access token secret:', ats)
            print('====================================================')
            sys.exit(1)
    else:
        at, ats = config['access token'], config['access token secret']
    
    return service.get_session((at, ats))


def get_album_uri(search_text, session):
    r = json.loads(session.get(
        API_ORIGIN + '/api/v2/album!search',
        params={"Text": search_text},
        headers={'Accept': 'application/json'}).text)
    return r['Response']['Album'][0]['Uri']


def main():
    session = get_session()
    
    album_uri = get_album_uri("Neues aus dem Lab", session)
    
    with open(sys.argv[1], 'rb') as f:
        data = f.read()
    mime = mimetypes.guess_type(sys.argv[1])[0]

    pprint(session.post(
        url=UPLOAD_ORIGIN,
        data=data,
        header_auth=True,
        headers={'Content-Length': str(len(data)),
                 'Content-MD5': hashlib.md5(data).hexdigest(),
                 'Content-Type': mime,
                 'X-Smug-AlbumUri': album_uri,
                 'X-Smug-ResponseType': 'JSON',
                 'X-Smug-Version': 'v2',
                 'X-Smug-FileName': sys.argv[1]}).text)


if __name__ == '__main__':
    main()
