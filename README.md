# Overview
This repository contains scripts for network topologies testing

There are 3 cases implemented:
1. Possibility of direct matching real and test topologies search
2. Using switch and VLANs for testing
3. Using local switch with VLANs and cloud

Each case has its script to run - **case*number*_*name*.py**. Input files should be stored in *input* directory. Output files are stored in **case*number*_out** directory.

## First approach
Input - *phys_infrastructure.csv* and *test_infrastructure.csv* files that describe topologies in format **host,interface,host,interface**

Output - result files for all found matches:
- matching*number*.png - image with topologies overlay
- matching_matrix*number*.csv - result in format **physical_host,physical_port,test_host,test_port**

## Second and third approaches
Input:
- *nodes_switch_map.yml* - describes connections between machines and switch with appropriate ports
- *test_infrastructure.csv* - file that describes test topology in format host,interface,host,interface

Output - results text file with result matrix and description of connections between nodes and switch[es]

## Package *common*
Contains code for drawing results of the first approach and mapping algorithm for 2nd and 3rd approaches