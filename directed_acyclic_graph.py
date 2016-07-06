import os
import sys

import argparse
import random
import textwrap

from itertools import chain

file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, file_dir)

from tools import graph_parser, create_graph, link, edges_to_str, split_vertices_to_str, first_line, last_line, write_in_and_group

from acyclicity import acyclic

random.seed(0)
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

def parser():
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            description=DESCRIPTION,
            epilog=EPILOG)
    parser.add_argument('-d',
            type=int,
            nargs='*',
            default=[6, 2],
            help="""
            specify num of vertices for each totally unconnected island
            Example: -d 4 5
            creates two groups, one with 4 vertices one with 5,
            with no edge between any of these two groups 
            CAVEAT: there might be more unconnected islands 
            than specified by -d but no less
            """
            )

def create_acyclic_graph(islands, num_edges):
    adj = [[] for i in range(sum(islands)) ]
    mapping = list(range(len(adj)))
    mapping = random.shuffle(mapping)
    results = [ create_island(num_vertices, num_edges)
            for num_vertices,  num_edges in zip(islands, num_edges) ]
    for adj in results:
        assert not acyclic(adj)
            

def create_island(num_vertices, num_edges):
    # print(num_edges, num_vertices)
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
        # print(edge)
        # print("start adj")
        # print(adj)
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

def main():
    islands = [112, 3]
    num_edges = [1116, 2]
    create_acyclic_graph(islands,num_edges)

if __name__ == "__main__":
    main()
