#!/bin/bash -ex
# Copyright 2012 NEC Corporation.
# All Rights Reserved.
#

DEST=${DEST:-/opt/stack}
TREMA_DIR=${TREMA_DIR:-$DEST/trema}
TREMA_TMP_DIR=${TREMA_TMP_DIR:-/tmp/trema}
SLICE_DIR="$TREMA_DIR/apps/sliceable_switch"
VAR_DIR="$TREMA_DIR/var"
TREMA_REPO=https://github.com/trema/trema.git
TREMA_APPS_REPO=https://github.com/trema/apps.git
#TREMA_BRANCH=develop
TREMA_BRANCH=0.2.2
#TREMA_APPS_BRANCH=master
TREMA_APPS_BRANCH=1377c14cdf68888bae28d1065baa80cf7913b829

pkgs="gcc make ruby ruby-dev irb file libjson-perl libpcap-dev sqlite3 \
libsqlite3-dev apache2-mpm-prefork libdbi-perl libdbd-sqlite3-perl \
libglib2.0-0 git"
sudo apt-get -y install $pkgs

sudo mkdir -p $TREMA_DIR
if [ ! -w $TREMA_DIR ]; then
    sudo chown `whoami` $TREMA_DIR
fi

# build
sliceable=$TREMA_DIR/apps/sliceable_switch/sliceable_switch
if [ ! -e $sliceable ] || [[ "$RECLONE" == "yes" ]]; then
    git clone https://github.com/trema/trema.git $TREMA_DIR/trema
    git clone https://github.com/trema/apps.git $TREMA_DIR/apps
    pushd $TREMA_DIR/trema
        git checkout $TREMA_BRANCH
    popd
    pushd $TREMA_DIR/apps
        git checkout $TREMA_APPS_BRANCH
        #FIXME
        if [ -f "$SLICEABLE_PATCH" ]; then
            patch -p1 < $SLICEABLE_PATCH
        fi
    popd

    pushd $TREMA_DIR/trema
        ./build.rb
    popd
    make -C $TREMA_DIR/apps/topology
    make -C $TREMA_DIR/apps/flow_manager
    make -C $TREMA_DIR/apps/sliceable_switch
fi

# prepare dir
for dir in apache db log script
do
    mkdir -p $VAR_DIR/$dir
done
sudo mkdir -p $TREMA_TMP_DIR
if [ ! -w $VAR_DIR ]; then
    sudo chown -R `whoami` $VAR_DIR
fi

# config HTTP Server for sliceable_switch
cat > $VAR_DIR/apache/sliceable_switch << 'END'
Listen 8888

<VirtualHost *:8888>

    DocumentRoot @VAR@/script

    <Directory />
        Options FollowSymLinks
        AllowOverride None
        Order deny,allow
        Deny from all
    </Directory>

    <Directory @VAR@/script/>
        Options +ExecCGI
        Script GET /config.cgi
        Script PUT /config.cgi
        Script POST /config.cgi
        Script DELETE /config.cgi
        AllowOverride None
        Order deny,allow
        Deny from all
    </Directory>

    <Location ~ "/(networks|filters)">
        Order allow,deny
        Allow from all
    </Location>

    RewriteEngine on
    RewriteRule ^/tenants/[^/]*/networks(.*)$  /networks$1? [QSA,PT]
    RewriteRule ^/tenants/[^/]*/filters(.*)$  /filters$1? [QSA,PT]
    RewriteRule ^/networks(.*)$ /networks$1? [QSA,L]
    RewriteRule ^/filters(.*)$ /filters$1? [QSA,L]

    AddHandler cgi-script .cgi

    ErrorLog @VAR@/log/sliceable_switch_error.log
    CustomLog @VAR@/log/sliceable_switch_access.log combined

</VirtualHost>
END
sudo sed -i -e "s|@VAR@|$VAR_DIR|" $VAR_DIR/apache/sliceable_switch
sudo ln -sf $VAR_DIR/apache/sliceable_switch /etc/apache2/sites-available
sudo a2enmod rewrite actions
sudo a2ensite sliceable_switch

# deploy files
pushd $SLICE_DIR
    rm -f filter.db  slice.db
    ./create_tables.sh
    mv filter.db  slice.db $VAR_DIR/db/
    cp Slice.pm Filter.pm config.cgi $VAR_DIR/script/
popd
sed -i -e "s|/home/sliceable_switch/db|$VAR_DIR/db|" \
    $VAR_DIR/script/config.cgi
cp $SLICE_DIR/sliceable_switch_null.conf $VAR_DIR/sliceable.conf
sed -i -e "s|../apps/sliceable_switch/slice.db|$VAR_DIR/db/slice.db|" \
       -e "s|../apps/sliceable_switch/filter.db|$VAR_DIR/db/filter.db|" \
       $VAR_DIR/sliceable.conf
sudo chown -R www-data.www-data $VAR_DIR

# reload apache
sudo /etc/init.d/apache2 reload

# start trema
pushd $TREMA_DIR/trema
    sudo ./trema killall
    sudo TREMA_TMP=$TREMA_TMP_DIR ./trema run -d -c $VAR_DIR/sliceable.conf
popd
