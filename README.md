`install -r requirements.txt`

Assuming user has db privileges:

`sh create_template_postgis­1.4.sh`

Or, if e.g. postgres user has db privileges:

`sudo ­u postgres sh create_template_postgis­1.4.sh`

`createdb -T template_postgis cjpwebdb`
`createuser -P cjpuser`
Password: cjppassword

# see: http://postgis.net/docs/PostGIS_FAQ.html
# legacy_gist not needed for updated Django (1.8)
`psql cjpwebdb < legacy_gist.sql`


in psql:

`# grant all privileges on database cjpwebdb to cjpuser;`

# data dump: https://www.dropbox.com/s/d0mx6x9jxnsqhxn/2016_01_06_full.psql.xz?oref=e

`export CJP_DJANGO_DEVELOPMENT=TestConfig_1`

`./manage.py syncdb`
`./manage.py runserver`


* cpdScraper script

To run the cpdScraper script, you will need GEOS installed. See the instructions in the Django documentation here:

https://docs.djangoproject.com/en/1.8/ref/contrib/gis/install/geolibs/


----
Transfering EC2 and RDS instances:

https://aws.amazon.com/premiumsupport/knowledge-center/account-transfer-ec2-instance/

https://aws.amazon.com/premiumsupport/knowledge-center/account-transfer-rds/


