# setup docker container for frappe

## initiate docker compose
docker-compose up -d
## enter container
docker-compose exec frappe bash
## for Windows: allow the container to write in the directory
cd /
sudo chmod -R 777 /workspace
cd /workspace/development
## install according to https://github.com/frappe/frappe_docker/tree/develop/development
## install frappe with fixed frappe version via bench
## (runs git clone, pip install for python packages, yarn for js etc.)
bench init --skip-redis-config-generation --frappe-branch version-13-beta frappe-bench
cd frappe-bench
## set up bench
bench set-mariadb-host mariadb
bench set-redis-cache-host redis-cache:6379
bench set-redis-queue-host redis-queue:6379
bench set-redis-socketio-host redis-socketio:6379

## for Windows go to main directory (above workspace) in Windows Explorer
## change access rights of frappe-mariadb.cnf for durrent user (check refuse for write permission)

## new frappe site (pass password that is set in docker), creates data bases
bench new-site landa.localhost --mariadb-root-password 123 --admin-password admin --no-mariadb-socket
## Set bench developer mode on the new site
## set developer mode (important for saving doctypes!)
bench --site landa.localhost set-config developer_mode 1
bench --site landa.localhost clear-cache

## install our custom app
bench get-app landa https://github.com/realexperts/landa.git
bench --site landa.localhost install-app landa

## start frappe
bench start

# restart container
## initiate docker compose
docker-compose up -d
## enter container
docker-compose exec frappe bash
## start bench in directory
cd frappe-bench
bench start
## open in browser
http://localhost:8000
first login: username = administrator, password = admin

## stop bench
ctrl+c

## exit container
exit

## stop docker
docker-compose stop

# git
