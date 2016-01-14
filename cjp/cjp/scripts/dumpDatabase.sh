#!/bin/sh

echo "You need sudo privileges to run this file"

d=`date +"%F-%H-%M"`
outfile=cjp-dbdump-$d.gz

sudo -u postgres pg_dump -a -o -t '(crimedata_|newsarticles_)*' cjpwebdb | gzip > $outfile
