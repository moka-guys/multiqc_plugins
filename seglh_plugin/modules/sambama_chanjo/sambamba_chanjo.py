#!/usr/bin/env python

""" MultiQC example plugin module """

from __future__ import print_function
from collections import OrderedDict, defaultdict
import logging
import os
import re
from multiqc import config
from multiqc.plots import table
from multiqc.modules.base_module import BaseMultiqcModule

# Initialise the main MultiQC logger
log = logging.getLogger('multiqc')

class MultiqcModule(BaseMultiqcModule):
    # custom metric display configurations (keys override defaults)
    sambamba_chanjo_metric_configs = {
        'GENE_SYMBOL (NA)': {
            "title": "Gene Symbol",
            "description": "HGNC Gene Symbol"
        },
        'PERCENTAGE_BASES_COVERED_AT_100X (NA)': {
            "title": "Bases covered at 100X (%)",
            "description": "Gene level coverage of bases covered at 100X",
            "min": 100,
            "suffix": "%",
            "scale": "Reds",            
        },
    }

    def __init__(self):
        # Halt execution if we've disabled the plugin
        if config.kwargs.get('disable_plugin', True):
            return None
        
        # Initialise the parent module Class object
        super(MultiqcModule, self).__init__(
            name = 'sambamba_chanjo metrics',
            target = "sambamba_chanjo",
            anchor = 'sambamba_chanjo',
            href = 'https://github.com/moka-guys/multiqc_plugins',
            info = "sambamba_chanjo gene level coverage for Illumina TSO500 samples."
        )

        # Find and load any input files for this module
        self.sambamba_chanjo_data_samples = dict()
        self.source_files = dict()
        for f in self.find_log_files('sambamba_chanjo'):
            self.parse_file(f)
            self.add_data_source(
                s_name=f['s_name'],
                source=os.path.join(f['root'],f['fn']),
                module="sambamba_chanjo",
                section="sambamba_chanjo-bysample",
            )

        # Filter out samples matching ignored sample names
        self.sambamba_chanjo_data_samples = self.ignore_samples(self.sambamba_chanjo_data_samples)

        # Nothing found - raise a UserWarning to tell MultiQC
        if len(self.sambamba_chanjo_data_samples) == 0:
            log.debug("Could not find any Sambamba_chanjo reports in {}".format(config.analysis_dir))
            raise UserWarning

        log.info("Found {} reports".format(len(self.sambamba_chanjo_data_samples)))

        # Write parsed report data to a file
        self.write_data_file(self.sambamba_chanjo_data_samples, 'multiqc_sambamba_chanjo')

    def parse_file(self, f):
        '''Parses the Metrics output file
        CSV file with header, one row per variant type

        input:
            f: file handle
        output:
            None
        '''
        header = []
        group, sample_names = '', []
        for line in f['f'].splitlines():
            if line.endswith('percent_bases_covered at 100x'):
                # header
                header = line.rstrip().split('\t') 
            elif line.startswith('#') or len(line) == 0 or re.match(r'^\s+$',line):
                # comment or empty line (reset)
                continue
            else:
                # parse data
                f = line.rstrip().split('\t')
                group = f[1]
                m = re.match(r'^([^_]+_\d{2}_[^_]+_\w{2}_[MFU]_[^_]+_Pan\d+)',f[0])
                if m:
                    sample = m.group(1)
                    if sample not in self.sambamba_chanjo_data_samples:
                        self.sambamba_chanjo_data_samples[sample] = dict()
                    self.sambamba_chanjo_data_samples[sample] = dict(zip(header[1:], f[1:]))
