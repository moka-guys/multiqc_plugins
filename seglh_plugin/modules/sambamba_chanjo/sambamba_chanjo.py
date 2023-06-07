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

def autocast(x):
    '''automatically typecasts numerical values to int or float'''
    if re.match('^(\d+)\.(\d+)$', x):
        return float(x)
    elif re.match('^(\d+)$', x):
        return int(x)
    else:
        return x
    
class MultiqcModule(BaseMultiqcModule):
    def __init__(self):
        # Halt execution if we've disabled the plugin
        if config.kwargs.get('disable_plugin', True):
            return None
        
        # Initialise the parent module Class object
        super(MultiqcModule, self).__init__(
            name = 'sambamba_chanjo',
            target = "sambamba_chanjo",
            anchor = 'sambamba_chanjo',
            href = 'https://github.com/moka-guys/multiqc_plugins',
            info = "sambamba_chanjo gene level coverage."
        )

        # Find and load any input files for this module
        self.sambamba_chanjo_data_samples = dict()
        self.source_files = dict()
        self.sambamba_chanjo_data_groups = defaultdict(list)
        for f in self.find_log_files('sambamba_chanjo'):
            self.sambamba_chanjo_data_samples[f['s_name']]= {}
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

        # create the result table
        self.add_section(
            name="Gene Level Coverage",
            anchor="sambamba_chanjo-bysample",
            description="Coverage metrics for each sample based on target assay",
            plot=self.sample_stats_table(),
            )
        
    def sample_stats_table(self):
        '''
        create a table with the sample statistics
        '''
        headers = OrderedDict()
        for samples in self.sambamba_chanjo_data_samples:
            for gene in sorted(self.sambamba_chanjo_data_samples[samples]):
                headers[gene] = {
                "title": gene,
                "description": "percentage genes covered at target coverage",
                "hidden": False,
                'scale': 'BuGn',
            }
        
        # Table config
        table_config = {
            "namespace": "sambamba_chanjo",
            "id": "sambamba_chanjo-sample-stats-table",
            "table_title": "Sambamba_chanjo Sample coverage Statistics",
            "no_beeswarm": True,
        }

        return table.plot(self.sambamba_chanjo_data_samples, headers, table_config)       

    def parse_file(self, f):
        '''Parses the Metrics output file
        CSV file with header, one row per variant type

        input:
            f: file handle
        output:
            None
        '''
        for line in f['f'].splitlines():
            #check if its the correct file
            if line.startswith('gene symbol'):
                continue
            #
            elif line.startswith('#') or len(line) == 0 or re.match(r'^\s+$',line):
                # comment or empty line (reset)
                continue
            else:
                #parse data
                gene, coverage = line.rstrip().split('\t')
                self.sambamba_chanjo_data_samples[f['s_name']][gene] = float(coverage)


