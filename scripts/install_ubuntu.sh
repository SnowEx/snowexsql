#! /bin/sh

# Add the postgres 12 to the repos
DATABASES="snowex test"

# sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
# wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
# sudo apt-get update
#
# # See  https://www.postgresql.org/download/linux/ubuntu/
# sudo apt-get install -y postgresql postgis

# Perform some clean up just in case
for DB in $DATABASES
do
  # Drop the db if it exists
  sudo -u postgres dropdb --if-exists $DB
done

# Delete the user
sudo -u postgres dropuser --if-exists $USER

# Create the USER
sudo -u postgres createuser -s $USER

# Modify the conf file with our settings
python modify_conf.py

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
