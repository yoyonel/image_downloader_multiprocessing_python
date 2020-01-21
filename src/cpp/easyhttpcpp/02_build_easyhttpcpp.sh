#!/bin/bash

set -e

CWD=`pwd`

mkdir -p _external
cd _external

# [[ ! -d easyhttpcpp ]] && git clone -b 1.0.0 --depth=1 --single-branch https://github.com/sony/easyhttpcpp.git
[[ ! -d easyhttpcpp ]] && git clone -b master --depth=1 --single-branch https://github.com/sony/easyhttpcpp.git
cd easyhttpcpp

rm -rf _build && mkdir _build
cd _build

CMAKE_TOOLCHAIN_FILE_ARG=""
if [[ "`uname`" == "Darwin" ]]; then
    # workaround to find_package(OpenSSL)
    CMAKE_TOOLCHAIN_FILE_ARG="-DCMAKE_TOOLCHAIN_FILE=${CWD}/cmake/AppleToolchain.cmake"
fi

# build easyhttpcpp in Release mode
cmake -DCMAKE_BUILD_TYPE=Release \
    -DEASYHTTPCPP_VERBOSE_MESSAGES=ON \
    -DCMAKE_CXX_STANDARD=11 \
    -DCMAKE_CXX_STANDARD_REQUIRED=ON \
    -DCMAKE_PREFIX_PATH=${CWD}/_install \
    -DCMAKE_INSTALL_PREFIX=${CWD}/_install \
    ${CMAKE_TOOLCHAIN_FILE_ARG} \
    ../

make -j7 install

cd ${CWD}