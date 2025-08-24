set -eu

bash venv.sh

python3 () { ./venv/bin/python3 "$@"; }
pip () { ./venv/bin/pip "$@"; }

sudo apt-get install -y libmariadb-dev
export MYSQLCLIENT_CFLAGS=$(mariadb_config --cflags) # -I/usr/include/mariadb -I/usr/include/mariadb/mysql
export MYSQLCLIENT_LDFLAGS=$(mariadb_config --libs) # -L/usr/lib/x86_64-linux-gnu/ -lmariadb

sudo apt-get install -y libpq-dev

pip install -r requirements.txt

# Confirm the library's binding
ldd ./venv/lib/python*/site-packages/MySQLdb/_mysql*.so | grep -iP 'mysql|mariadb'
