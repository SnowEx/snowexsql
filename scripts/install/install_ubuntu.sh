#! /bin/sh

# Add the postgres 14 to the repos
DATABASES="snowex test"

# Users to add to the db
USERS="snow builder"

# User to be readonly
READ_ONLY="snow"

# Assign our DB_BUILDER
DB_BUILDER="builder"

# Are you using a virtualenv?
USING_VIRTUALENV=true

sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
sudo apt install pandoc

# See  https://www.postgresql.org/download/linux/ubuntu/
sudo apt-get install -y postgresql postgis libxml2-dev libgeos-dev libproj-dev libjson-c-dev gdal-bin libgdal-dev \
                        postgresql-14-postgis-3-scripts python3-pip unzip

# Start the database
sudo -u postgres pg_ctlcluster 14 main stop

sudo -u postgres pg_ctlcluster 14 main start

# Perform some clean up just in case
for DB in $DATABASES
  do
    # Drop the db if it exists
    sudo -u postgres dropdb --if-exists $DB
  done

for DB_USER in $USERS
  do
    # Drop the db if it exists
    sudo -u postgres dropuser --if-exists $DB_USER
    sudo -u postgres psql -c "DROP ROLE IF EXISTS $DB_USER;"

  done

# Install the python package
if $USING_VIRTUALENV
  then
    cd ../../ && python3 setup.py install && cd -
  else
    cd ../../ && python3 setup.py install --user && cd -

fi

# Use the package to modify the postgres conf file with our settings
python3 modify_conf.py

# Restart the postgres service to update the changes in the conf file
sudo service postgresql restart

# Create roles before db
sudo -u postgres psql -c "CREATE USER $DB_BUILDER WITH PASSWORD 'db_builder';"
sudo -u postgres psql -c "CREATE USER $READ_ONLY WITH PASSWORD 'hackweek';"

# Loop over the databases and create them and install extensions
for DB in $DATABASES
  do
    echo Creating $DB database
    # Create the dbs that the database build owns
    sudo -u postgres createdb -O $DB_BUILDER $DB

    # Install postgis
    sudo -u postgres psql $DB -c 'CREATE EXTENSION postgis; CREATE EXTENSION postgis_raster;'
    python3 ../upload/create.py --overwrite --db $DB --credentials ../upload/credentials.json
  done

# Establish builder as our uploading user
sudo -u postgres psql snowex -c "GRANT CONNECT ON DATABASE snowex TO $DB_BUILDER;"
sudo -u postgres psql snowex -c "GRANT CONNECT ON DATABASE test TO $DB_BUILDER;"
sudo -u postgres psql snowex -c "GRANT USAGE ON SCHEMA public TO $DB_BUILDER;"
sudo -u postgres psql snowex -c "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO $DB_BUILDER;"


# Establish snow as a readonly user based on
# https://medium.com/@swaplord/grant-read-only-access-to-postgresql-a-database-for-a-user-35c57897dd0b
sudo -u postgres psql snowex -c "GRANT CONNECT ON DATABASE snowex TO $READ_ONLY;"
sudo -u postgres psql snowex -c "GRANT USAGE ON SCHEMA public TO $READ_ONLY;"

# Create the tables

#psql snowex -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO $READ_ONLY;"
sudo -u postgres psql snowex -c "GRANT SELECT ON sites TO $READ_ONLY;"
sudo -u postgres psql snowex -c "GRANT SELECT ON points TO $READ_ONLY;"
sudo -u postgres psql snowex -c "GRANT SELECT ON layers TO $READ_ONLY;"
sudo -u postgres psql snowex -c "GRANT SELECT ON images TO $READ_ONLY;"
