#!/bin/bash

# The purpose of this script is to dump the news article data to a downloadable
# archive for analysis purposes.
#
# In order to authenticate to the database server, a .pgpass file must be
# present in the home directory of the user running the script. Refer to the
# Postgres documentation for details.

DATABASE_URL=chicagojustice.cbeugrz1koxf.us-east-1.rds.amazonaws.com
OUTPUT_DIRECTORY=/home/sftp_users/files

PG_TABLES=( "newsarticles_article" "newsarticles_usercoding" "newsarticles_category" "newsarticles_usercoding_categories" )

cd $OUTPUT_DIRECTORY
if [[ $? -ne 0 ]]; then
    exit 1
fi
mkdir cjp_tables

for table in "${PG_TABLES[@]}"
do
    psql cjpweb_prd -h $DATABASE_URL -U cjpuser -c "\\copy $table to 'cjp_tables/$table.csv' with csv"
    psql cjpweb_prd -h $DATABASE_URL -U cjpuser -c "\\d $table" >> column_names.txt
done

tar -czf cjp_tables.tgz cjp_tables/
rm -r cjp_tables
