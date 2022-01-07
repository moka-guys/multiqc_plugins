#!/bin/sh

rm -rf multiqc_*
python setup.py install
multiqc -c test_data/multiqc_config.yaml test_data/live
