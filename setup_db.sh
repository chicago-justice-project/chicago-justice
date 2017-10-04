#!/bin/bash
echo "Ruuning script"
cjp/manage.py migrate
cjp/manage.py loaddata category news_source
cjp/manage.py runserver
