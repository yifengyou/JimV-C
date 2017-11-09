#!/usr/bin/env bash

su - www -c "cd ~/sites/JimV-C; gunicorn -c gunicorn_config.py main:app"
