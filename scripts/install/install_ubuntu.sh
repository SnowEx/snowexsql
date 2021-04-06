#! /bin/sh

# Add the postgres 13 to the repos
DATABASES="snowex test"

# Users to add to the db
USERS="snow ubuntu"

# User to be readonly
READ_ONLY="snow"

sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
sudo apt-get update
sudo apt install pandoc

# See  https://www.postgresql.org/download/linux/ubuntu/
sudo apt-get install -y postgresql postgis libxml2-dev libgeos-dev libproj-dev libjson-c-dev gdal-bin libgdal-dev \
                        postgresql-13-postgis-3-scripts python3-pip

# Start the database
sudo -u postgres pg_ctlcluster 13 main start

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
  # Create the USER
  sudo -u postgres createuser -s $USER
done

# Install the python package
cd ../../ && python3 setup.py install --user && cd -

# Use the package to modify the postgres conf file with our settings
python3 modify_conf.py

# Restart the postgres service to update the changes in the conf file
sudo service postgresql restart

# Loop over the databases and create them and install extensions
for DB in $DATABASES
do
  echo $DB
  # Create it
  createdb $DB

  # Install postgis
  psql $DB -c 'CREATE EXTENSION postgis; CREATE EXTENSION postgis_raster;'

done

# Establish snow as a readonly user
psql snowex -c "CREATE USER $READ_ONLY WITH PASSWORD 'hackweek';"
psql snowex -c "GRANT CONNECT ON DATABASE snowex TO $READ_ONLY;"
psql snowex -c "GRANT USAGE ON SCHEMA public TO $READ_ONLY;"
psql snowex -c "GRANT SELECT ON ALL TABLES IN SCHEMA public TO $READ_ONLY;"