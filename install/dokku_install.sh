#!/bin/bash
while getopts u:p
do
    case "${flag}" in
        u) username=${OPTARG};;
        p) password=${OPTARG};;
    esac
done

#BASE INSTALL DOKKU
# for debian systems, installs Dokku via apt-get
wget -NP . https://dokku.com/install/v0.34.4/bootstrap.sh
sudo DOKKU_TAG=v0.34.4 bash bootstrap.sh

#add ssh key to dokku
cat ~/.ssh/authorized_keys | dokku ssh-keys:add admin

#add domain name to dokku
dokku domains:set-global uebaba.xyloz.ru

#INSTALL AND INIT USED PLUGINS TO DOKKU:
#1. postgres
sudo dokku plugin:install https://github.com/dokku/dokku-postgres.git postgres
dokku postgres:create uebaba_bot_db
#2. http-auth
dokku plugin:install https://github.com/dokku/dokku-http-auth.git
#3. lets-encrypt
dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git

