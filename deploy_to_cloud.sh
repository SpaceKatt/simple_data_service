#!/usr/bin/env bash
source .env

cd infrastructure/scripts

./run_packer.sh && ./terra_apply.sh
