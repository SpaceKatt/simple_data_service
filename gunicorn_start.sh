#!/usr/bin/env bash
source .env

cd src
gunicorn --bind 127.0.0.1:8000 \
         --worker-class aiohttp.GunicornUVLoopWebWorker \
         main:APP
