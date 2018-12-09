'''
Runs the webserver.
'''

# External dependencies
import asyncio
import json
import os
from sys import stderr

import aiohttp
from aiohttp import web

import db as pg_cli


ROUTES = web.RouteTableDef()


AUTH_CODE = os.environ['AUTH_SIMPLE_IDENT']
IDENTITY_ENDPOINT = os.environ['IDENTITY_ENDPOINT']


@ROUTES.get('/')
async def root_handle(req):
    '''
    Tells the malcontent to go root themselves off our lawn.
    '''
    return web.Response(status=200, body='Stuff goes here')


async def auth_user(username, passhash):
    endpoint = 'http://{}/authenticate'.format(IDENTITY_ENDPOINT)

    async with aiohttp.ClientSession() as session:
        async with session.post(endpoint, json={
                                                "username": username,
                                                "passhash": passhash,
                                                "auth_code": AUTH_CODE
                                                }) as resp:
            if resp.status == 401:
                return -1

            try:
                resp_data = await resp.json()
            except json.decoder.JSONDecodeError:
                print('Error communicating with identity service', file=stderr)
                return -2
            try:
                uid = resp_data['uid']
                return uid
            except KeyError:
                print('Error parsing identity response', file=stderr)
                return -2


@ROUTES.post('/data')
async def post_data(req):
    '''
    Registers a new user
    '''
    try:
        data = await req.json()
    except json.decoder.JSONDecodeError:
        return web.Response(status=400)

    try:
        username = data['username']
        passhash = data['passhash']
        msg = data['msg']
    except KeyError:
        return web.Response(status=400)

    if username is False or passhash is False:
        return web.Response(status=400)

    uid = await auth_user(username, passhash)

    if uid == -1:
        return web.Response(status=401)
    if uid == -2:
        return web.Response(status=500)

    success = await pg_cli.insert_data(req, uid, msg, username)

    if success:
        return web.Response(status=201)
    else:
        print('We gots an error', file=stderr)
        return web.Response(status=500)


@ROUTES.post('/fetch')
async def post_fetch(req):
    '''
    Registers a new user
    '''
    try:
        data = await req.json()
    except json.decoder.JSONDecodeError:
        return web.Response(status=400)

    try:
        username = data['username']
        passhash = data['passhash']
        count = data['count']
    except KeyError:
        return web.Response(status=400)

    try:
        back = data['back']
    except KeyError:
        back = 0

    uid = await auth_user(username, passhash)

    if uid == -1:
        return web.Response(status=401)
    if uid == -2:
        return web.Response(status=500)

    if username is False or passhash is False:
        return web.Response(status=400)

    success = await pg_cli.fetch_data(req, count, back)

    for item in success['result']:
        item['created_on'] = item['created_on'].isoformat()

    if success:
        return web.json_response(success)
    else:
        return web.Response(status=401)


@web.middleware
async def auth_middleware(req, handler):
    try:
        data = await req.json()
    except json.decoder.JSONDecodeError:
        return web.Response(status=400)

    try:
        auth_token = data['auth_code']
    except KeyError:
        return web.Response(status=400)

    if auth_token != AUTH_CODE:
        return web.Response(status=401, body='Wrong auth token!')

    response = await handler(req)
    return response


async def init_app():
    '''
    Initialize the database, then application server
    '''
    app = web.Application(middlewares=[auth_middleware])

    app['pool'] = await pg_cli.init_db()

    app.add_routes(ROUTES)

    return app


LOOP = asyncio.get_event_loop()
APP = LOOP.run_until_complete(init_app())


if __name__ == '__main__':
    web.run_app(APP, host='0.0.0.0:8080')
