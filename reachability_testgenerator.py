import sys
import os

import random
import argparse
import textwrap

random.seed(0)

from itertools import chain

file_dir = os.path.dirname(os.path.abspath(__file__))

def parse_arguments():
    parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description="""Create testset for reachability assignment""",
            epilog=textwrap.dedent("""
            The test set is generated in the following way:
            1. shuffles 'n' vertices 
            Example:
                n = 8
                [0, 1, 2, 3, 4, 5, 6, 7] -> 
                [3, 4, 1, 2, 6, 0, 7, 5]

            2. splits them according to 's' ...
                s[0] = 0.25, s[1] = 0.5 (implicitly s[2] = 0.25)
                a = [3, 4]
                b = [1, 2, 6, 0]
                c = [7, 5]

            3. links them 
                edges[1] = [(3,4)]
                edges[2] = [(1,2), (2,6), (6,0)]
                edges[3] = [(7,5)]

            4. adds k additional edges
                Adds edges in porportion to
                the number of vertices in each group (approximately)
                or max number of edges group can support
                if total edges cannot be supported by group raises error
                k = 2
                edges[2] = [(1,2), (2,6), (6,0), (1,6), (2, 6)]

            5. Generates two files
                x = 1, y = 6
                a(ssignment)1p(roblem1)1t(est)x.in 
                x increments if there already exists prior in
                Also order of edges are shuffled
                All values are increased by one as vertices start from 1
                according to course specification
                a1p1t2.in [ a1p1t1.in already exists so 2]
                8 10 [n, n+k]
                2 3
                4 5
                ...
                7 1
                1 6 [ vertices you want to go from and to]

                test number for .group will match .in, will overwrite 
                a1p1t2.group 
                3, 4
                1, 2, 6, 0
                7, 5

            """)
        )
    parser.add_argument('-n', type=int, help='number of vertices', default=10)
    parser.add_argument('-s', 
            help='number and distribution of groups, for only one group enter 1',
            nargs='*',
            type=float,
            default=[0.5])
    parser.add_argument('-k', type=int, help='number of additional vertices', default=4)
    parser.add_argument('-x', type=int, help='initial vertex', default=1)
    parser.add_argument('-y', help='destination vertex', default='last vertex')
    parser.add_argument('-o', type=int, 
            help='specify what number test it should be',
            default='-1')

    args = parser.parse_args()
    return args

def shuffle(n):
    vertices = list(range(n))
    random.shuffle(vertices)
    return vertices

def split(vertices, s):
    amounts = [ round(len(vertices) * flt) for flt in s ]
    ranges = [amounts[0]]
    for i in range(1,len(amounts)):
        ranges.append(ranges[i-1] + amounts[i])
    new_ranges = [0] + ranges + [len(vertices)]
    split_vertices = [ vertices[new_ranges[i]:new_ranges[i+1]] 
            for i in range(len(new_ranges) - 1) ]
    return split_vertices

def link(split_vertices):
    edges = [ link_group(group) for group in split_vertices ]
    return edges

def link_group(group):
    return [ set([group[i], group[i+1]]) for i in range(len(group) - 1) ]
    
def add_extra_edges(edges, split_vertices, k, s):
    """
    Adds edges in porportion to the number of vertices 
    in each group (approximately)
    or max number of edges group can support
    given by complete_graph - 1
    amends edges, returns none
    """
    porportional_edges_per_group = [ round(k * flt) for flt in s ]
    max_edges = [ complete_graph(len(vertices)) - 1
            for vertices in split_vertices[:-1] ]
    # print("porportional_edges_per_group : ", porportional_edges_per_group)
    # print("max_edges : ", max_edges)
    new_edges_per_group = [ porportional_edges_per_group[i] 
            if porportional_edges_per_group[i] < max_edges[i]
            else max_edges[i]
            for i in range(len(porportional_edges_per_group)) ]
    last_num_edges = k - sum(new_edges_per_group)
    if complete_graph(len(split_vertices[-1])) - 1 < last_num_edges:
        raise ValueError("Graph cannot support {0} number of edges".format(k))
    new_edges_per_group.append(k - sum(new_edges_per_group))
    # print(new_edges_per_group, k)
    for group, vertices, num_edges in zip(
            edges, split_vertices, new_edges_per_group):
        add_edges_to_group(group, vertices, num_edges)
    # print(edges)
    # print(len(edges[0]), len(edges[1]))

def complete_graph(n):
    return n*(n-1)/2

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
        for vertices in split_vertices ])
    # print(split_vertices_str)
    return split_vertices_str

def add_start_end(edges_str, n, k, x, y, s):
    if abs(s[0] - 1) < 0.0000001:
        num_edges = n + k - 1
    else:
        num_edges = n + k - len(s) - 1
    start = "{0} {1}\n".format(n, num_edges)
    end = "\n{0} {1}".format(x, y)
    in_str = start + edges_str + end
    return in_str

def process_s(s):
    sum_s = sum(s) 
    if sum_s >= 1:
        raise ValueError("sum of s args should be less than 1" \
                + '\n' + 'sum of ' + str(s) + ' = ' + str(sum_s))

def process_y(y, n):
    if y == 'last vertex':
        return n
    elif y:
        return str(y)

def str_to_file(string, dir_path, name):
    with open(os.path.join(dir_path, name), 'w') as outputFile:
        outputFile.write(string)

def write_in_and_group(in_str, split_vertices_str, o):
    if o == -1:
        i = 1
        while True:
            in_name = "a1p1t{0}.in".format(i)
            if in_name in os.listdir(file_dir):
                i += 1
            else:
                break
    else:
        i = o
        in_name = "a1p1t{0}.in".format(i)
    str_to_file(in_str, file_dir, in_name)
    str_to_file(split_vertices_str, file_dir, "a1p1t{0}.group".format(i))

def onegroup(args, vertices):
    edges = link_group(vertices)
    add_edges_to_group(edges, vertices, args.k)
    return [edges], [vertices]

def morethanone_group(args, vertices):
    process_s(args.s)
    split_vertices = split(vertices, args.s)
    edges = link(split_vertices)
    add_extra_edges(edges, split_vertices, args.k, args.s)
    return edges, split_vertices

def main():
    args = parse_arguments()
    vertices = shuffle(args.n)
    y = process_y(args.y, args.n)
    if abs(args.s[0] - 1) < 0.0000001:
        edges, split_vertices = onegroup(args, vertices)
    else:
        edges, split_vertices = morethanone_group(args, vertices)
    edges_str = edges_to_str(edges)
    split_vertices_str = split_vertices_to_str(split_vertices)
    in_str = add_start_end(edges_str, args.n, args.k, args.x, y, args.s)
    write_in_and_group(in_str, split_vertices_str, args.o)

if __name__ == "__main__":
    main()
