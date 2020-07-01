################################################################################
# Ubuntu 18.04 PostGIS install Script. Instructions bashified from
# http://postgis.net/docs/postgis_installation.html#install_short_POSTGIS_VERSION
#
# Written by: Micah Johnson
# Date: 07-01-2020
################################################################################

# See https://postgis.net/source/ for available versions
POSTGIS_VERSION=3.0.1
INSTALL_DIR=~/packages

# Install Posgres development files and other pre-reqs
sudo apt install postgresql-server-dev-10 libxml2-dev libgeos-dev libproj-dev libjson-c-dev gdal-bin libgdal-dev

# Download our postgis
wget https://download.osgeo.org/postgis/source/postgis-$POSTGIS_VERSION.tar.gz -O $INSTALL_DIR/postgis.tar.gz
tar xvfz $INSTALL_DIR/postgis.tar.gz -C $INSTALL_DIR
cd $INSTALL_DIR/postgis-$POSTGIS_VERSION && \
  ./configure --with-raster&& \
make && \
sudo make install

# Link libraries
sudo ldconfig

# Clean up
rm -f $INSTALL_DIR/postgis.tar.gz

# Prompt user to add path
echo " "
echo "Install Complete!"
echo "Add the following to your ~/.bashrc to have access to tools like raster2psql:"
echo "export PATH=/usr/lib/postgresql/10/bin/:\$PATH"
