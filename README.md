# Experiments for [DivCon](https://github.com/romits800/divCon)
This repo contains experiments for [DivCon](https://github.com/romits800/divCon).


## Prerequisites

[ROPgadget](http://shell-storm.org/project/ROPgadget/)

#### Python libraries

[capstone](https://www.capstone-engine.org/lang_python.html)

[matplotlib](https://matplotlib.org/)

#### Install DivCon

Follow the instruction in [DivCon](https://github.com/romits800/divCon).

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


