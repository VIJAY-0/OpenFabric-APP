#!/bin/bash

start_sh_server
start_code_server

set -a && source .env && set +a

python3 ./ignite.py

infinite_loop