#! /bin/sh

# Add the postgres 12 to the repos
DATABASES="snowex test"

brew install pandoc
brew install postgres
brew install postgis

# Perform some clean up just in case
for DB in $DATABASES
do
  # Drop the db if it exists
  dropdb --if-exists $DB
done

# Modify the conf file with our settings
python modify_conf.py

# Restart the postgres service to update the changes in the conf file
brew services restart postgresql

# We need a little delay
sleep 1

# Loop over the databases and create them and install extensions
for DB in $DATABASES
do
  # Create it
  createdb $DB

  # Install postgis
  psql $DB -c 'CREATE EXTENSION postgis; CREATE EXTENSION postgis_raster;'

done
