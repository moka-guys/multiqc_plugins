
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
    ed_metric_configs = {
        'min.refs': {
            "title": "Minimum Reference Samples",
            "description": "Requested minimum number of reference samples",
            "min": 1,
            "suffix": " samples",
            "hidden": True
        },
        'refsamples': {
            "title": "Reference samples",
            "description": "Size of reference set",
            "min": 1,
            "suffix": " samples",
            "scale": "Greens",
            "format": "{:,.0f}"
        },
        'correlations': {
            "title": "Reference correlation",
            "description": "Correlation of reference samples",
            "scale": "RdYlGn",
            "min": 0.8,
            "max": 1,
            "format": "{:,.3f}"
        },
        'expected.BF': {
            "title": "Expected BF",
            "description": "Exprected Bayes Factor",
            "scale": "Greens",
            "format": "{:,.2f}"
        },
        'phi': {
            "title": "Dispersion",
            "description": "Phi dispersion metric of fitted model",
            "scale": "Greens",
            "format": "{:,.2e}"
        },
        'RatioSd': {
            "title": "RatioSd",
            "hidden": True
        },
        'mean.p': {
            "title": "Mean p",
            "hidden": True
        },
        'median.depth': {
            "title": "Depth (median)",
            "description": "Median Read Depth",
            "suffix": "x",
            "format": "{:,.0f}"
        },
        'batch.maxcor': {
            "title": "Correlation (max)",
            "description": "Maximum correlation within batch",
            "min": 0.8,
            "max": 1,
            "format": "{:,.3f}"
        },
        'batch.mediancor': {
            "title": "Correlation (median)",
            "description": "Median correlation within batch",
            "min": 0.8,
            "max": 1,
            "format": "{:,.3f}"
        },
        'coeff.var': {
            "title": "Variation",
            "description": "Coefficient of variation (RPKM)",
            # "scale": "RdYlGr-rev",
            "scale": "Reds",
            "format": "{:,.2f}"
        },
    }

    def __init__(self):
        # Halt execution if we've disabled the plugin
        if config.kwargs.get('disable_plugin', True):
            return None

        # Initialise the parent module Class object
        super(MultiqcModule, self).__init__(
            name = 'ExomeDepth metrics',
            target = "exomedepth",
            anchor = 'exomedepth',
            href = 'https://github.com/moka-guys/multiqc_plugins',
            info = " SEGLH CNV analysis metrics."
        )

        # Find and load any input files for this module
        self.ed_data_samples = dict()
        self.source_files = dict()
        for f in self.find_log_files('exomedepth'):
            self.parse_file(f)
            self.add_data_source(
                s_name=f['s_name'],
                source=os.path.join(f['root'],f['fn']),
                module="exomedepth",
                section="exomedepth-bysample",
            )

        # Filter out samples matching ignored sample names
        self.ed_data_samples = self.ignore_samples(self.ed_data_samples)

        # Nothing found - raise a UserWarning to tell MultiQC
        if len(self.ed_data_samples) == 0:
            log.debug("Could not find any reports in {}".format(config.analysis_dir))
            raise UserWarning

        log.info("Found {} reports".format(len(self.ed_data_samples)))

        # Write parsed report data to a file
        self.write_data_file(self.ed_data_samples, 'multiqc_exomedepth')
        
        # write data table
        self.add_section(
            name="Sample Statistics",
            anchor="exomedepth-bysample",
            description="ExomeDepth metrics for each sample",
            plot=self.sample_stats_table(),
        )
        # batch plots ()

    def sample_stats_table(self):
        '''
        create a table with the sample statistics
        '''
        headers = OrderedDict()
        for sample in self.ed_data_samples.keys():
            for metric in self.ed_data_samples[sample]:
                # get metrics definiton template or create from scratch
                # extract metric name and unit
                if metric not in headers.keys():
                    name = metric.replace('.','').replace('_',' ').capitalize()
                    headers[metric] = {
                        'title': name,
                        'description': metric
                    }
                    # Overwrite default dict with custom values
                    try:
                        headers[metric].update(self.ed_metric_configs[metric])
                    except KeyError:
                        pass
                else:
                    continue
        # Table config
        table_config = {
            "namespace": "exomedepth",
            "id": "exomedepth-sample-stats-table",
            "table_title": "Exomedepth Sample Statistics",
            "no_beeswarm": False,
        }

        return table.plot(self.ed_data_samples, headers, table_config)


    def parse_file(self, f):
        '''Parses the Metrics output file
        input:
            f: file handle
        output:
            None
        
        '''
        metrics_header, skipped = [], 0
        for i, line in enumerate(f['f'].splitlines()):
            # match data block header
            m = re.match(r'^\[(.*)\]\s*$', line)
            if line.startswith('#') or len(line) == 0 or re.match(r'^\s+$',line):
                # skipped line (comment or empty) 
                skipped += 1
                continue
            elif i-skipped == 0 and line.startswith('sample'):
                # is the header line
                metrics_header = line.rstrip().split('\t')
            else:
                # parse data
                f = line.rstrip().split('\t')
                m = re.match(r'([^_]+_\d{2}_[^_]+_\w{2}_[MFU]_[^_]+_Pan\d+(?:_S\d+)?)',f[0])
                if m:
                    sample = m.group(1)
                    if sample not in self.ed_data_samples:
                        self.ed_data_samples[sample] = dict()
                    self.ed_data_samples[sample] = dict(zip(metrics_header[1:], f[1:]))
