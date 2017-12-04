#!/usr/bin/env bash

on_exit(){
    if [ ${?} -ne 0 ] ; then
        echo "[ERROR] Error occurred at ${BASH_SOURCE}:${LINENO} command: ${BASH_COMMAND}"
    else
        echo "[PASSED]"
    fi

}
trap on_exit EXIT

set -e
set -x

APP_URL="http://localhost:5000"

for arg in ${*} ; do
    if [[ ${arg} =~ ^\-\-url= ]] ; then APP_URL=${arg##--url=} ; fi
done

APP_HOSTNAME=$(echo ${APP_URL} | sed -E -e 's_.*://([^/@]*@)?([^/:]+).*_\2_')
CURL_OPTS="-s --noproxy ${APP_HOSTNAME}"

install_jq(){
    if type jq > /dev/null 2>&1; then return 0 ; fi
    JQ_DOWNLOAD_URL="https://github.com/stedolan/jq/releases"
    JQ_VERSION="1.5"
    JQ_INSTALL_DIR=/tmp/bin
    uname=$(uname)
    mkdir -p ${JQ_INSTALL_DIR} 2>&1 || true
    if [ "${uname}" = "Linux" ] ; then
        DOWNLOAD_URL="${JQ_DOWNLOAD_URL}/download/jq-${JQ_VERSION}/jq-linux64"
    elif [ "${uname}" = "Darwin" ] ; then
        DOWNLOAD_URL="${JQ_DOWNLOAD_URL}/download/jq-${JQ_VERSION}/jq-osx-amd64"
    else
        echo "jq not found in PATH"
        echo "Download it at ${JQ_DOWNLOAD_URL}"
        return 1
    fi
    curl -k -L ${DOWNLOAD_URL} > ${JQ_INSTALL_DIR}/jq
    chmod +x ${JQ_INSTALL_DIR}/jq
    export PATH="${JQ_INSTALL_DIR}:${PATH}"
}

#
# Common test functions
#

_upload_file(){
    local file=${1?"file argument required"}
    if [ ! -f ${file} ] ; then echo "${file} does not exist" ; return 1 ; fi
    curl ${CURL_OPTS} -X POST -F file=@${file} "${APP_URL}/files"
}

_delete_uploaded_file(){
    local filename=${1?"filename argument required"}
    curl ${CURL_OPTS} -X DELETE "${APP_URL}/files/${filename}"
}

_list_uploaded_files(){
    curl ${CURL_OPTS} -X GET "${APP_URL}/files" | jq '.Files[].name' |  tr -d '"'
}

_delete_all_files(){
    for filename in `_list_uploaded_files` ; do
        _delete_uploaded_file "${filename}"
    done
}

_download_uploaded_file(){
    local filename=${1?"filename argument required"}
    local target_file=${2?"target_file argument required"}
    curl ${CURL_OPTS} -X GET "${APP_URL}/files/${filename}" > ${target_file}
}

_has_file_in_listing(){
    local listing=${1?"listing file required"}
    if [ ! -f ${listing} ] ; then echo "${listing} does not exist" ; return 1 ; fi
    local filename=${2?"filename argument required"}
    if [ `cat ${listing} | egrep "^${filename}$" | wc -l | awk '{print $1}'` -eq 1 ] ; then
        echo "true"
    else
        echo "false"
    fi
}

_rename_uploaded_file(){
    local filename=${1?"filename argument required"}
    local newname=${2?"newname argument required"}
    curl ${CURL_OPTS} -X PUT "${APP_URL}/files/${filename}" -F "newname=${newname}"
}

_update_uploaded_file(){
    local filename=${1?"filename argument required"}
    local newfile=${2?"newfile argument required"}
    if [ ! -f ${newfile} ] ; then echo "${newfile} does not exist" ; return 1 ; fi
    curl ${CURL_OPTS} -X PUT "${APP_URL}/files/${filename}" -F file=@${newfile}
}

test_upload(){
    _delete_all_files

    echo "bar" > /tmp/foo
    _upload_file /tmp/foo

    _list_uploaded_files > /tmp/listing1

    if ! `_has_file_in_listing /tmp/listing1 "foo"` ; then
        echo "foo is not listed"
        return 1
    fi
}

#
# Tests
#

test_download(){
    _delete_all_files

    echo "bar" > /tmp/foo
    _upload_file /tmp/foo
    _download_uploaded_file "foo" /tmp/foo2

    if [ `cat /tmp/foo2` != "bar" ] ; then
        echo "downloaded foo does not contain 'bar'"
        return 1
    fi
}

test_numerize(){
    _delete_all_files

    echo "foo" > /tmp/bar
    _upload_file /tmp/bar
    _upload_file /tmp/bar
    _upload_file /tmp/bar

    _list_uploaded_files > /tmp/listing1

    if [ `cat /tmp/listing1 | wc -l | awk '{print $1}'` -ne 3 ] ; then
        echo "listing should have 3 entries"
        return 1
    fi

    if ! `_has_file_in_listing /tmp/listing1 "bar"` ; then
        echo "bar is not listed"
        return 1
    elif ! `_has_file_in_listing /tmp/listing1 "bar-1"` ; then
        echo "bar-1 is not listed"
        return 1
    elif ! `_has_file_in_listing /tmp/listing1 "bar-2"` ; then
        echo "bar-2 is not listed"
        return 1
    fi
}

test_rename(){
    _delete_all_files

    echo "pocus" > /tmp/hocus
    _upload_file /tmp/hocus

    _list_uploaded_files > /tmp/listing1
    if ! `_has_file_in_listing /tmp/listing1 "hocus"` ; then
        echo "hocus is not listed"
        return 1
    fi

    _rename_uploaded_file "hocus" "pocus"

    _list_uploaded_files > /tmp/listing2
    if ! `_has_file_in_listing /tmp/listing2 "pocus"` ; then
        echo "pocus is not listed"
        return 1
    fi
}

test_update(){
    _delete_all_files

    echo "bar" > /tmp/foo
    _upload_file /tmp/foo

    _list_uploaded_files > /tmp/listing1

    if ! `_has_file_in_listing /tmp/listing1 "foo"` ; then
        echo "foo is not listed"
        return 1
    fi

    echo "bar2" > /tmp/foo2
    _update_uploaded_file "foo" /tmp/foo2

    _download_uploaded_file "foo" /tmp/foo3
    if [ `cat /tmp/foo3` != "bar2" ] ; then
        echo "downloaded foo does not contain 'bar2'"
        return 1
    fi
}

install_jq
test_upload
test_download
test_numerize
test_rename
test_update
