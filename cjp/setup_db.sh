#!/bin/bash
# Create DB tables and populate with seed data
echo "Setting up database"
./manage.py migrate
./manage.py loaddata category news_source
