# Chicago Justice Project backend app

## Local installation instructions

### Postgres installation

#### macOS

The easiest way to install PostgreSQL for Mac is with a prebuilt Postgres
installation, like [Postgres.app](http://postgresapp.com/).

Alternatively, you may use [Homebrew](https://brew.sh/):

```bash
brew install postgres
brew services start postgresql
```

#### GNU/Linux

The version of PostgreSQL provided in most distros' repositories should be
adequate and can be installed through your distro's package manager.

Ubuntu 16.04:

```bash
sudo apt-get update
sudo apt-get install postgresql
```

Arch Linux:

```bash
sudo pacman -S postgresql
sudo -u postgres initdb --locale $LANG -E UTF8 -D '/var/lib/postgres/data'
sudo systemctl start postgresql.service
```

### Postgres setup

Once PostgreSQL is installed and running, you can create the database you'll
use locally for this app.

As a user with Postgres database privileges:

```bash
createdb cjpdb
```

The name of the database (e.g., `cjpdb`) may be anything you choose, but
keep track of what you name it along with the user and password we're about to
create. You'll need these for setting up your virtual environment.

Create the Postgres user and give it a password:

```bash
createuser --interactive --pwprompt
```

Finally, grant privileges on the database you just created to the user you just
created. For instance, if we created database `cjpdb` and the user `cjpuser`:

```bash
psql -d postgres -c "GRANT ALL ON DATABASE cjpdb TO cjpuser;"
```

### Create a python virtual environment

Next we're going to create a virtual environment to house the environment
variables and the app's dependencies.

If not already installed, install python's `virtualenv` and
`virtualenvwrapper` (as we use python 2, we want to make sure we install the
python 2 versions of all packages):

```bash
pip2 install virtualenv virtualenvwrapper
mkdir ~/.virtualenvs
```

Add the following to your `.bashrc` file:

```bash
export WORKON_HOME=~/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
```

Find out the path to your python installation:

```bash
which python2
```

Create your working environment, naming it whatever you'd like (e.g.,
`cjp_dev`), where `usr/local/bin/python2` is whatever path the previous command
returned:

```bash
mkvirtualenv --python=/usr/local/bin/python2 cjp_dev
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

With your virtual environment activated, we're now ready to install the
necessary dependencies:

```bash
pip2 install -r requirements.txt
```

### Initialize Django models and start server

```bash
./manage.py syncdb
./manage.py runserver
```

## Running news scrapers

```bash
./manage.py runscrapers
```

To run a single scraper, enter the scraper name as an argument, e.g.:

```bash
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
