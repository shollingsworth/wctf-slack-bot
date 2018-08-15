#!/usr/bin/env bash
#Mac hack for realpath program
dbname="mydb"
test $(which realpath) || realpath() {
   [[ $1 = /* ]] && echo "$1" || echo "$PWD/${1#./}"
}
env="$1"
test -z "${env}" && {
    echo "Error, environment argument is empty"
    exit -1
}
source ~/.bashrc
odir=$(pwd)
mydir=$(dirname $(realpath $0))
cd ${mydir}
echo "Recreating/Restoring: ${dbname}"
./modify_db.py init --environment ${env} --db ${dbname}
./data_import_export.py import -e ${env} -i ${mydir}/authdata-${env}.json
./genzappa_settings.py
cd ${odir}
zappa update ${env}
