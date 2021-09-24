
# Install Landa in Docker

First of all we'll be using the "official docker setup" by *Frappe*. It's weird compared to others you might know from different systems as it heavily depends on the Visual Studio Code Plugin [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers). So you will need to install [VS Code](https://code.visualstudio.com/) and use this extension. See [frappe docker documentation](https://github.com/frappe/frappe_docker/blob/develop/development/README.md#use-vscode-remote-containers-extension) on how to do so.

Let's start by downloading the frappe docker boilerplate. The `.devcontainer` folder we create contains the docker environment configuration used by the above mentioned extension. 

```sh
git clone https://github.com/frappe/frappe_docker.git landa-docker
cd landa-docker
cp -R devcontainer-example .devcontainer
```

To be able to install our custom landa app later we need to adjust the docker-compose file and forward our SSH agent. And while we're at it we add the possibility to connect to the MariaDB from the host. Change the *frappe* and *mariadb* services in `/path/to/landa-docker/.devcontainer/docker-compose.yml` according to the following excerpt.

```
[...]

  mariadb:
    image: mariadb:10.3
    environment:
      - MYSQL_ROOT_PASSWORD=123
      - MYSQL_USER=root
    volumes:
      - ../installation/frappe-mariadb.cnf:/etc/mysql/conf.d/frappe.cnf
      - mariadb-vol:/var/lib/mysql
    ports:
      - 3306:3306

[...]

  frappe:
    image: frappe/bench:latest
    command: sleep infinity
    environment:
      - SHELL=/bin/bash
      - SSH_AUTH_SOCK=/ssh-agent
    volumes:
      - ..:/workspace:cached
      - $SSH_AUTH_SOCK:/ssh-agent
    working_dir: /workspace/development
    ports:
      - "8000-8005:8000-8005"
      - "9000-9005:9000-9005"

[...]
```

Next initialize a *bench* environment. *Bench* is a CLI tool that will be used to manage our site and app(s) and will be executed within the *frappe* container defined in the `.devcontainer/docker-compose.yml`. 

```sh
docker exec -ti landa-docker_devcontainer_frappe_1 bash -c '
  bench init --skip-redis-config-generation --frappe-branch version-13 landa-bench;
'
```

Just to be sure you did everything right:

```sh
docker exec -ti landa-docker_devcontainer_frappe_1 bash -c '
  cd landa-bench;
  bench find .
'
```

**Optional:** Apart from `bench find .` the rest is boilerplate. For convinience you might wat to create a little helper function and put it to `~/.zshrc` or `~/.bashrc` depending on what shell you're using. Like this:

```sh
function landaCli {
  LANDA_FRAPPE_CONTAINER=landa-docker_devcontainer_frappe_1
  if [ ! "$(docker ps -a | grep $LANDA_FRAPPE_CONTAINER)" ]; then
    echo "Landa frappe container not running"
    return 1
  fi
  docker exec -ti landa-docker_devcontainer_frappe_1 bash -c "cd landa-bench; $@"
}
```

And use it like this:

```
landaCli "bench find ." 
```

Then you need to adjust some bench confgurations to match the docker environment.

```sh
docker exec -ti landa-docker_devcontainer_frappe_1 bash -c '
  cd landa-bench;
  bench set-mariadb-host mariadb;
  bench set-redis-cache-host redis-cache:6379;
  bench set-redis-queue-host redis-queue:6379;
  bench set-redis-socketio-host redis-socketio:6379
'
```

For some reason the frappe documentation states that a site in development (locally) *needs* to be named with a suffix of `.localhost` so let's do it:

```sh
docker exec -ti landa-docker_devcontainer_frappe_1 bash -c '
  cd landa-bench;
  bench new-site landa.localhost \
    --mariadb-root-password 123 \
    --admin-password admin \
    --no-mariadb-socket \
 '
```
Set site to developer mode. *(This seems to be important - leaving this out will result in failing the ERPNext installation)*

```sh
docker exec -ti landa-docker_devcontainer_frappe_1 bash -c '
  cd landa-bench;
  bench --site landa.localhost set-config developer_mode 1;
  bench --site landa.localhost clear-cache;
'
```

Download and install ERPNext.

```sh
docker exec -ti landa-docker_devcontainer_frappe_1 bash -c '
  cd landa-bench;
  bench get-app --branch version-13 erpnext https://github.com/frappe/erpnext.git;
  bench --site landa.localhost install-app erpnext;
'
```

Now start the environment.

```sh
docker exec -ti landa-docker_devcontainer_frappe_1 bash -c '
  cd landa-bench;
  bench start;
'
```

Use the setup wizard to initialize the site before you install the landa app. Go to http://localhost:8000/ and login as **administrator** with password **admin**. See https://github.com/realexperts/landa#2-complete-the-setup-wizard for some examples of values to use in the wizard.

Finally download and install our custom landa app.

```sh
docker exec -ti landa-docker_devcontainer_frappe_1 bash -c '
  cd landa-bench;
  bench get-app --branch version-13 landa git@github.com:realexperts/landa.git
  bench --site landa.localhost install-app landa
  bench --site landa.localhost migrate
'
```

## Troubleshooting

### On Windows file changes are not being detected

It was previously assumed that changing permissions could fix the problem:

```sh
docker exec -ti landa-docker_devcontainer_frappe_1 bash -c '
  cd landa-bench;
  find /workspace/development/landa-bench -type f -exec chmod 666 {} \;
  find /workspace/development/landa-bench -type d -exec chmod 777 {} \;
'
```

## Persist changes

Export changes made in the UI by calling the following:

```sh
docker exec -ti landa-docker_devcontainer_frappe_1 bash -c '
  cd landa-bench;
  bench --site landa.localhost export-fixtures --app landa
'
```

If not already done you might want to define those parts you want to export first. To do so you need to add the doctypes you want to export to the `hooks.py` file within the custom app (landa).

```
fixtures = [
  …,
  "DoctypeToexport",
	{
		"doctype": "DoctypeToExportFiltered",
		"filters":	{
			"name": ["in", "Instance name", "Another instance name"]
		}
	}
]
```