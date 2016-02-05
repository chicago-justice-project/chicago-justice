#!/bin/sh

# script for promoting code to production
# Used by John in early versions of site

echo
echo Have you made a recent DB backup?
echo

rm -rf /tmp/cjp*
svn export file:///home/john/svnrepo/cjp/trunk /tmp/cjp
cp cjp-dbdump-* /tmp/cjp/cjp/scripts
rm /tmp/cjp/cjp/scripts/exportCode.sh
sed 's/DEBUG = True/DEBUG = False/' /tmp/cjp/cjp/settings.py > /tmp/settings.py
cp /tmp/settings.py /tmp/cjp/cjp/settings.py

cd /tmp
tar cvfz cjp.tgz ./cjp
rm settings.py
