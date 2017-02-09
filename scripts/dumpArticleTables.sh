#!/bin/bash

# The purpose of this script is to dump the news article data to a downloadable
# archive for analysis purposes.
#
# In order to authenticate to the database server, a .pgpass file must be
# present in the home directory of the user running the script. Refer to the
# Postgres documentation for details.

DATABASE_URL=chicagojustice.cbeugrz1koxf.us-east-1.rds.amazonaws.com
OUTPUT_DIRECTORY=/home/sftp_users/files

cd $OUTPUT_DIRECTORY
if [[ $? -ne 0 ]]; then
    exit 1
fi
mkdir cjp_tables
psql cjpweb_prd -h $DATABASE_URL -U cjpuser -c "\\copy newsarticles_article to 'cjp_tables/newarticles_article.csv' with csv"
psql cjpweb_prd -h $DATABASE_URL -U cjpuser -c "\\copy newsarticles_category to 'cjp_tables/newsarticles_category.csv' with csv"
psql cjpweb_prd -h $DATABASE_URL -U cjpuser -c "\\copy newsarticles_article_categories to 'cjp_tables/newsarticles_article_categories.csv' with csv"
tar -czf cjp_tables.tgz cjp_tables/
rm -r cjp_tables
