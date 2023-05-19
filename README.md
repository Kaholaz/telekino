# Telekino

## Description

Telekino is a algorithm for finding optimal connection between endpoints in a network. Each node makes its own decisions based on the information it has about its neighbors. The algorithm is based on the distributed Bellman-Ford algorithm. Detailed informmation about the algorithm can be found in the [report](report.pdf).

A command line tool for testing and visualizing the algorithm is provided. The tool can be used to test the algorithm with different parameters and to visualize the results. The tool simulates a network and displays the simulation using [matplotlib](https://matplotlib.org/)

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

Arguments can be seen with the following command:

```shell
python main.py --help
```

Node count and endpoints must be set for the program to work:

### Example

```shell
python main.py -n 10 -e 2
```

## To developers

Black and pylint is used for formatting and linting. The following command can be used to format the code:

```shell
black .
```
