#!/bin/bash

# The purpose of this script is to dump the news article data to a downloadable
# archive for analysis purposes.
#
# Assumes DB and AWS credentials are set as envvars from Elastic Beanstalk config

export PGPASSWORD=$DATABASE_PASSWORD
OUTPUT_DIRECTORY=/tmp

PG_TABLES=(
    "newsarticles_newssource"
    "newsarticles_article"
    "newsarticles_usercoding"
    "newsarticles_category"
    "newsarticles_usercoding_categories"
    "newsarticles_trainedcoding"
    "newsarticles_trainedlocation"
    "newsarticles_trainedcategoryrelevance"
)

cd $OUTPUT_DIRECTORY
if [[ $? -ne 0 ]]; then
    exit 1
fi
mkdir -p cjp_tables

for table in "${PG_TABLES[@]}"
do
    psql $DATABASE_NAME -h $DATABASE_HOST -U $DATABASE_USER -c "\\copy $table to STDOUT with csv" | gzip > cjp_tables/${table}.csv.gz
    psql $DATABASE_NAME -h $DATABASE_HOST -U $DATABASE_USER -c "\\d $table" >> cjp_tables/column_names.txt
done

tar -czf cjp_tables.tar.gz cjp_tables/
rm -r cjp_tables

aws s3 cp --acl public-read cjp_tables.tar.gz s3://cjp-news-data/cjp-tables-${EXPORT_TOKEN}.tar.gz
