"""
decomposition.py
----------------

Decomposing a TTSP DAG into its decomposition tree.

J. Valdes, R. E. Tarjan, and E. L. Lawler. The recognition of series
parallel digraphs. SIAM Journal on Computing, 11(2):298–313, 1982.

"""

import networkx as nx


def read_dag():
    """Read a DAG from an edgelist file.  All nodes labels must be unique."""
    dag = nx.DiGraph()

    num_edges = input()
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


def parallel_reduce_all(dag, node):
    """Perform as many parallel reductions as possible on edges incident to node."""
    # TODO: for every out-neighbor of node, remove all multi-edges of the
    # form node -> neighbor, and then just add a single one.
    # TODO: for every in-neighbor of node, remove all multi-edges of the
    # form neighbor -> node, and then just add a single one.
    pass


def parallel_reduce(dag, edge1, edge2):
    """Modify the dag so that parallel edges edge1 and edge2 are merged into
    one, which is returned."""
    dag.remove_edge(edge2)
    return edge1


def decompose(dag):
    """Return the decomposition tree of the DAG."""
    # The TTSP recognition algorithm, from the referenced source.

    # We maintain a list of vertices that initially includes all vertices
    # except the source and the sink.
    source = get_source(dag)
    sink = get_sink(dag)
    to_visit = set(dag.nodes()).difference(source, sink)

    # The algorithm proceeds by removing any vertex v from this list and
    # performing as many parallel reductions on the edges incident to
    # (from) it as it is possible.
    while to_visit:
        node = to_visit.pop()
        parallel_reduce_all(dag, node) # modifies dag!

        # Now we have either 1. the vertex has a single entering edge and a
        # single exiting edge, or 2. discovering that the vertex still has
        # at least two distinct in-neighbors or two distinct out-neighbors.
        # In the first alternative, the vertex is removed by a series reduction
        # and the two vertices adjacent to it added to the unsatisfied list if
        # they are not there already.
        if dag.indegree()[node] == 1 and dag.outgoing()[node] == 1:
            to_visit.add(get_parent(dag, node))
            to_visit.add(get_child(dag, node))
            series_reduce(dag, node) # modifies dag!

        else:
            # We've found an invalid node.  This is not a TTSP.
            return

    # This process is repeated until the unsatisfied list becomes empty, at
    # which point the same process is applied to the source and the sink
    # (in order to eliminate any multiple edges between them) before
    # stopping.
    parallel_reduce_all(dag, source) # modifies dag!

    # The following line is not necessary as at this point there are no
    # more nodes other than source and sink, and all edges must be parallel
    # between them.
    # parallel_reduce_all(dag, sink)

    # The unsatisfied list becomes empty, either because all vertices
    # (except source and sink) have been deleted by series reductions or
    # because every remaining vertex has two distinct in-neighbors or two
    # distinct out-neighbors. In the first case the DAG is TTSP; in the
    # second it is not.
    return dag


def main():
    """Read a DAG from stdin, and decompose it if possible."""
    dag = read_dag()
    return decompose(dag)


if __name__ == '__main__':
    print(main())
