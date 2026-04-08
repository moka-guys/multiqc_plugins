# MultiQC Plugin for SEGLH
MultiQC modules for custom software and pipeline QC metrics at the SEGLH. 
## Available modules

- `tso500` for TSO500 metrics output from Illumina's monolithic pipeline
- `sompy` for som.py benchmarking results (displays recall metrics only as default)
- `exomedepth` for exomedepth readcount, coorelation and model fitting metrics
- `sambamba_chanjo` sambamba gene level coverage data

## Development

Please use this plugin when writing new modules.

Please refer to the main MultiQC documentation:
http://multiqc.info/docs/#coding-with-multiqc

### Overview of files

* `setup.py`
    * Where the `setuptools` plugin hooks are defined. This is where you tell MultiQC where to find your code.
    * This file also defines how your plugin should be installed, including required python packages.
* `seglh_plugin/`
    * Installable Python packages are typically put into a directory with the same name.
* `seglh_plugin/__init__.py`
    * Python packages need an `__init__.py` file in every directory. Here, these are mostly empty (except the one in the `my_example` folder, which contains a shortcut to make the `import` statement shorter).
    * If you prefer, you can put all code in these files and just reference the directory name only.
* `seglh_plugin/cli.py`
    * Additional command line parameters to add to MultiQC
* `seglh_plugin/custom_code.py`
    * File to hold custom functions that can tie into the main MultiQC execution flow.
    * In this file, we define some new config defaults, including the search patterns used by the example module
* `seglh_plugin/modules/modulename/`
    * This folder contains a MultiQC module which will execute along with all other MultiQC modules (as defined by the `setup.py` hook).
* `requirements.txt`
    * This file contains all the relevant packages needed to run the core MultiQC module. If MultiQC Version is upgraded, this file will need to be checked to 
    make sure no new packages are needed for QC analysis

### Overview of Custom Modules

* `sambamba_chanjo`
    * This module creates coverage statistics per sample. Specifically giving percentage of genes covered at a target coverage
* `Bases2Fastq_Import`
    * This module provides QC metrics in relation to the demultiplexing tool, Bases2Fastq for Aviti sequenced runs. This module is directly imported
    from https://github.com/Elembio/MultiQC which is Element Biosciences MultiQC repo thats is forked off the main MultQC repository.
    * This is the MultiQC analysis that is provided when the Bases2Fastq docker tool is used however now combines it with the rest of our GSTT QC analysis.
    * Small changes to the code have been made to include a column in the Unassigned Indexes table to identify whether the read is PhiX or not

### Usage

To use this code, you need to install MultiQC and then your code. For example:

```bash
pip install MultiQC
python setup.py install
```

Use `python setup.py develop` if you're actively working on the code - then you don't need to rerun the installation every time you make an edit _(though you still do if you change anything in `setup.py`)_.

### Docker

To build the docker image simply run the `build.sh` script. It will create an image with the correct version of multiqc and tag version for the plugins (e.g. `seglh/multiqc_v1.31:v2.0.0`).

### DNANexus Upload and Usage

Once the docker has been made, the following steps can be followed to upload to DNANexus and use with the `dnanexus_multiqc` module:
* `docker save {docker_name:docker_tag} > {docker_name:docker_tag}.tar`
* `gzip {docker_name:docker_tag}.tar`
* `dx upload {docker_name:docker_tag}.tar.gz` - Make sure you are in an appropriate dx project before running this or specify project ID to load into
* Identify the new file ID for this docker tar file and update the relevant file IDs in the `dnanexus_multiqc` module where this is being called

### Disabling the plugin

In this plugin, I have defined a single additional command line flag - e.g. `--disable-seglh-plugin`. When specified, it sets a new MultiQC config value to `True`. This is checked in every plugin function; the function then returns early if it's `True`.

In this way, we can effectively disable the plugin code and allow native MultiQC execution. Note that a similar approach could be used to _enable_ a custom plugin or feature.

### Future Upgrade
* If the MultiQC Version is upgraded in the future, please reference the 'requirements.txt' file in this repository with the requirements stated within the Core MultiQC Repository to ensure all necessary packages are included in this docker
