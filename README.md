# Chicago Justice Project backend app

## Local installation instructions

### Postgres installation

#### macOS

The easiest way to install PostgreSQL for Mac is with a prebuilt Postgres
installation, like [Postgres.app](http://postgresapp.com/).

Alternatively, you may use [Homebrew](https://brew.sh/):

```shell
brew install postgresql
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

There are two methods to creating a virtual environment:

##### PyEnv

Install PyEnv as according to the repository's [installation instructions](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation)

Addtionally, install pyenv-virtualenv for managing virtual environments within different Python versions. Installation instructions found [here](https://github.com/pyenv/pyenv?tab=readme-ov-file#installation)

Next, let's install Python 3.8 (or an alternative version if you'd like).

```shell
pyenv install 3.8
pyenv global 3.8
```

Now, we're able to set up our virtual environment:

```shell
pyenv virtualenv 3.8 name-of-my-virtual-env
pyenv activate name-of-my-virtual-env
```

##### VirtualEnv

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

### Using the Article-Tagging Package Locally

For development purposes, changes to the [article-tagging](https://github.com/chicago-justice-project/article-tagging) package may be required. This requires packaging the project locally to be used in this project.

This can be done via:
`pip install -e PATH_TO_ARTICLE_TAGGING_REPO`

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

## Deployment

### CLI setup

The app runs on AWS Elastic Beanstalk. In order to manage the production app, a project maintainer must grant
you an AWS login and access key.

The Elastic Beanstalk CLI is separate from the main AWS CLI. Install it as described
[in the docs](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html).

The most reliable way to configure your credentials is to set the key ID and secret as environment
variables. If you use a different AWS account normally, you can create a file that sets the
envvars to the CJP account, and only source the file when working on the project.

Create a file `cjp-aws.env` with the following lines, or add them to your shell configuration.
**Make sure that these values don't get checked into version control!**

```
export AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXX
export AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

If you create a standalone file, you can enable the CJP credentials in your current
terminal session with `source cjp-aws.env`.

Test that you have the CLI configured correctly by running the following from the
`chicago-justice` project directory:

```
eb status
```

### Deploying

To deploy to production, run `eb deploy` from the project directory. It will deploy
whatever is on your local filesystem, even if it isn't checked into git. To maintain
consistency between production and git, it's recommended to merge changes to master
and then `git checkout master && git pull` before deploying.

Elastic Beanstalk will run any database migrations as part of the deployment. You can check on the
status of the deployment with `eb status`, or `eb logs` for the most recent logs from
various important logfiles.

Environment variables can also be configured with the CLI or from the AWS web interface.
