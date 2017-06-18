#!/usr/bin/env bash

# Create the template spatial database
createdb -E UTF8 template_postgis

# Add PLPGSQL language support
createlang -d template_postgis plpgsql

<<<<<<< HEAD
# Create postgis extenions
psql -d template_postgis -c "CREATE EXTENSION postgis;"

# Enable users to alter spatial tables
psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;" 
=======
# Enable PostGIS extension
psql -d template_postgis -c "CREATE EXTENSION postgis;"

# Enable users to alter spatial tables
psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"
>>>>>>> a4c849fbb6eaa6c632e37200d7bdbd23c41de0b5
psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"

# Make the database a template
psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';"
