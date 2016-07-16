import os
import sys

import argparse
import random
import textwrap

from itertools import chain

FILE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, FILE_DIR)

from tools import str_to_file
from acyclicity import acyclic
from todot import to_dot, create_image

# random.seed(1)

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

Files generated
    c = 1, 6 [ vertex intial and vertex final ]
    dagx.in 
    x increments if there already exists prior .in
    Also order of edges are shuffled
    Also all values are increased by one as vertices start from 1
    according to course specification
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
            island. SEE DISTRIBUTION CAVEAT
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
    parser.add_argument(
            '-s',
            "--show",
            help=textwrap.dedent("""
            If included creates image using graphviz
            """.format(NAME_TEMPLATE)),
            action="store_true"
            )
    parser.add_argument(
            '-c', 
            type=int, 
            help="inital and destination vertex",
            nargs='*'
            )
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
    s = bool(args.show)
    return num_edges, islands, o, s

def process(islands, num_edges):
    adj_list = create_acyclic_graph(islands, num_edges)
    edges_list = adj_to_edges(adj_list)
    return edges_list

def create_acyclic_graph(islands, num_edges):
    adj_lists = [ create_island(num_vertices, num_edges)
            for num_vertices,  num_edges in zip(islands, num_edges) ]
    to_add = [0]
    for adj_list in adj_lists:
        to_add.append(to_add[-1] + len(adj_list))
    if len(adj_lists) > 1:
        new_adj_lists = [ 
                [ [vertex + to_add[i] for vertex in vertices ]
                for vertices in adj_lists[i] ] 
                for i in range(len(adj_lists))]
    else:
        new_adj_lists = adj_lists
    mapping = list(range(sum(islands)))
    random.shuffle(mapping)
    adj_list = [ vertices for adj_list in new_adj_lists for vertices in adj_list ]
    random_adj = [None] * len(adj_list)
    for i in range(len(adj_list)):
        random_adj[mapping[i]] = [ mapping[vertex] for vertex in adj_list[i] ]
    assert not acyclic(random_adj)
    return random_adj

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

def edges_to_str(edges_list):
    random.shuffle(edges_list)
    edges_str= "\n".join([ " ".join(str(x+1) for x in item) 
        for item in edges_list ])
    return edges_str


def to_output(total_vertices, total_edges, edges_list, o, s):
    edges_str = edges_to_str(edges_list)
    output_str = "{0} {1}\n".format(total_vertices, total_edges) + edges_str
    filename, i = get_filename(o, NAME_TEMPLATE, FILE_DIR)
    str_to_file(output_str, FILE_DIR, filename)
    if s:
        image_filename = NAME_TEMPLATE.format(i) + ".png"
        dot_str = to_dot(edges_list, directed=True)
        create_image(dot_str, image_filename)


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
    num_edges, islands, o, s = get_input()
    show = True
    edges_list = process(islands, num_edges)
    to_output(sum(num_edges), sum(islands), edges_list, o, s)

if __name__ == "__main__":
    main()
