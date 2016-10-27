"""
decomposition.py
----------------

Decomposing a TTSP DAG into its decomposition tree.

J. Valdes, R. E. Tarjan, and E. L. Lawler. The recognition of series
parallel digraphs. SIAM Journal on Computing, 11(2):298–313, 1982.

"""

import networkx as nx
from itertools import groupby


def read_dag():
    """Read a DAG from an edgelist file.  All nodes labels must be unique."""
    dag = nx.DiGraph()

    num_edges = int(input())
    for _ in range(num_edges):
        source, target = input().split(' ')
        dag.add_edge(source, target)

    return dag


def get_source(dag):
    """Return the source of the DAG."""
    # FIXME: for now, we're forcing the source to have the lowest label
    return min(dag.nodes())


def get_sink(dag):
    """Return the sink of the DAG."""
    # FIXME: for now, we're forcing the sink to have the highest label
    return max(dag.nodes())


def get_sole_parent(dag, node):
    """Return the parent of node, given that it only has one predecessor."""
    in_edges = dag.in_edges(node)
    assert len(in_edges) == 1
    return in_edges[0][0]


def get_sole_child(dag, node):
    """Return the child of node, given that it only has one successor."""
    out_edges = dag.out_edges(node)
    assert len(out_edges) == 1
    return out_edges[0][1]


def parallel_reduce(dag, node):
    """Perform all possible parallel reductions on edges incident to node."""
    # For every neighbor of node, remove all repeated multi-edges of the
    # form node -> neighbor or neighbor -> node, and just leave a single
    # one.

    for edge, replicas in groupby(dag.out_edges(node) + dag.in_edges(node)):
        for replica in replicas:
            dag.remove_edge(*replica)
        dag.add_edge(*edge)


def series_reduce(dag, node, parent=None, child=None):
    """Reduce a node that lies between just one parent and just one child."""
    if parent is None:
        parent = get_sole_parent(dag, node)
    if child  is None:
        child = get_sole_child(dag, node)

    dag.remove_edge(parent, node)
    dag.remove_edge(node, child)
    dag.add_edge(parent, child)


def decompose(dag):
    """Return the decomposition tree of the DAG."""
    # The TTSP recognition algorithm, from the referenced source.

    # We maintain a list of vertices that initially includes all vertices
    # except the source and the sink.
    source = get_source(dag)
    sink = get_sink(dag)
    print('Source: {}, sink: {}'.format(source, sink))
    to_visit = set(dag.nodes()).difference(source, sink)
    print('to visit: {}'.format(to_visit))

    # The algorithm proceeds by removing any vertex v from this list and
    # performing as many parallel reductions on the edges incident to
    # (from) it as it is possible.
    while to_visit:
        node = to_visit.pop()
        parallel_reduce(dag, node) # modifies dag!

        # Now we have either 1. the vertex has a single entering edge and a
        # single exiting edge, or 2. the vertex still has at least two
        # distinct in-neighbors or two distinct out-neighbors.  In the
        # first alternative, the vertex is removed by a series reduction
        # and the two vertices adjacent to it added to the unsatisfied list
        # if they are not there already.
        if dag.in_degree()[node] == 1 and dag.out_degree()[node] == 1:
            parent = get_sole_parent(dag, node)
            child = get_sole_child(dag, node)
            if parent not in [source, sink]:
                to_visit.add(parent)
            if child not in [source, sink]:
                to_visit.add(child)

            series_reduce(dag, node, parent, child) # modifies dag!

        else:
            # We've found an invalid node.  This is not a TTSP.
            print('{} is invalid.'.format(node))
            return

    # This process is repeated until the unsatisfied list becomes empty, at
    # which point the same process is applied to the source and the sink
    # (in order to eliminate any multiple edges between them) before
    # stopping.
    parallel_reduce(dag, source) # modifies dag!

    # The following line is not necessary as at this point there are no
    # more nodes other than source and sink, and all edges must be parallel
    # between them.
    # parallel_reduce(dag, sink)

    # The unsatisfied list becomes empty, either because all vertices
    # (except source and sink) have been deleted by series reductions or
    # because every remaining vertex has two distinct in-neighbors or two
    # distinct out-neighbors. In the first case the DAG is TTSP; in the
    # second it is not.
    print(dag.nodes())
    print(dag.edges())
    return dag


def main():
    """Read a DAG from stdin, and decompose it if possible."""
    return decompose(read_dag())


if __name__ == '__main__':
    print(main())
