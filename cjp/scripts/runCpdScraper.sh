#!/bin/sh
export DJANGO_SETTINGS_MODULE=cjp.settings
export PYTHONPATH=$PYTHONPATH:/home/cjp/sites/chicago-justice:/home/cjp/sites/chicago-justice/cjp
cd /home/cjp/sites/chicago-justice/cjp/scripts

if [ "$1" = "--rebuild" ]; then
  echo "Running with --rebuild"
  python cpdScraper.py --rebuild
else
  python cpdScraper.py
fi
