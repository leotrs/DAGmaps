"""
synthetic_ttsp.py
-----------------

Generate a random TTSP.

"""

import random


def create_singleton(start_node=0, num_operations=4):
    """
    create singleton

    returns:
    a tuple, first element is a singleton, which is a list of edges and
    the second element is a tuple(soure node, sink node)

    """
    edges = list()
    start_edge = (start_node, start_node+1)
    edges.append(start_edge)
    source = edges[0][0]
    #print source
    target = edges[-1][1]
    #print target
    for _ in range(num_operations):
        if random.random() < 0.5:
            edges.append((source, target))
        else:
            edges.append((target, target + 1))
            target = target + 1
    return edges, (source, target)


def replace_nodes_in_edgelist(edgelist, target_node, replaced_node):
    """
    Takes an edgelist and replace all occurences of a node by another node

    Returns
    -------
    The modified edgelist

    """
    first_elements, second_elements = [list(l) for l in zip(*edgelist)]
    for idx, item in enumerate(first_elements):
        if item == target_node:
            first_elements[idx] = replaced_node

    for idx, item in enumerate(second_elements):
        if item == target_node:
            second_elements[idx] = replaced_node

    return list(zip(first_elements, second_elements))


def merge_series(singleton1, singleton2):
    """
    Takes two singleton and merge them by replacing the second
    singleton's source by first singleton's sink node.

    Returns
    -------
    A merged TTSP and its source and sink node

    """
    singleton1_tgt = singleton1[1][1]
    singleton2_src = singleton2[1][0]
    merged_edges = singleton1[0] + replace_nodes_in_edgelist(singleton2[0],
                                                             singleton2_src,
                                                             singleton1_tgt)
    return merged_edges, (singleton1[1][0], singleton2[1][1])


def merge_parallel(singleton1, singleton2):
    """
    takes two singleton and merge them by replacing the second
    singleton's source by first singleton's source and second
    singleton's sink by first singleton's sink

    Returns
    -------
    A merged TTSP and its source and sink node
    """
    singleton1_src = singleton1[1][0]
    singleton1_tgt = singleton1[1][1]

    singleton2_src = singleton2[1][0]
    singleton2_tgt = singleton2[1][1]

    new_edges = replace_nodes_in_edgelist(singleton2[0], singleton2_src, singleton1_src)
    new_edges = replace_nodes_in_edgelist(new_edges, singleton2_tgt, singleton1_tgt)

    merged_edges = singleton1[0] + new_edges
    return merged_edges, (singleton1_src, singleton1_tgt)


def create_synthetic_ttsp(n_merge=3):
    """
    it randomly merges (series or parallel) the randomly created
    singletons at each n_merge step

    returns:
    A tuple, first element is the edgelist of a TTSP and the second
    element is a tuple (source node, sink node)
    """
    source = 0
    current_singleton = create_singleton(start_node=source)

    sink = current_singleton[1][1]
    max_node = sink

    if n_merge > 1:
        for _ in range(n_merge - 1):
            if random.random() < 0.5:
                new_singleton = create_singleton(start_node=max_node + 1)
                max_node = new_singleton[1][1] - 1
                current_singleton = merge_parallel(current_singleton, new_singleton)
                source = current_singleton[1][0]
                sink = current_singleton[1][1]

            else:
                new_singleton = create_singleton(start_node=max_node + 1)
                max_node = new_singleton[1][1]
                current_singleton = merge_series(current_singleton, new_singleton)
                source = current_singleton[1][0]
                sink = current_singleton[1][1]

    return current_singleton


def main():
    """Run stuff!"""
    synthetic_ttsp = create_synthetic_ttsp(n_merge=4)
    filename = "synthetic_ttsp.txt"
    with open(filename, 'w') as file:
        file.write(str(len(synthetic_ttsp[0])))
        for edge in synthetic_ttsp[0]:
            file.write("\n")
            # print(edge)
            file.write(' '.join([str(edge[0]), str(edge[1])]))

if __name__ == '__main__':
    main()
