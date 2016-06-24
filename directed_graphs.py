import argparse
import textwrap
import random

random.seed(0)

def graph_parser():
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            add_help=False
            )
    parser.add_argument('-n', type=int, help='number of vertices', default=10)
    parser.add_argument('-d', 
            help=textwrap.dedent("""
            There are two methods of specifiying groups
            The simpler one involves specifying number of vertices in each group
            Example: 10 20 41
            The second involves specifying total number and distribution
            Example: 10 0.5
            distribution of last value is automatically calculated by 1 - f1 - f2 ...
            """),
            nargs='*',
            type=float,
            default=[10])
    parser.add_argument('-e', type=int, 
            help="""
            There are two methods of specifiying additional edges
            The simpler one involves specifying number of edges in each group
            Example: 3 5 1
            The second involves specifying total number and distribution
            Example: 10 0.5
            distribution of last value is automatically calculated by 1 - f1 - f2 ...
            If the group cannot support the edges, error is raised
            If no argument is specified, program will attempt to add around 30% more edges to each group or the max it can have
            """,
            default=-1)
    parser.add_argument('-x', type=int, help='initial vertex')
    parser.add_argument('-y', type=int, help='destination vertex')
    filename = parser.add_mutually_exclusive_group()
    parser.add_argument('-o', type=int, 
            help='specify what number test it should be',
            default='-1')
    return parser

def create_graph(args):
    if len(args.d) > 1 and args.d[1] < 1:
        num_vertices = round(args.d[0])
        ranges = get_ranges_complex(num_vertices, args.d[1:])
    else:
        num_vertices = round(sum(args.d))
        ranges = get_ranges_simple(args.d)
    vertices = shuffle(num_vertices)
    print(vertices)
    print(ranges)
    split_vertices = split(vertices, ranges)
    print(split_vertices)
    return num_vertices, ranges, vertice, split_vertices

def get_ranges_simple(simple_d):
    amounts = [ round(flt) for flt in simple_d ]
    return amounts_to_ranges(amounts)

def get_ranges_complex(num_vertices, distribution):
    amounts = distribution_to_amounts(num_vertices, distribution)
    new_ranges = amounts_to_ranges(amounts) + [num_vertices]
    return new_ranges

def split(vertices, ranges):
    split_vertices = [ vertices[ranges[i]:ranges[i+1]] 
            for i in range(len(ranges) - 1) ]
    return split_vertices

def shuffle(n):
    vertices = list(range(n))
    random.shuffle(vertices)
    return vertices

def amounts_to_ranges(amounts):
    ranges = [0]
    for i in range(len(amounts)):
        ranges.append(ranges[i] + amounts[i])
    return ranges

def distribution_to_amounts(total, distribution):
    return [ round(total * percent) for percent in distribution ]

def main():
    parent_parser = graph_parser()
    simple_parser = argparse.ArgumentParser(parents=[parent_parser])
    create_graph(simple_parser.parse_args())

if __name__ == "__main__":
    main()
