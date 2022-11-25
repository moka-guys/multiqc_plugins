#!/bin/sh
MULTIQC_VERSION=$(sed -n 's/^.*MULTIQC_VERSION=\(.*\)$/\1/p' Dockerfile)
TAG=$(sed -n 's/^.*MULTIQC_PLUGIN_VERSION=\(.*\)$/\1/p' Dockerfile)
echo Building version $MULTIQC_VERSION of MultiQC with seglh multiqc_plugin version $TAG
docker build -t seglh/multiqc_$MULTIQC_VERSION:$TAG .
