#!/bin/bash
echo "Setting up database"
../cjp/manage.py migrate
../cjp/manage.py loaddata category news_source
