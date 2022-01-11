#!/bin/sh
TAG=$(sed -n 's/^.*MULTIQC_VERSION=\(.*\)$/\1/p' Dockerfile)
echo Building version $TAG of MultiQC
docker build -t seglh/multiqc:$TAG .
