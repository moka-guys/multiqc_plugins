#!/usr/bin/env python
""" MultiQC example plugin functions

We can add any custom Python functions here and call them
using the setuptools plugin hooks.
"""

from __future__ import print_function
from pkg_resources import get_distribution
import logging

from multiqc.utils import report, util_functions, config

# Initialise the main MultiQC logger
log = logging.getLogger('multiqc')

# Save this plugin's version number (defined in setup.py) to the MultiQC config
config.seglh_plugin_version = get_distribution("seglh_plugin").version


# Add default config options for the things that are used in MultiQC_NGI
def seglh_plugin_execution_start():
    """ Code to execute after the config files and
    command line flags have been parsedself.

    This setuptools hook is the earliest that will be able
    to use custom command line flags.
    """

    # Halt execution if we've disabled the plugin
    if config.kwargs.get('disable_plugin', True):
        return None

    log.info("Running SEGLH MultiQC Plugin v{}".format(config.seglh_plugin_version))

    # Add to the main MultiQC config object.
    # User config files have already been loaded at this point
    #   so we check whether the value is already set. This is to avoid
    #   clobbering values that have been customised by users.

    # Add to the search patterns used by modules (somehow the YAML search patterns file is not loaded)
    if 'tso500' not in config.sp:
        config.update_dict( config.sp, { 'tso500': { 'fn': 'MetricsOutput.tsv' } } )
    if 'sompy' not in config.sp:
        config.update_dict( config.sp, { 'sompy': {
            'fn': '*.stats.csv',
            'contents': ',sompyversion,sompycmd',
            'num_lines': 1
        } } )
    if 'exomedepth' not in config.sp:
        config.update_dict( config.sp, { 'exomedepth': {
            'fn': '*_readCount.csv',
            'contents': 'refsamples',
            'num_lines': 1
        } } )

    # Some additional filename cleaning
    config.fn_clean_exts.extend([
        '.my_tool_extension',
        '.removeMetoo'
    ])

    # Ignore some files generated by the custom pipeline
    config.fn_ignore_paths.extend([
        '*/my_awesome_pipeline/fake_news/*',
        '*/my_awesome_pipeline/red_herrings/*',
        '*/my_awesome_pipeline/noisy_data/*',
        '*/my_awesome_pipeline/rubbish/*'
    ])
