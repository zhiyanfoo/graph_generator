import os
import sys

import argparse
import random
import textwrap

file_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, file_dir)

random.seed()

from tools import graph_parser, create_graph, link, edges_to_str, split_vertices_to_str, first_line, last_line, write_in_and_group

from todot import to_dot, create_image

def linker(group):
    return [ set([group[i], group[i+1]]) for i in range(len(group) - 1) ]

def add_extra_edges(edges, split_vertices, additional_edges):
    for group, vertices, num_edges in zip(
            edges, split_vertices, additional_edges):
        add_edges_to_group(group, vertices, num_edges)

def add_edges_to_group(group, vertices, num_edges):
    # print(group, vertices, num_edges)
    required_size = len(group) + num_edges
    # print("required_size : ", required_size)
    while len(group) != required_size:
        a = random.choice(vertices)
        b = random.choice(vertices)
        if a == b:
            continue
        new_edge = set([a, b])
        if new_edge not in group:
            group.append(new_edge)

def main():
    name_template = "simple_graph{0}"
    simple_parser = argparse.ArgumentParser(
            formatter_class=argparse.RawTextHelpFormatter,
            description="""Create a simple graph""",
            epilog=textwrap.dedent("""
            The test set is generated in the following way:
            1. shuffles vertices 
            Example:
                num_vertices = 8
                [0, 1, 2, 3, 4, 5, 6, 7] -> 
                [3, 4, 1, 2, 6, 0, 7, 5]

            2. splits them according to 'd' ...
                first method
                d[0] = 2, d[1] = 3, d[2] = 3
                a = [3, 4]
                b = [1, 2, 6]
                c = [7, 5, 0]

                d[0] = 0.25, d[1] = 0.5 (implicitly d[2] = 0.25)
                a = [3, 4]
                b = [1, 2, 6]
                c = [7, 5, 0]

            3. links them 
                edges[0] = [(3,4)]
                edges[1] = [(1,2), (2,6)]
                edges[2] = [(7,5), (5,0)]

            4. adds e additional edges
                first method
                e = 0 1 1
                edges[1] = [(1,2), (2,6), (1,6)]
                edges[2] = [(7,5), (5,0), (7,0)]
                second method
                2 0 0.5 
                edges[1] = [(1,2), (2,6), (1,6)]
                edges[2] = [(7,5), (5,0), (7,0)]

            5. Generates two files
                c = 1, 6 [ vertex intial and vertex final ]
                simple_graphx.in 
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
                test number for .group will match test number for .in
                will overwrite any .group with same number
                simple_graph2.group 
                3, 4
                1, 2, 6
                7, 5, 0
            """)
            )
    graph_parser(simple_parser)
    simple_parser.add_argument(
            '-c', 
            type=int, 
            help="inital and destination vertex",
            nargs='*'
            )
    simple_parser.add_argument(
            '-s',
            "--show",
            help=textwrap.dedent("""
            If included creates image using graphviz
            """.format(name_template)),
            action="store_true"
            )
    args = simple_parser.parse_args()
    num_vertices, ranges, vertices, split_vertices, additional_edges = create_graph(args)
    edges = link(split_vertices, linker)
    add_extra_edges(edges, split_vertices, additional_edges)
    edges_str = edges_to_str(edges)
    in_str = first_line(num_vertices, edges) + edges_str 
    if args.c is not None:
        if len(args.c) != 2:
            raise ValueError(
                    "num -c args is {0}, should be  2".format(len(args.c)))
        in_str += last_line(args.c)
    split_vertices_str = split_vertices_to_str(split_vertices)
    i = write_in_and_group(in_str, split_vertices_str, file_dir, args.o, name_template)
    flat_edges = [ list(edge) for edgesli in edges for edge in edgesli ]
    s = bool(args.show)
    if s:
        image_filename = name_template.format(i) + ".png"
        dot_str = to_dot(flat_edges, directed=False)
        create_image(dot_str, image_filename)



if __name__ == "__main__":
    main()
