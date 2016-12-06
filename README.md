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

# Deployment

This is a standard Django project. Current deployment is done via reverse-proxied Nginx with gunicorn running the application. To acheive this, be sure gunicorn is running the application on a port. How you do this will vary according to your system. On Ubuntu, consider using Upstart to manage Gunicorn.

Your Nginx configuration should contain information to proxy requests to the application port. E.g. (if running on port 9000):

```
server {
    listen 80;
    server_name http://data.chicagojustice.org/;
    access_log  /var/log/nginx/chicagojustice.log;
    client_max_body_size 5M;
    root /usr/share/nginx/chicagojustice;

    location / {
        try_files $uri @proxy_to_chicagojustice;
    }

    location @proxy_to_chicagojustice {
      proxy_pass http://127.0.0.1:9000;
      proxy_set_header Host $host;
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

See the Django deployment docs for more details: https://docs.djangoproject.com/en/1.10/howto/deployment/


