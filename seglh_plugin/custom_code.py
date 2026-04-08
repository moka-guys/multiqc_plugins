#!/usr/bin/env python
from __future__ import print_function
from importlib.metadata import version
import logging
from multiqc import config

log = logging.getLogger('multiqc')

config.seglh_plugin_version = version("seglh_plugin")

def seglh_plugin_execution_start():
    if getattr(config, 'disable_plugin', False):
        return None

    log.info("Running SEGLH MultiQC Plugin v{}".format(config.seglh_plugin_version))

    if 'sambamba_chanjo' not in config.sp:
        config.sp.update({'sambamba_chanjo': {'fn': '*.gene_level.txt'}})
    if 'Bases2Fastq_Import/run' not in config.sp:
        log.info("Bases2Fastq RunStats file not found in config.sp")
        config.sp.update({'Bases2Fastq_Import/run': {'fn': 'RunStats.json', 'contents': 'SampleStats', 'num_lines': 100}})
    if 'Bases2Fastq_Import/project' not in config.sp:
        log.info('Bases2Fastq Project RunStats file not found in config.sp')
        config.sp.update({'Bases2Fastq_Import/project': {'fn': '*_RunStats.json', 'contents': 'SampleStats', 'num_lines': 100}})
    if 'Bases2Fastq_Import/manifest' not in config.sp:
        log.info('Bases2Fastq RunManifest.csv not found in config.sp')
        config.sp.update({'Bases2Fastq_Import/manifest': {'fn': 'RunManifest.json', 'contents': 'Settings', 'num_lines': 100}})

    config.fn_clean_exts.extend([
        '.my_tool_extension',
        '.removeMetoo'
    ])
    config.fn_ignore_paths.extend([
        '*/my_awesome_pipeline/fake_news/*',
        '*/my_awesome_pipeline/red_herrings/*',
        '*/my_awesome_pipeline/noisy_data/*',
        '*/my_awesome_pipeline/rubbish/*'
    ])