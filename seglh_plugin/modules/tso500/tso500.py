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
    tso500_metric_configs = {
        'CONTAMINATION_SCORE (NA)': {
            "title": "Contamination Score",
            "description": "Estimated contamintion of sample",
            "scale": "Blues"
        },
        'CONTAMINATION_P_VALUE (NA)': {
            "title": "Contamination significance",
            "description": "Contamination P-value",
            "min": 0.05,
            "suffix": " (p-value)",
            "scale": "Greens",
            "format": "{:,.2f}"
        },
        'PCT_CONTAMINATION_EST (%)': {
            "title": "Estimated contamination",
            "description": "Estimated Contamination (%)",
            "suffix": "%",
            "scale": "Reds"
        },
        'COVERAGE_MAD (Count)': {
            "title": "Coverage MAD",
            "description": "Median absolute deviation of coverage",
            "suffix": "",
            "scale": "Oranges",
            "format": "{:,.3f}"
        },
        'PCT_EXON_50X (%)': {
            'placement' : 990
        },
        'PCT_EXON_100X (%)': {
            'placement' : 991
        },
        'MEDIAN_EXON_COVERAGE (Count)': {
            'placement' : 992   
        },
        'PCT_TARGET_0.4X_MEAN (%)': {
            'placement' : 1001
        },
        'PCT_TARGET_100X (%)': {
            'placement' : 1002   
        },
        'PCT_TARGET_250X (%)': {
            'placement' : 1003   
        },
        'MEDIAN_TARGET_COVERAGE (Count)': {
            'placement' : 1004    
        },
        'MEAN_TARGET_COVERAGE (Count)': {
            'placement' : 1005   
        },
    }

    # configures manual metric->group mappings
    special_groups = {
        'PCT_EXON_100X (%)': 'Coverage metrics',
        'PCT_EXON_50X (%)': 'Coverage metrics',
        'MEAN_TARGET_COVERAGE (Count)': 'Coverage metrics',
        'MEDIAN_TARGET_COVERAGE (Count)': 'Coverage metrics',
        'MEDIAN_EXON_COVERAGE (Count)': 'Coverage metrics',
        'PCT_TARGET_0.4X_MEAN (%)': 'Coverage metrics',
        'PCT_TARGET_100X (%)': 'Coverage metrics',
        'PCT_TARGET_250X (%)': 'Coverage metrics',
        'CONTAMINATION_P_VALUE (NA)': 'Contamination',
        'PCT_CONTAMINATION_EST (%)': 'Contamination',
        'CONTAMINATION_SCORE (NA)': 'Contamination'
    }

    def __init__(self):
        # Halt execution if we've disabled the plugin
        if config.kwargs.get('disable_plugin', True):
            return None

        # Initialise the parent module Class object
        super(MultiqcModule, self).__init__(
            name = 'TSO500 metrics',
            target = "tso500",
            anchor = 'tso500',
            href = 'https://github.com/moka-guys/multiqc_plugins',
            info = " Illumina TSO500 analysis blackbox plugin."
        )

        # Find and load any input files for this module
        self.tso500_data_samples = dict()
        self.tso500_data_limits = dict()
        self.tso500_data_groups = defaultdict(list)
        self.source_files = dict()
        for f in self.find_log_files('tso500'):
            self.parse_file(f)
            self.add_data_source(
                s_name=f['s_name'],
                source=os.path.join(f['root'],f['fn']),
                module="tso500",
                section="tso500-bysample",
            )

        # Filter out samples matching ignored sample names
        self.tso500_data_samples = self.ignore_samples(self.tso500_data_samples)

        # Nothing found - raise a UserWarning to tell MultiQC
        if len(self.tso500_data_samples) == 0:
            log.debug("Could not find any reports in {}".format(config.analysis_dir))
            raise UserWarning

        log.info("Found {} reports".format(len(self.tso500_data_samples)))

        # Write parsed report data to a file
        self.write_data_file(self.tso500_data_samples, 'multiqc_tso500')

        # # Add a number to General Statistics table
        # headers = OrderedDict()
        # for data_key in self.tso500_data_limits.keys():
        #     m = re.match(r'^([^\(]+)\(([^\)]+)\)_.*', data_key)
        #     if m:
        #         name = m.group(1).rstrip()
        #         headers[data_key] = {
        #             'title': name,
        #             'description': '',
        #             'min': self.tso500_data_limits['CONTAMINATION_SCORE (NA)'][0],
        #             'max': self.tso500_data_limits['CONTAMINATION_SCORE (NA)'][1],
        #             'scale': 'RdYlGn-rev',
        #             'format': '{:,.0f}'
        #         }
        # print(self.tso500_data_samples)
        # self.general_stats_addcols(self.tso500_data_samples, headers)

        for group in sorted(self.tso500_data_groups.keys()):
            metrics = self.tso500_data_groups[group]
            self.add_section(
                name=group,
                anchor="tso500-bysample",
                description="",
                plot=self.sample_stats_table(metrics),
            )

    def sample_stats_table(self, metrics):
        '''
        create a table with the sample statistics
        '''
        headers = OrderedDict()
        for metric in self.tso500_data_limits.keys():
            if metric in metrics:
                # get metrics definiton template or create from scratch
                m = re.match(r'^([^\(]+)\(([^\)]+)\)', metric)
                if m:
                    name = m.group(1).rstrip().replace('PCT_','').replace('_',' ').capitalize()
                    fieldtype = m.group(2)
                    if fieldtype == 'NA':
                        headers[metric] = {
                            'title': name,
                            'description': metric,
                            'scale': 'RdYlGn-rev',
                            'format': '{:,.2f}'
                        }
                    elif fieldtype == 'Count':
                        headers[metric] = {
                            'title': name,
                            'description': metric,
                            'suffix': '',
                            'scale': 'BuPu',
                            'format': '{:.0f}',
                        }
                    elif fieldtype == 'bp':
                        headers[metric] = {
                            'title': name,
                            'description': metric,
                            'suffix': 'bp',
                            'scale': 'RdYlGn',
                            'format': '{:.0f}',
                        }
                    elif fieldtype == '%':
                        headers[metric] = {
                            'title': name,
                            'description': metric,
                            'suffix': '%',
                            'min': 0,
                            'max': 100,
                            'format': '{:.0f}',
                            'scale': 'RdYlGn',
                        }
                    else:
                        headers[metric] = {
                            'title': name,
                            'description': metric,
                            'scale': 'RdYlGn-rev',
                            'format': '{:,.0f}'
                        }
                else:
                    continue
                # Overwrite default dict with custom values
                try:
                    headers[metric].update(self.tso500_metric_configs[metric])
                except KeyError:
                    pass
                # add LSL USL boundaries if defined
                if self.tso500_data_limits[metric][0] is not None:
                    headers[metric]['min'] = self.tso500_data_limits[metric][0]
                if self.tso500_data_limits[metric][1] is not None:
                    headers[metric]['max'] = self.tso500_data_limits[metric][1]
        # Table config
        table_config = {
            "namespace": "tso500",
            "id": "tso500-sample-stats-table",
            "table_title": "TSO500 Sample Statistics",
            "no_beeswarm": True,
        }

        return table.plot(self.tso500_data_samples, headers, table_config)


    def parse_file(self, f):
        '''Parses the Metrics output file
        input:
            f: file handle
        output:
            None
        
        '''
        group, sample_names = '', []
        for line in f['f'].splitlines():
            m = re.match(r'^\[(.*)\]\s*$', line)
            if line.startswith('#'):
                # comment 
                continue
            elif len(line) == 0 or re.match(r'^\s+$',line):
                # empty line (reset)
                group, sample_names = '', []
                continue
            elif m:
                # is a group header
                group = m.group(1)
            elif group:
                if group in ['Header']:
                    # global metrics/data
                    pass
                elif group.startswith('DNA'):
                    # DNA data line
                    if line.startswith("Metric "):
                        sample_names = line.rstrip().split('\t')[3:]
                        # add sample data dictionaries
                        for s in [ sample for sample in sample_names if sample not in self.tso500_data_samples.keys()]:
                            self.tso500_data_samples[s] = dict()
                    else:
                        # parse data
                        f = line.rstrip().split('\t')
                        metric = f[0]
                        lsl = float(f[1]) if f[1] != 'NA' else None
                        usl = float(f[2]) if f[2] != 'NA' else None
                        self.tso500_data_limits[metric] = (lsl, usl)
                        try:
                            self.special_groups[metric]
                        except KeyError:
                            self.tso500_data_groups[group].append(metric)
                        else:
                            self.tso500_data_groups[self.special_groups[metric]].append(metric)
                        data = f[3:]
                        for i, sample in enumerate(sample_names):
                            self.tso500_data_samples[sample][metric] = float(data[i])
                else:
                    pass # unknown group