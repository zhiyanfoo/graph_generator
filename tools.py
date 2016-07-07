import os
import argparse
import textwrap
import random
from itertools import chain

def graph_parser(parser):
    parser.add_argument('-d', 
            help=textwrap.dedent("""
            There are two methods of specifiying groups 
            The simpler one involves specifying number of vertices in each group
            Example: 10 20 10 
            The second involves specifying total number and distribution
            Example: 40 0.25 0.5
            This produces the same graph
            distribution of last value is automatically calculated by 1 - f1 - f2 ...
            """),
            nargs='*',
            type=float,
            default=[10])
    parser.add_argument('-e',
            help=textwrap.dedent(
            """
            There are two methods of specifiying the 
            additional edges to add to each group
            The simpler one involves specifying number of edges in each group
            Example: 2 4 14 
            This adds 2 edges to the first group 4 to the second 
            and 14 to the third
            The second involves specifying total number and distribution
            This examples does the same thing as the first
            Example: 20 0.1 0.2
            distribution of last value is automatically calculated by 1 - f1 - f2 ...

            """),
            nargs='*',
            type=float,
            default=[-1])
    parser.add_argument('-o', type=int, 
            help='specify what number test it should be',
            default='-1')

def create_graph(args):
    if len(args.d) > 1 and args.d[1] < 1:
        num_vertices = round(args.d[0])
        ranges = get_ranges_complex(num_vertices, args.d[1:])
    else:
        num_vertices = round(sum(args.d))
        ranges = get_ranges_simple(args.d)
    vertices = shuffle(num_vertices)
    # print(vertices)
    # print(ranges)
    split_vertices = split(vertices, ranges)
    # print(split_vertices)
    if abs(args.e[0] - -1) < 0.00001:
        additional_edges = get_porportionate_edges(split_vertices)
    elif len(args.e) != len(split_vertices):
        raise ValueError(
                "length of additional edges list not equal to number of groups")
    elif len(args.e) > 1 and sum(args.e[1:]) < 1:
        num_additional_edges = args.e[0]
        edges_distribution = args.e[1:]
        additional_edges = get_edges_complex(
                num_additional_edges, edges_distribution)
    else:
        additional_edges = [ round(edges) for edges in args.e ]
    groups_can_support_edges(split_vertices, additional_edges)
    return num_vertices, ranges, vertices, split_vertices, additional_edges

def get_ranges_simple(simple_d):
    amounts = [ round(flt) for flt in simple_d ]
    return amounts_to_ranges(amounts)

def get_ranges_complex(num_vertices, distribution):
    amounts = distribution_to_amounts(num_vertices, distribution)
    new_ranges = amounts_to_ranges(amounts) + [num_vertices]
    return new_ranges

def amounts_to_ranges(amounts):
    ranges = [0]
    for i in range(len(amounts)):
        ranges.append(ranges[i] + amounts[i])
    return ranges

def distribution_to_amounts(total, distribution):
    return [ round(total * percent) for percent in distribution ]

def get_edges_complex(num_additional_edges, edges_distribution):
    additional_edges = distribution_to_amounts(
            num_additional_edges, edges_distribution)
    additional_edges.append(round(num_additional_edges - sum(additional_edges)))
    return additional_edges

def get_porportionate_edges(split_vertices):
    porportional_edges_per_group = [ 
            round(0.3 * len(vertices)) for vertices in split_vertices ]
    max_edges = [ max_vertices(len(vertices))
            for vertices in split_vertices ]
    additional_edges = [ porportional_edges_per_group[i] 
            if porportional_edges_per_group[i] < max_edges[i]
            else max_edges[i]
            for i in range(len(porportional_edges_per_group)) ]
    # print(additional_edges)
    return additional_edges

def complete_graph(n):
    return n*(n-1)/2

def max_vertices(n):
    e = complete_graph(n)
    return e - (n-1) if e != 0 else 0

def groups_can_support_edges(split_vertices, additional_edges):
    # print("additional_edges : ", additional_edges)
    max_edges = [ max_vertices(len(vertices))
            for vertices in split_vertices ]
    for i in range(len(split_vertices)):
        if additional_edges[i] > max_edges[i]:
            raise ValueError(
                    "too many edges at group {0}. {1} edges".format(i, additional_edges[i]))

### END OF GRAPH PARSER


def split(vertices, ranges):
    split_vertices = [ vertices[ranges[i]:ranges[i+1]] 
            for i in range(len(ranges) - 1) ]
    return split_vertices

def shuffle(n):
    vertices = list(range(n))
    random.shuffle(vertices)
    return vertices

def link(split_vertices, linker):
    edges = [ linker(group) for group in split_vertices ]
    return edges


### TO STRING METHODS

def edges_to_str(edges):
    """note that the specification used by the course requires vertices to start from 1, so everything is added by one"""
    edges_flat = list(chain(*edges))
    random.shuffle(edges_flat)
    # print(len(edges_flat))
    edges_str= "\n".join([ " ".join(str(x+1) for x in item) for item in edges_flat ])
    # print("edges_str")
    # print(edges_str)
    return edges_str

def split_vertices_to_str(split_vertices):
    """note that the specification used by the course requires vertices to start from 1, so everything is added by one"""
    # print(split_vertices)
    split_vertices_str = "\n".join([ " ".join(str(x+1) for x in vertices) 
        for vertices in split_vertices ]) + "\n"
    # print(split_vertices_str)
    return split_vertices_str

def first_line(num_vertices, edges):
    # print(chain(*edges))
    start = "{0} {1}\n".format(num_vertices, len(list(chain(*edges))))
    return start

def last_line(coordinates):
    end = "\n{0} {1}".format(*coordinates)
    return end

### FILE METHODS
def str_to_file(string, dir_path, name):
    with open(os.path.join(dir_path, name), 'w') as outputFile:
        outputFile.write(string)

def write_in_and_group(in_str, split_vertices_str, file_dir, o, name_template):
    if o == -1:
        i = 1
        while True:
            in_name = name_template.format(i) + ".in"
            if in_name in os.listdir(file_dir):
                i += 1
            else:
                break
    else:
        i = o
        in_name = name_template.format(i) + ".in"
    in_str += "\n"
    str_to_file(in_str, file_dir, in_name)
    str_to_file(split_vertices_str, file_dir, name_template.format(i) + ".group")
