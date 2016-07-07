import os
import sys

import argparse
import random
import textwrap

from itertools import chain

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, FILE_DIR)

from tools import edges_to_str, str_to_file

from acyclicity import acyclic

random.seed()

NAME_TEMPLATE = "directed_graph{0}"

DESCRIPTION = """Create a direct acyclic graph"""
EPILOG = """ 
The test set is generated in the following way:

Start with empty adj list for each island
While adj has not enough edges:
    get random edge
    if tried before random edge
        continue
    else
        add edge to adj list
        if adj list has cycle:
            remove edge
    add edge to tried

Once all islands compelete randomize the edge names

Generates two files
    c = 1, 6 [ vertex intial and vertex final ]
    dagx.in 
    x increments if there already exists prior .in
    Also order of edges are shuffled
    Also all values are increased by one as vertices start from 1
    according to course specification
    simple_graph2.in [ if for example simple_graph1.in already exists ]
    8 10 [num vertices, num edges]
    2 3
    2 7
    ...
    4 5
    1 6 [ vertices you want to go from and to specified by -c can be blank]
    """

def create_parser():
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            description=DESCRIPTION,
            epilog=EPILOG)
    parser.add_argument(
            '-d',
            "--distribution",
            type=int,
            nargs='*',
            help=textwrap.dedent("""
            specify num of vertices for each totally unconnected island
            Example: -d 4 5
            creates two groups, one with 4 vertices one with 5,
            with no edge between any of these two groups 
            CAVEAT: there might be more unconnected islands 
            than specified by -d but no less
            """)
            )
    parser.add_argument(
            '-e',
            "--edges",
            type=int,
            nargs='*',
            help=textwrap.dedent("""
            specify num of edges for each totally unconnected island
            Example: -e 9 3 
            NOTICE: Must match num of islands specified by distribution.
            --distribution 7 4 3 --edges 12 3 4 
            MAX and MIN edges based on 'n' num vertices specified
            max : (n-1)(n)/2
            min : n-1
            You might think this implies that each island will be connected
            internally.
            This is NOT the case. There are unlikely circumstances where
            a node is just by itself even though it should be part of an
            island. This might even happen frequently. But probably not.
            """)
            )

    parser.add_argument(
            '-o',
            type=int, 
            help=textwrap.dedent("""
            specify what number in name of file, 
            if none specified increments number until no
            conflicting name in the current directory
            name template : {0}
            """.format(NAME_TEMPLATE)),
            default=-1)
    return parser

def get_input():
    parser = create_parser()
    args = parser.parse_args()
    islands = args.distribution
    if islands is None:
        raise ValueError("Did not specify --distribution")
    num_edges = args.edges
    if num_edges is None:
        raise ValueError("Did not specify --edges")
    o = args.o
    return num_edges, islands, o

def process(islands, num_edges):
    adj_li = create_acyclic_graph(islands, num_edges)
    edges_li = [ adj_to_edges(adj) for adj in adj_li ]
    return edges_li

def create_acyclic_graph(islands, num_edges):
    mapping = list(range(sum(islands)))
    random.shuffle(mapping)
    adj_li= [ create_island(num_vertices, num_edges)
            for num_vertices,  num_edges in zip(islands, num_edges) ]
    new_adj_li = [ [ [ mapping[vertex] for vertex in vertices] 
        for vertices in adj ] 
        for  adj in adj_li ]
    for adj in adj_li:
        assert not acyclic(adj)
    return new_adj_li

def create_island(num_vertices, num_edges):
    check_edge_vertices(num_vertices, num_edges)
    adj = [[] for i in range(num_vertices) ]
    tried = [[] for i in range(num_vertices) ]
    tried_counter = 0
    history = []

    while sum(len(x) for x in adj) != num_edges:
        max_iterations = num_edges * 10000
        if tried_counter > max_iterations:
            errmsg = ("attempted {0} iterations"
                      " but could not find directed graph" 
                      " with {1} vertices and {2} edges" )
            raise ValueError(errmsg.format(
                         max_iterations,
                         num_vertices,
                         num_edges))
        edge = random.sample(range(num_vertices), 2)
        if edge[1] in tried[edge[0]]:
            continue
        adj[edge[0]].append(edge[1])
        if acyclic(adj):
            adj[edge[0]].pop()
        tried[edge[0]].append(edge[1])
        tried_counter += 1
    return adj


def check_edge_vertices(num_vertices, num_edges):
    errmsg = ("number of edges specified : {0},"
            "\n{1} number of edges that {2} vertices {4} : {3}")
    if num_edges > max_edges_DAG(num_vertices):
        raise ValueError(errmsg.format(
            num_edges,
            "max",
            num_vertices, 
            max_edges_DAG(num_vertices),
            "supports"
            ))
    elif num_edges < min_edges_DAG(num_vertices):
        raise ValueError(errmsg.format(
            num_edges,
            "min",
            num_vertices, 
            min_edges_DAG(num_vertices),
            "requires"
            ))
    
def max_edges_DAG(n):
    """n : num of vertices in the DAG"""
    return round((n-1)*(n)/2)

def min_edges_DAG(n):
    return n-1

def adj_to_edges(adj):
    edges = [ [i, vertex] for i in range(len(adj)) for vertex in adj[i] ]
    return edges

def to_output(total_vertices, total_edges, edges_li, o):
    edges_str = edges_to_str(edges_li)
    output_str = "{0} {1}".format(total_vertices, total_edges) + edges_str
    filename, _ = get_filename(o, NAME_TEMPLATE, FILE_DIR)
    str_to_file(output_str, FILE_DIR, filename)

def get_filename(o, name_template, file_dir):
    if o == -1:
        i = 1
        while True:
            filename = name_template.format(i) + ".in"
            if filename in os.listdir(file_dir):
                i += 1
            else:
                break
    else:
        i = o
        filename = name_template.format(i) + ".in"
    return filename, i

def main():
    num_edges, islands, o = get_input()
    edges_li = process(islands, num_edges)
    to_output(sum(num_edges), sum(islands), edges_li, o)

if __name__ == "__main__":
    main()
