"""
galls.py
--------

Algorithm that decides whether a graph has galls.

This implements Algorithm 1 http://bit.ly/2dPSOCP.

"""


###############################################################################
###                              PRELIMINARIES                              ###
###############################################################################


### DEFINITIONS ###

# Excerpt from the article with our working definition of galls.

#     Reticulation nodes have more than one ancestors.  It is easy to
#     realize that a phylogenetic tree is a phylogenetic network without
#     reticulation nodes.

#     Reticulation cycles are defined as follows.  Since there is only one
#     root node in every rooted phylogenetic network, in the corresponding
#     undirected graph every reticulation node belongs to a cycle.  This
#     cycle, in the directed graph, is called reticulation cycle.

#     A gall is a reticulation cycle in a phylogenetic network that shares
#     no nodes with any other reticulation cycle.  It consists of a
#     beginning node g0, two chains (the left and the right one) and a
#     reticulation node gk, as shown in Figure 1.

#     The beginning node g0 is on level 1 of this subgraph, the
#     reticulation node on level k + 1, and the chain nodes are on the i-th
#     levels, i ∈ {2, ..., k}.  Every level i may contain either one or two
#     chain nodes.  Every node gi, i ∈ {0, ..., k}, of the gall may have a
#     subtree ti+1 as a descendant.  These subtrees do not have more
#     connections with this gall, because in that case a reticulation cycle
#     would be created, which would share a node with the gall, and this is
#     not allowed according to the definition of a gall.


### PROPOSED ALGORITHM ###

# This is the authors' description of the algorithm that determines whether
# a graph contains a gall.

#   Algorithm 1: Locating the galls of a graph
#   Input:       A Graph G.
#   Output:      The set of galls and the characterization of G as a galled
#                tree or a galled network, or null if the graph is neither.

#     1.  Perform a simple graph traversal in order to locate the
#         reticulation nodes.
#     2.  If a node with more than two incoming edges is found, then
#         return null.
#     3.  For every reticulation node find its two parents. Each of these
#         parents belongs to a chain of the gall.
#     4.  For every parent find its parent and assign it to the same
#         chain. (At each step discover one node from each chain.)
#     5.  Continue this process until a node is found which already
#         belongs to the other chain. This is the beginning node of the
#         gall. If no such node is found, return null.
#     6.  After locating all the galls, test the galled tree and the
#         galled network condition.
#     7.  If the galled tree condition holds then characterize the graph
#         as a "galled tree".
#     8.  Else if the galled network condition holds then characterize
#         the graph as a "galled network".
#     9.  Else return null.
#     10. Return the located galls.

# The referenced "galled tree condition" and "galled network condition" are
# found in the Preliminaries section:

# Galled tree condition: A galled tree is a phylogenetic network whose
# reticulation cycles are galls. (Refs: [5, 23])

# Galled network condition: A galled network is a rooted phylogenetic
# network in which every reticulation cycle shares no reticulation nodes
# with any other reticulation cycle [9].  In contrast to galled trees,
# galled networks allow the reticulation cycles to share nodes, as long as
# they are not reticulation nodes. These reticulation cycles are called
# loose galls.


### COMMENTS ###

# 1. Step 2: Are there any other early termination conditions other than step 2?

# 2. Step 5 has to be aware of the fact that there is a root node.

# 3. Step 5 must find a gall if the network is rooted.

# 4. Step 5 "If no such node is found, return null" should say "If no such
#    node is found for any of the reticulation nodes, return null".

# 5. Steps 6-9: Can we check for both conditions at the same time? Maybe
#    when traversing the tree during step 1, or during step 5.

# 6. Keep in mind that every reticulation cycle corresponds to exactly one gall.

# 7. Use a hash table for storing chain nodes.

# 8. Excerpt: "This process will discover all the galls of the graph, since
#    every reticulation node corresponds to exactly one gall. In addition,
#    every chain node will be visited a constant number of times if we use a
#    hash table to store the chain nodes. Also, the property that every gall
#    has exactly one reticulation node guarantees that this algorithm will
#    neither leave any gall undiscovered, nor claim to discover a gall that
#    does not exist. Thus, it is straightforward to show that Algorithm 1 runs
#    in O(n + m) time."


###############################################################################
###                                  TASKS                                  ###
###############################################################################

# 1. Implement the algorithm.
# 2. Write tests.
# 3. Analyze complexity. (Validate comment 8.)
# 4. Think of efficient ways of checking for both conditions at the same time.
# 5. Optimize set intersection code (when checking chain intersection).


###############################################################################
###                                  CODE                                   ###
###############################################################################

import itertools
import networkx as nx
from networkx.drawing.nx_agraph import graphviz_layout
import matplotlib.pyplot as plt


def get_parents(graph, node):
    """Return a list with all parents of the node."""
    return list(graph.pred[node].keys())


def find_reticulation_nodes(graph):
    """Locate the reticulation nodes.  If there is a node with more than two
    ancestors, return None.

    <graph> a NetworkX DiGraph

    <returns> a dictionary with elements of the form `node: (parent1,
    parent2)`.  Each key in the dictionary is a reticulation node in
    <graph> and its correspoinding tuple contains both its parents.

    """
    # 2.  If a node with more than two incoming edges is found, then
    #     return null.
    degrees = graph.in_degree()
    if any(deg > 2 for deg in degrees.values()):
        return

    # 1.  Perform a simple graph traversal in order to locate the
    #     reticulation nodes.
    # 3.  For every reticulation node find its two parents. Each of these
    #     parents belongs to a chain of the gall.
    return {node: get_parents(graph, node) for node in graph
            if degrees[node] == 2}


def is_galled_tree(graph, cycles):
    """Return if the graph and its galls hold the galled tree condition."""
    # A galled tree is a phylogenetic network whose reticulation cycles are
    # galls.
    node_sets = [{reticulation, *chains[0], *chains[1]}
                 for reticulation, chains in cycles.items()]

    for set1, set2 in itertools.combinations(node_sets, 2):
        if set1 & set2:
            return False

    return True


def is_galled_network(graph, cycles):
    """Retuen if the graph and its galls hold the galled network condition."""
    # A galled network is a rooted phylogenetic network in which every
    # reticulation cycle shares no reticulation nodes with any other
    # reticulation cycle.  In contrast to galled trees, galled networks
    # allow the reticulation cycles to share nodes, as long as they are not
    # reticulation nodes. These reticulation cycles are called loose galls.
    all_reticulations = cycles.values()
    uniques = set(all_reticulations)

    return len(all_reticulations) == len(uniques)


def find_galls(graph):
    """Find all the galls in the graph.

    <graph> a NetworkX DiGraph

    <returns> a list of galls in <graph>, and a boolean value.  The boolean
    is True if <graph> is a galled tree, and False if it's a galled
    network.  If there are no galls, return None.

    """
    # Steps 1, 2, 3
    reticulation_nodes = find_reticulation_nodes(graph)
    if reticulation_nodes is None:
        return

    cycles = {}
    # 3.  For every reticulation node find its two parents. Each of these
    #     parents belongs to a chain of the gall.
    for reticulation, parents in reticulation_nodes.items():

        # 4.  For every parent find its parent and assign it to the same
        #     chain. (At each step discover one node from each chain.)
        left_chain = {parents[0]}
        right_chain = {parents[1]}

        # 5.  Continue this process until a node is found which already
        #     belongs to the other chain. This is the beginning node of the
        #     gall. If no such node is found, return null.
        current_left = parents[0]
        current_right = parents[1]
        while not left_chain.intersection(right_chain):
            ancestors = get_parents(graph, current_left)
            assert len(ancestors) == 1, \
                "Found another reticulation node inside left chain."
            current_left = ancestors[0]
            left_chain.add(ancestors[0])

            ancestors = get_parents(graph, current_right)
            assert len(ancestors) == 1, \
                "Found another reticulation node inside right chain."
            current_right = ancestors[0]
            right_chain.add(ancestors[0])

        cycles[reticulation] = (left_chain, right_chain)

    # 6.  After locating all the galls, test the galled tree and the
    #     galled network condition.
    # 7.  If the galled tree condition holds then characterize the graph
    #     as a "galled tree".
    # 8.  Else if the galled network condition holds then characterize
    #     the graph as a "galled network".
    # 9.  Else return null.
    # 10. Return the located galls.
    if is_galled_tree(graph, cycles):
        return cycles, True

    elif is_galled_network(graph, cycles):
        return cycles, False

    else:
        return


def read_graph(filename):
    """Read an edgelist file and return a nx.DiGraph."""
    return nx.read_edgelist(filename, create_using=nx.DiGraph(), nodetype=str)


if __name__ == '__main__':
    # graph = read_graph('graph.edgelist')
    # pos = graphviz_layout(graph, prog='dot')
    # nx.draw(graph, pos, with_labels=True, arrows=True)
    # plt.show()

    print(find_galls(read_graph('graph.edgelist')))
