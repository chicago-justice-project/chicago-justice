Install apt requirements
========================

psql (9.4 repository must be added)
----
```
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install postgresql-client-9.4
```

sudo apt-get update
sudo apt-get -y install build-essential checkinstall libreadline-gplv2-dev libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev libc6-dev libbz2-dev
sudo apt-get install git
sudo apt-get install python-pip python-dev build-essential

Upgrade Python
==============
python -V
mkdir tmp
cd tmp
wget https://www.python.org/ftp/python/2.7.10/Python-2.7.10.tgz
tar xzf Python-2.7.10.tgz 
cd Python-2.7.10/
sudo ./configure 
sudo make install
python -V

More apts
=========
sudo pip install virtualenv
sudo apt-get install libpq-dev python-dev
sudo apt-get install libgeos-dev
sudo apt-get install python-psycopg2
sudo apt-get install binutils libproj-dev gdal-bin

Setup postgress access
======================
/home/cjp/.pgpass (0600)

```
chicagojustice.cbeugrz1koxf.us-east-1.rds.amazonaws.com:5432:postgres:cjp:<password>
```
With <password> replaced

Connect:
`psql -h chicagojustice.cbeugrz1koxf.us-east-1.rds.amazonaws.com postgres`


Setup git deployment key and repository
=======================================
ssh-keygen -t rsa
/home/cjp/.ssh/config:
```
Host chicagojustice github.com
Hostname github.com
IdentityFile ~/.ssh/id_rsa_chicago-justice-deploy
```

With virtualenv created and sourced:

In /home/cjp/sites:
`git clone git@github.com:NUKnightLab/chicago-justice.git`
`pip install -r requirements.txt`


Setup Database and user
=======================
`createuser -h chicagojustice.cbeugrz1koxf.us-east-1.rds.amazonaws.com -P cjpuser`

DB Server is not accessible to world. Using `cjpuser` for username and password.

`psql -h chicagojustice.cbeugrz1koxf.us-east-1.rds.amazonaws.com postgres`

(See AWS RDS Postgis setup instructions for more details on setup below. http://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Appendix.PostgreSQL.CommonDBATasks.html#Appendix.PostgreSQL.CommonDBATasks.PostGIS)

```
postgres=> create extension postgis;
postgres=> create extension fuzzystrmatch;
postgres=> create extension postgis_tiger_geocoder;
postgres=> create extension postgis_topology;
postgres=> alter schema tiger owner to rds_superuser;
postgres=> alter schema topology owner to rds_superuser;
postgres=> CREATE FUNCTION exec(text) returns text language plpgsql volatile AS $f$ BEGIN EXECUTE $1; RETURN $1; END; $f$;
```

Note: the following command is wrong in AWS documentation. s.b. semi-colon, not a comma, after `OWNER TO rds_superuser`

```
postgres=>
SELECT exec('ALTER TABLE ' || quote_ident(s.nspname) || '.' || quote_ident(s.relname) || ' OWNER TO rds_superuser;')
  FROM (
    SELECT nspname, relname
    FROM pg_class c JOIN pg_namespace n ON (c.relnamespace = n.oid) 
    WHERE nspname in ('tiger','topology') AND
    relkind IN ('r','S','v') ORDER BY relkind = 'S')
s;  
```

Test
----
```
postgres=> SET search_path=public,tiger;
postgres=> select na.address, na.streetname, na.streettypeabbrev, na.zip from normalize_address('1 Devonshire Place, Boston, MA 02109') as na;
postgres=> select topology.createtopology('my_new_topo',26986,0.5);
```

Create new databases
-------------------
```
postgres=> create database cjpweb_prd encoding 'UTF8' template template_postgis;
postgres=> grant all on database cjpweb_prd to cjpuser;

postgres=> create database cjpweb_stg encoding 'UTF8' template template_postgis;
postgres=> grant all on database cjpweb_stg to cjpuser;
```

Setup web application
=====================
Create file: `/etc/init/chicagojustice.conf`
