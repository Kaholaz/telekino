import argparse
from typing import Union, Sequence, Any, Optional

from simulation import simulate


def define_args(argparser: argparse.ArgumentParser) -> None:
    argparser.add_argument(
        "-n",
        "--number-of-nodes",
        type=int,
        required=True,
        help="Number of moving nodes",
    )
    argparser.add_argument(
        "-e",
        "--number-of-endpoints",
        type=int,
        required=True,
        help="Number of endpoints to generate",
    )
    argparser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Create a seed to generate the same random network each time",
    )
    argparser.add_argument(
        "-s",
        "--simulation-steps",
        type=int,
        default=1000,
        help="Number of steps to simulate",
    )
    argparser.add_argument(
        "-w",
        "--wiggle",
        type=float,
        default=0.01,
        help=(
            "Distance (dx and dy) the node travels when calculating the move direction"
        ),
    )
    argparser.add_argument(
        "-m",
        "--move-strength",
        type=float,
        default=0.01,
        help="Distance the node moves each step",
    )
    argparser.add_argument(
        "--transmit-from-endpoints",
        action="store_true",
        help="Choose whether endpoints can emit signals back to nodes",
    )

    class DomainAction(argparse.Action):
        def __call__(
            self,
            parser: argparse.ArgumentParser,
            namespace: argparse.Namespace,
            values: Union[str, Sequence[Any], None],
            option_string: Optional[str] = None,
        ) -> None:
            if values is None or type(values) == str or len(values) != 2:
                raise argparse.ArgumentError(
                    self, "The domain needs to be a sequence of two values"
                )
            if values[0] >= values[1]:
                raise argparse.ArgumentError(
                    self, "The first value needs to be smaller than the second value"
                )
            setattr(namespace, self.dest, values)

    argparser.add_argument(
        "-nd",
        "--node-domain",
        nargs=2,
        type=float,
        action=DomainAction,
        default=[-20, 20],
        help="Domain of where the node positions are generated",
    )
    argparser.add_argument(
        "-ed",
        "--endpoint-domain",
        nargs=2,
        type=float,
        action=DomainAction,
        default=None,
        help=(
            "Domain of where the endpoint positions are generated. this defaults to the"
            " node domain"
        ),
    )

    argparser.add_argument(
        "-d",
        "--draw-steps",
        action="store_true",
        help="Draw each step of the simulation on the graph",
    )

    argparser.add_argument(
        "-x",
        "--export",
        action="store_true",
        help="Export the simulation as a png",
    )

    def positive_float(value: str) -> float:
        try:
            fvalue = float(value)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"{value} is an invalid positive float value"
            )

        if fvalue <= 0:
            raise argparse.ArgumentTypeError(
                f"{value} is an invalid positive float value"
            )
        return fvalue

    argparser.add_argument(
        "--max-speed",
        type=positive_float,
        default=5,
        help="Maximum speed of the nodes",
    )

    def positive_int(value: str) -> int:
        try:
            ivalue = int(value)
        except ValueError:
            raise argparse.ArgumentTypeError(
                f"{value} is an invalid positive int value"
            )

        if ivalue <= 0:
            raise argparse.ArgumentTypeError(
                f"{value} is an invalid positive int value"
            )
        return ivalue

    argparser.add_argument(
        "-c",
        "--max-connections",
        type=positive_int,
        default=-1,
        help=(
            "Maximum number of connections per node. Improves simulation speed on large"
            " networks"
        ),
    )


def main() -> None:
    argparser = argparse.ArgumentParser(
        prog="network-simulation",
        description=(
            "Simulate a network of nodes that move around to minimize the cost to the"
            " endpoints."
        ),
    )
    define_args(argparser)

    args = argparser.parse_args()

    # Run the simulation with argparse arguments
    try:
        simulate(
            args.simulation_steps,
            args.wiggle,
            args.move_strength,
            args.number_of_nodes,
            args.number_of_endpoints,
            args.seed,
            args.transmit_from_endpoints,
            args.node_domain,
            args.endpoint_domain,
            args.draw_steps,
            args.export,
            args.max_speed,
            args.max_connections,
        )
    except ValueError as e:
        print(e)
        exit(1)


if __name__ == "__main__":
    main()
