#!/usr/bin/env python
"""
Setup Script to import all entry points for custom modules 
needed for GSTT Specific QC checks

For more information about MultiQC, see http://multiqc.info
"""

from setuptools import setup, find_packages

version = '1.0.0'

setup(
    name = 'seglh_plugin',
    version = version,
    author = 'SE GLH GSTT Bioinformatics Team',
    author_email = 'gsttbioinformatics@synnovis.co.uk',
    description = "Plugin for GSTT SEGLH",
    long_description = __doc__,
    keywords = 'bioinformatics',
    url = 'https://github.com/moka-guys/multiqc_plugins',
    download_url = 'https://github.com/moka-guys/multiqc_plugins/releases',
    license = 'MIT',
    packages = find_packages(),
    include_package_data = True,
    install_requires = [
        'multiqc'
    ],
    entry_points = {
        'multiqc.modules.v1': [
            'sambamba_chanjo = seglh_plugin.modules.sambamba_chanjo:MultiqcModule',
            'Bases2Fastq_Import = seglh_plugin.modules.Bases2Fastq_Import:MultiqcModule',
        ],
        'multiqc.cli_options.v1': [
            'disable_plugin = seglh_plugin.cli:disable_plugin'
        ],
        'multiqc.hooks.v1': [
            'execution_start = seglh_plugin.custom_code:seglh_plugin_execution_start'
        ]
    },
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: JavaScript',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Visualization',
    ],
)
