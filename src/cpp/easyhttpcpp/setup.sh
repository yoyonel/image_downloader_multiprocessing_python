#!/usr/bin/env bash
# https://stackoverflow.com/questions/20280726/how-to-git-clone-a-specific-tag
# https://github.com/sony/easyhttpcpp/tree/master/scripts
# https://github.com/sony/easyhttpcpp/wiki/Installing-EasyHttp
set -e
set -x

sudo apt-get install libsqlite3-dev libssl-dev

ROOT_DIR=$(pwd)/_external
POCO_BUILD_DIR=${ROOT_DIR}/poco/_build
EASYHTTPCPP_SRC_DIR=${ROOT_DIR}/easyhttpcpp
EASYHTTPCPP_BUILD_DIR=${EASYHTTPCPP_SRC_DIR}/_build
EASYHTTPCPP_SAMPLES_DIR=${EASYHTTPCPP_SRC_DIR}/samples
EASYHTTPCPP_SAMPLE_SIMPLEHTTPCLIENT_BUILD_DIR==${EASYHTTPCPP_SAMPLES_DIR}/SimpleHttpClient/_build

mkdir -p ${ROOT_DIR}
pushd ${ROOT_DIR}

[[ ! -d poco ]] && git clone -b tags/poco-1.7.9-release --single-branch https://github.com/pocoproject/poco.git
cd poco
#
mkdir -p ${POCO_BUILD_DIR}
cd ${POCO_BUILD_DIR}
rm -f CMakeCache.txt && cmake -DCMAKE_BUILD_TYPE=Release ../
make -j7
export Poco_DIR=${POCO_BUILD_DIR}

cd ${ROOT_DIR}
[[ ! -d easyhttpcpp ]] && git clone -b 1.0.0 --depth=1 --single-branch https://github.com/sony/easyhttpcpp.git
cd easyhttpcpp
#
mkdir -p ${EASYHTTPCPP_BUILD_DIR}
cd ${EASYHTTPCPP_BUILD_DIR}
rm -f CMakeCache.txt && cmake ..
make -j7
export easyhttpcpp_DIR=$(realpath easyhttpcpp)

#
cd ${EASYHTTPCPP_SAMPLES_DIR}/SimpleHttpClient
mkdir -p _build
cd _build
rm -f CMakeCache.txt && cmake ..
make -j7
#
./Project-SimpleHttpClient http://www.google.fr

popd