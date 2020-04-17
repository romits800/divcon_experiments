# Experiments for [DivCon](https://github.com/romits800/divCon)
This repo contains experiments for [DivCon](https://github.com/romits800/divCon).


## Prerequisites

[ROPgadget](http://shell-storm.org/project/ROPgadget/),[capstone](https://www.capstone-engine.org/lang_python.html),
[matplotlib](https://matplotlib.org/), numpy, uncertainties

```
pip install capstone matplotlib ROPgadget numpy uncertainties
```

You may need to install tk:
```
sudo apt-get install python-tk
```


#### Python libraries


#### Install DivCon

Follow the instruction in [DivCon](https://github.com/romits800/divCon).

Set environment variable DIVCON_PATH

```bash
export DIVCON_PATH=/path/to/divcon
```

#### Install the llc unison extension
Clone the git repository with Unison extension:

```
git clone https://github.com/unison-code/llvm.git
```

Select the unsion branch:
```
git branch -b release_38-unison
```

Install llc:
```
mkdir build
cmake -G "Unix Makefiles" ..
make && sudo make install
```

## Run the experiments
To run the experiments in parallel write:

```bash
make run-par
```

### Extract aggregated data

```bash
make aggr
```

then:

```bash
make merge
```

and then :

```bash
make results
```


### Calculate gadget survival

```bash
make gadgets
```

#### Extract .csv files

```bash
make extract
```


