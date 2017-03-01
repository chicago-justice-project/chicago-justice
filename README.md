# Chicago Justice Project backend app

## Installation instructions

Recommended: Create a python virtualenv

`pip install -r requirements.txt`

You must have GEOS and its python bindings installed. See:
<https://docs.djangoproject.com/en/1.8/ref/contrib/gis/install/geolibs/>

### Postgres setup

Postgres' PostGIS extensions are required. The easiest way to install the
extension is with a prebuilt postgress installation, like Postgres.app for Mac.

Assuming user has db privileges:

`sh create_template_postgis­1.4.sh`

Or, if e.g. postgres user has db privileges:

`sudo ­u postgres sh create_template_postgis­1.4.sh`

Then create Postgres user and data:


`createdb -T template_postgis cjpwebdb`
`createuser -P cjpuser`

Password: cjppassword

see: <http://postgis.net/docs/PostGIS_FAQ.html>

in psql:

`# grant all privileges on database cjpwebdb to cjpuser;`

### Initialize Django models and start server

```bash
export DJANGO_SETTINGS_MODULE=cjp.settings.local    # Change config from production (default) to local
./manage.py syncdb
./manage.py runserver
```

## Running news scrapers

```
./manage.py runscrapers
```

To run a single scraper, enter the scraper name as an argument, e.g.:

```
./manage.py runscrapers crainsScraper
```

For local operation, you must specify local config via `DJANGO_SETTINGS_MODULE` env var, e.g.

```
DJANGO_SETTINGS_MODULE=cjp.settings.local ./manage.py runscrapers
```

----

## Transfering EC2 and RDS instances:

* <https://aws.amazon.com/premiumsupport/knowledge-center/account-transfer-ec2-instance/>
* <https://aws.amazon.com/premiumsupport/knowledge-center/account-transfer-rds/>

# Deployment

This is a standard Django project. The following information is specific to an Ubuntu based deployment using Nginx with Gunicorn. This information will not necessarily apply to all deployment setups. For details on deploying Django applications, see the Django deployment documentation: https://docs.djangoproject.com/en/1.10/howto/deployment/

Current deployment is done via reverse-proxied Nginx with gunicorn running the application. To achieve this, be sure gunicorn is running the application on a port. How you do this will vary according to your system. On Ubuntu, consider using Upstart to manage Gunicorn.

An example upstart config is available in `conf/etc/init/chicagojustice.conf`.

The application can then be managed via: `sudo service chicagojustice [start|stop|restart]`

Your Nginx configuration should contain information to proxy requests to the application port. Example nginx config is
available in `conf/etc/nginx/default`.

## Code updates to the existing deployment

The code is deployed via git repository. Deployment of code changes should
simply require `git pull` inside the application repository, and likely 
`sudo service chicagojustice restart` (please check the name of the service with what
is in the upstart configs under `/etc/init`)

In some cases (ie. model changes) a schema migration is required. Migrate via
`./manage.py migrate`. Be sure to source the virtual environment before running
migrations. See the Django docs for details on schema migrations:
<https://docs.djangoproject.com/en/1.10/topics/migrations/>

To copy static files into place for production, you must run
`python manage.py collectstatic`.

## Accessing the data via SFTP

The script `dumpArticleTables.sh` currently runs every 24 hours. This script exports the article and category tables in CSV format, then packs them into a tar archive in `/home/sftp_users/files`.

Users in the `sftp_users` group can access `/home/sftp_users` via SFTP only. These users do not have shell access and cannot access any other directories.

To create a user in this group, use the command `adduser --home /home/sftp_users/files --ingroup sftp_users`.

The current SSHD config for this group is as follows:
```
Match Group sftp_users
        ForceCommand internal-sftp
        PasswordAuthentication yes
        ChrootDirectory /home/sftp_users
        PermitTunnel no
        AllowAgentForwarding no
        AllowTcpForwarding no
        X11Forwarding no
```
