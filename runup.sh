#!/bin/bash

gunicorn -c gunicorn_config.pyc main:app
