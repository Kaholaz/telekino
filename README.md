# Telekino

## Description

Telekino is a algorithm for finding optimal connection between endpoints in a mobile network. Each node makes its own decisions based on the connection it has to its neighbors. The algorithm is based on the distributed Bellman-Ford algorithm. Detailed informmation about the algorithm can be found in the [report](report.pdf).

A command line tool for testing and visualizing the algorithm is provided. The tool can be used to test the algorithm with different parameters and to visualize the results. The tool simulates a network and displays the simulation using [matplotlib](https://matplotlib.org/).

## Requirements

- Python 3.10
- Python 3.10 venv module

## Installation

```shell
python -m venv venv && source venv/bin/activate
```

```shell
pip install -r requirements.txt
```

## Usage

The program can be run with the following command:

```shell
python main.py
```

To see all the available simulation parameters, run the following command:

```shell
python main.py --help
```

The simulation is displayed using matplotlib. Plus signs represents endpoints and nodes are represented by dots. The connection between the nodes are represented by lines. The color of the lines represents the connection quality. The worse the connection, the lighter the color is.

Node count and endpoints are the only required parameters. Large and long simulations with -d flag can take a long time to complete due to matplotlib. It is therefore recommended to run long simulations without the -d flag. If you are running a large simulation, it is also recommended to set the --max-connections parameter to a low value to avoid long simulation times.

### Example

```shell
python main.py -n 10 -e 2
```

Further examples can be found in the [report](report.pdf).

## To developers

Black and pylint is used for formatting and linting. The following command can be used to format the code:

```shell
black .
```
