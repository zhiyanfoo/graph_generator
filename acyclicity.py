#Uses python3

import sys

def acyclic(adj):
    visited_once =  [ False ] * len(adj)
    visited_twice = visited_once[:]
    i = 0
    order_num = 0
    for i in range(len(adj)):
        if visited_once[i]:
            continue
        has_cycle = search(
                i, adj, visited_once, visited_twice)
        if has_cycle:
            return True
    return False

def search(start, adj, visited_once, visited_twice):
    visited_once[start] = True
    for vertex in adj[start]:
        if not visited_once[vertex]:
            has_cycle = search(
                    vertex, adj, visited_once, visited_twice)
            if has_cycle:
                return True
        elif visited_once[vertex] and not visited_twice[vertex]:
            return True
    visited_twice[start] = True
    return False

if __name__ == '__main__':
    input = sys.stdin.read()
    data = list(map(int, input.split()))
    n, m = data[0:2]
    data = data[2:]
    edges = list(zip(data[0:(2 * m):2], data[1:(2 * m):2]))
    adj = [[] for _ in range(n)]
    for (a, b) in edges:
        adj[a - 1].append(b - 1)
    print(int(acyclic(adj)))
