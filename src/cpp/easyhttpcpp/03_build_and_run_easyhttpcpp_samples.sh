#!/bin/bash

set -e

CWD=`pwd`

mkdir -p _external
cd _external

cd easyhttpcpp/samples

rm -rf _build && mkdir _build
cd _build

CMAKE_TOOLCHAIN_FILE_ARG=""
if [[ "`uname`" == "Darwin" ]]; then
    # workaround to find_package(OpenSSL)
    CMAKE_TOOLCHAIN_FILE_ARG="-DCMAKE_TOOLCHAIN_FILE=${CWD}/cmake/AppleToolchain.cmake"
fi

# build all samples with Debug lib
cmake -DCMAKE_BUILD_TYPE=Debug -DCMAKE_CXX_STANDARD=11 -DCMAKE_CXX_STANDARD_REQUIRED=ON -DCMAKE_PREFIX_PATH=${CWD}/_install ${CMAKE_TOOLCHAIN_FILE_ARG} ../
make

# run all samples
./bin/easyhttpcpp-samples-SimpleHttpClient https://github.com/sony/easyhttpcpp

# # build all samples with Release lib
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CXX_STANDARD=11 -DCMAKE_CXX_STANDARD_REQUIRED=ON -DCMAKE_PREFIX_PATH=${CWD}/_install ${CMAKE_TOOLCHAIN_FILE_ARG} ../
make -j7

# run all samples
./bin/easyhttpcpp-samples-SimpleHttpClient https://github.com/sony/easyhttpcpp
./bin/easyhttpcpp-samples-AsyncHttpClient https://github.com/sony/easyhttpcpp

cd ${CWD}