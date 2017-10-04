# Chicago Justice Project backend app

## Local installation instructions

### Postgres installation

#### macOS

The easiest way to install PostgreSQL for Mac is with a prebuilt Postgres
installation, like [Postgres.app](http://postgresapp.com/).

Alternatively, you may use [Homebrew](https://brew.sh/):

```shell
brew install postgres
brew services start postgresql
```

#### GNU/Linux

The version of PostgreSQL provided in most distros' repositories should be
adequate and can be installed through your distro's package manager.

Ubuntu 16.04:

```shell
sudo apt-get update
sudo apt-get install postgresql
```

Arch Linux:

```shell
sudo pacman -S postgresql
sudo -u postgres initdb --locale $LANG -E UTF8 -D '/var/lib/postgres/data'
sudo systemctl start postgresql.service
```

### Postgres setup

Once PostgreSQL is installed and running, you can create the database you'll
use locally for this app.

As a user with Postgres database privileges:

```shell
createdb cjpdb
```

The name of the database (e.g., `cjpdb`) may be anything you choose, but
keep track of what you name it along with the user and password we're about to
create. You'll need these for setting up your virtual environment.

Create the Postgres user and give it a password:

```shell
createuser --interactive --pwprompt
```

Finally, grant privileges on the database you just created to the user you just
created. For instance, if we created database `cjpdb` and the user `cjpuser`:

```shell
psql -d postgres -c "GRANT ALL ON DATABASE cjpdb TO cjpuser;"
```

### Setup Environment Variables

Certain settings are read from environment variables. There are two ways you
can set variables: 1) Use a `.env` file in the root directory; 2) setup a
python virtual environment and use `virtualenv`'s `postactivate` and
`predeactivate` hooks. Both methods are detailed below.

#### Create a `.env` environment variable file

An example `.env` file is provided. You should copy it:

```shell
cp .env-example .env
```

Then, you can edit the file in your preferred editor.

#### Create a python virtual environment

Alternatively, you can create a virtual environment to house the environment
variables and the app's dependencies.

If not already installed, install python's `virtualenv` and
`virtualenvwrapper`:

```shell
pip install virtualenv virtualenvwrapper
mkdir ~/.virtualenvs
```

Add the following to your `.bashrc` file:

```shell
export WORKON_HOME=~/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
```

Find out the path to your python installation:

```shell
which python
```

Create your working environment, naming it whatever you'd like (e.g.,
`cjp_dev`), where `usr/local/bin/python` is whatever path the previous command
returned:

```shell
mkvirtualenv --python=/usr/local/bin/python cjp_dev
```

You may now use `workon cjp_dev` and `deactivate` to activate and deactivate
the virtual environment. Setup hooks so that when the virtual environment is
activated, the proper environment variables will be set. Be sure to substitute
`cjp_dev`, `cjpdb`, `cjpuser`, and `cjppassword` with your setup. You can also
generate a unique secret key with something like this [Django Secret Key
Generator](http://www.miniwebtool.com/django-secret-key-generator/)

Add the following to `~/.virtualenvs/cjp_dev/bin/postactivate`:

```bash
export DJANGO_SETTINGS_MODULE="cjp.settings.local"
export DATABASE_NAME="cjpdb"
export DATABASE_USER="cjpuser"
export DATABASE_PASSWORD="cjppassword"
export SECRET_KEY='#&ubnzmo6$-0nk7i&hmii=e$7y-)nv+bm#&ps)6eq@!k+n-nq5'
```

To make sure these variables are unset upon deactivating the virtual
environment, add the following to `~/.virtualenvs/cjp_dev/bin/predeactivate`:

```bash
unset DJANGO_SETTINGS_MODULE
unset DATABASE_NAME
unset DATABASE_USER
unset DATABASE_PASSWORD
unset SECRET_KEY
```

### Install Dependencies

With the environment variables set, we're now ready to install the necessary
dependencies:

```shell
pip install -r requirements.txt
```

### Initialize Django models and start server

```shell
./manage.py migrate
./manage.py loaddata category news_source
./manage.py runserver
```

## Running news scrapers

```shell
./manage.py runscrapers
```

To run a single scraper, enter the scraper name as an argument, e.g.:

```shell
./manage.py runscrapers crains
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
