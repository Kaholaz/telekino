# Telekino

<div style="display:flex; align-items:center; justify-content: center;">
    <img src="https://home.samfundet.no/~arunang/thumbnail-min.png" alt="thumbnail" style="max-width: 1200px" loading="lazy" />
</div>

## Description


Telekino is a algorithm for finding optimal connection between endpoints in a mobile network. Each node makes its own decisions based on the connection it has to its neighbors. The algorithm is based on the distributed Bellman-Ford algorithm. Detailed information about the algorithm can be found in the [report](report.pdf).

A command line tool for testing and visualizing the algorithm is provided. The tool can be used to test the algorithm with different parameters and to visualize the results. The tool simulates a network and displays the simulation using [matplotlib](https://matplotlib.org/).

## Requirements

- Python 3.9+
- Python venv module

## Installation

```shell
python -m venv venv && source venv/bin/activate
```

```shell
pip install -r requirements.txt
```

And if you also would like to develop and contribute:

```shell
pip install -r requirements-dev.txt
```

```shell
pre-commit install
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

## C++ implementation
An implementation in C++ is also provided. The C++ implementation is multithreaded. The implementation is not as flexible as the Python implementation, and is unstable. The C++ implementation is therefore not recommended for use, but can be tested if desired. The C++ implementation can sometimes get Segmentation Faults, and must be re-run if this happens. To run the C++ implementation, make and G++ 11 or higher is required.

The C++ implementation can be compiled with the following command in  the [cpp](cpp) directory:   

```shell
 make
 ```

The program can be run with the following command:
    
```shell
./telekino
```

The only way to visualize the simulation is to use a graphing tool and a csv file as input. The result can be copied into a file, and visualized using a online graphing tool like [csvplot](https://www.csvplot.com/).

## To developers

Black and ruff is used for formatting and linting. The following command can be used to format the code:

```shell
black .
```

Please use the [pre-commit](https://pre-commit.com/) framework to ensure code-quality for committed code. Once the development environment has been set up, run `pre-commit install` to install the pre-commit hook.

