'''
Runs the webserver.
'''

# External dependencies
import asyncio
import json
import os

from aiohttp import web

import db as pg_cli


ROUTES = web.RouteTableDef()
AUTH_CODE = os.environ['AUTH_SIMPLE_IDENT']


@ROUTES.get('/')
async def root_handle(req):
    '''
    Tells the malcontent to go root themselves off our lawn.
    '''
    return web.Response(status=200, body='Stuff goes here')


@ROUTES.post('/register')
async def register(req):
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
    except KeyError:
        return web.Response(status=400)

    if username is False or passhash is False:
        return web.Response(status=400)

    success = await pg_cli.insert_new_user(req, username, passhash)

    if success:
        return web.Response(status=201)
    else:
        return web.Response(status=409, body="Username already taken")


@ROUTES.post('/authenticate')
async def authenticate(req):
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
    except KeyError:
        return web.Response(status=400)

    if username is False or passhash is False:
        return web.Response(status=400)

    success = await pg_cli.authenticate_user(req, username, passhash)

    if success:
        return web.Response(status=200)
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
