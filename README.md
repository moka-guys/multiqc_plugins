# MultiQC Plugin for SEGLH
MultiQC modules for custom software and pipeline QC metrics at the SEGLH.
## Available modules

- `tso500` for TSO500 metrics output from Illumina's monolithic pipeline

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
* `seglh_plugin/modules/my_example/`
    * This folder contains a minimal MultiQC module which will execute along with all other MultiQC modules (as defined by the `setup.py` hook).

### Usage

To use this code, you need to install MultiQC and then your code. For example:

```bash
pip install MultiQC
python setup.py install
```

Use `python setup.py develop` if you're actively working on the code - then you don't need to rerun the installation every time you make an edit _(though you still do if you change anything in `setup.py`)_.

### Disabling the plugin

In this plugin, I have defined a single additional command line flag - e.g. `--disable-seglh-plugin`. When specified, it sets a new MultiQC config value to `True`. This is checked in every plugin function; the function then returns early if it's `True`.

In this way, we can effectively disable the plugin code and allow native MultiQC execution. Note that a similar approach could be used to _enable_ a custom plugin or feature.
