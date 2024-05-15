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

#INSTALLING PROMETHEUS/GRAFANA/LOKI STACK
#Create bridged network
dokku network:create prometheus-bridge
#Create pronetheus app
dokku apps:create prometheus
dokku proxy:ports-add prometheus http:80:9090
#Create a volumes for data
mkdir -p /var/lib/dokku/data/storage/prometheus/{config,data}
touch /var/lib/dokku/data/storage/prometheus/config/{alert.rules,prometheus.yml}
chown -R nobody:nogroup /var/lib/dokku/data/storage/prometheus

dokku storage:mount prometheus /var/lib/dokku/data/storage/prometheus/config:/etc/prometheus
dokku storage:mount prometheus /var/lib/dokku/data/storage/prometheus/data:/prometheus
#Set prometheus config and attach to bridged network
dokku config:set --no-restart prometheus DOKKU_DOCKERFILE_START_CMD="--config.file=/etc/prometheus/prometheus.yml
  --storage.tsdb.path=/prometheus
  --web.console.libraries=/usr/share/prometheus/console_libraries
  --web.console.templates=/usr/share/prometheus/consoles
  --web.enable-lifecycle
  --storage.tsdb.no-lockfile"
dokku network:set prometheus attach-post-deploy prometheus-bridge
#Move prometheus config file
cat config/prometheus.yml | sed 's/<username>/'"$username"' s/<password>/'"$password"'' > config/prometheus.yml
mv config/prometheus.yml /var/lib/dokku/data/storage/prometheus/config/prometheus.yml
#Deploy prometheus image
docker pull prom/prometheus:latest
docker tag prom/prometheus:latest dokku/prometheus:latest
dokku tags:deploy prometheus latest
dokku letsencrypt prometheus
dokku http-auth:on prometheus $username $password
#Setup node-exporter
dokku apps:create node-exporter
dokku proxy:ports-set node-exporter http:80:9100
dokku config:set --no-restart node-exporter DOKKU_DOCKERFILE_START_CMD="--collector.textfile.directory=/data --path.procfs=/host/proc --path.sysfs=/host/sys"
#Create volumes for data
mkdir -p /var/lib/dokku/data/storage/node-exporter
chown nobody:nogroup /var/lib/dokku/data/storage/node-exporter
dokku storage:mount node-exporter /proc:/host/proc:ro
dokku storage:mount node-exporter /:/rootfs:ro
dokku storage:mount node-exporter /sys:/host/sys:ro
dokku storage:mount node-exporter /var/lib/dokku/data/storage/node-exporter:/data
#Add node-exporter to host network
dokku docker-options:add node-exporter deploy "--net=host"
#Disable zero-downtime checks
dokku checks:disable node-exporter
#Deploy node-exporter
docker image pull prom/node-exporter:latest
docker image tag prom/node-exporter:latest dokku/node-exporter:latest
dokku tags:deploy node-exporter latest
dokku letsencrypt node-exporter
dokku http-auth:on node-exporter $username $password
#Setup cAdvisor
dokku apps:create cadvisor
dokku proxy:ports-set cadvisor http:80:8080
dokku config:set --no-restart cadvisor DOKKU_DOCKERFILE_START_CMD="--docker_only --housekeeping_interval=10s --max_housekeeping_interval=60s"
#Set the storage mounts
dokku storage:mount cadvisor /:/rootfs:ro
dokku storage:mount cadvisor /sys:/sys:ro
dokku storage:mount cadvisor /var/lib/docker:/var/lib/docker:ro
dokku storage:mount cadvisor /var/run:/var/run:rw
#Attach to bridge network
dokku network:set cadvisor attach-post-deploy prometheus-bridge
#Deploy cAdvisor
docker image pull gcr.io/google-containers/cadvisor:latest
docker image tag gcr.io/google-containers/cadvisor:latest dokku/cadvisor:latest
dokku tags:deploy cadvisor latest
dokku letsencrypt cadvisor
dokku http-auth:on cadvisor $username $password
#Setup Loki
dokku apps:create loki
dokku proxy:ports-add loki http:80:3100
dokku config:set --no-restart loki DOKKU_DOCKERFILE_START_CMD="-config.file=/etc/loki/loki-config.yaml"
#Set the storage mounts
mkdir -p /var/lib/dokku/data/storage/loki/config
touch /var/lib/dokku/data/storage/loki/config/loki-config.yml
chown -R nobody:nogroup /var/lib/dokku/data/storage/loki
dokku storage:mount loki /var/lib/dokku/data/storage/loki/config:/etc/loki
#Attach to bridge network
dokku network:set loki attach-post-deploy prometheus-bridge
#Move Loki config file
mv config/loki-config.yaml /var/lib/dokku/data/storage/loki/config/loki-config.yaml
#Deploy Loki
docker image pull grafana/loki:2.0.0
docker image tag grafana/loki:2.0.0 dokku/loki:latest
dokku tags:deploy loki latest
dokku letsencrypt loki
dokku http-auth:on loki $username $password
#Setup Promtail
dokku apps:create promtail
dokku config:set --no-restart promtail DOKKU_DOCKERFILE_START_CMD="-config.file=/etc/promtail/promtail-config.yaml"
#Set the storage mounts
mkdir -p /var/lib/dokku/data/storage/promtail/config
touch /var/lib/dokku/data/storage/promtail/config/promtail-config.yml
chown -R nobody:nogroup /var/lib/dokku/data/storage/promtail
dokku storage:mount promtail /var/lib/dokku/data/storage/promtail/config:/etc/promtail
dokku storage:mount promtail /var/log:/var/log
#Attach to bridge network
dokku network:set promtail attach-post-deploy prometheus-bridge
#Move Loki config file
mv config/promtail-config.yaml /var/lib/dokku/data/storage/promtail/config/promtail-config.yaml
#Deploy Promtail
docker image pull grafana/promtail:2.0.0
docker image tag grafana/promtail:2.0.0 dokku/promtail:latest
dokku tags:deploy promtail latest
dokku domains:disable promtail
#Setup grafana
dokku apps:create grafana
dokku proxy:ports-add grafana http:80:3000
#Set the storage and config mounts
mkdir -p /var/lib/dokku/data/storage/grafana/{config,data,plugins}
mkdir -p /var/lib/dokku/data/storage/grafana/config/provisioning/datasources
chown -R 472:472 /var/lib/dokku/data/storage/grafana
dokku storage:mount grafana /var/lib/dokku/data/storage/grafana/config/provisioning/datasources:/etc/grafana/provisioning/datasources
dokku storage:mount grafana /var/lib/dokku/data/storage/grafana/data:/var/lib/grafana
dokku storage:mount grafana /var/lib/dokku/data/storage/grafana/plugins:/var/lib/grafana/plugins
#Set datasources
mv config/datasources/prometheus.yml /var/lib/dokku/data/storage/grafana/config/provisioning/datasources/prometheus.yml
mv config/datasources/loki.yml /var/lib/dokku/data/storage/grafana/config/provisioning/datasources/loki.yml
#Attach to bridge network
dokku network:set grafana attach-post-deploy prometheus-bridge
#Deploy grafana
docker pull grafana/grafana:latest
docker tag grafana/grafana:latest dokku/grafana:latest
dokku tags:deploy grafana latest
dokku letsencrypt grafana