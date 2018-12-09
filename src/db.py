'''
This module connects us to our postgreSQL instance
'''
import os
import asyncpg as pg


async def init_db():
    '''
    Initialize our database and create a connection pool.
    '''
    user = os.environ['DB_USERNAME']
    host = os.environ['DB_HOST']
    port = os.environ['DB_PORT']
    database = os.environ['DB_NAME']
    password = os.environ['DB_PASSWORD']

    return await pg.create_pool(
        database=database,
        user=user,
        host=host,
        port=port,
        password=password
    )


def get_pool(req):
    '''
    Return the connection pool from an incoming request object
    '''
    return req.app['pool']


async def insert_data(req, uid, msg, username):
    '''
    Associate a statement with a fictional character
    '''
    pool = get_pool(req)

    async with pool.acquire() as connection:
        async with connection.transaction():
            try:
                await connection.execute('''
                                     INSERT INTO message (uid, msg, nameuser)
                                     VALUES ($1, $2, $3)
                                     RETURNING did
                                         ''', uid, msg, username)
                return True
            except pg.exceptions.UniqueViolationError:
                return False
            except Exception:
                return False


async def get_max_int(req):
    pool = get_pool(req)

    async with pool.acquire() as connection:
        async with connection.transaction():
            stmt = await connection.fetchrow('''
                                               SELECT count(*) as exact_count
                                               FROM message
                                          ''')
            try:
                did = stmt['exact_count']
                return did
            except KeyError:
                return False


async def fetch_data(req, count, back):
    '''
    Retrieves a statement from a fictional character
    '''
    max_did = await get_max_int(req)
    # actual_max = max_did
    # max_did = int(max_did) - int(back) + 1
    # min_did = max_did - int(count) - 1

    pool = get_pool(req)

    async with pool.acquire() as connection:
        async with connection.transaction():
            stmt = await connection.fetch('''
                                        SELECT * FROM message
                                        ORDER BY did DESC LIMIT $1
                                          ''', int(count))
            if stmt is None:
                return False
            else:
                try:
                    results = {
                            "result": [dict(x) for x in stmt],
                            "max_post": max_did
                            }
                    return results
                except Exception:
                    return False
