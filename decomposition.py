"""
decomposition.py
----------------

Decomposing a TTSP DAG into its decomposition tree.

J. Valdes, R. E. Tarjan, and E. L. Lawler. The recognition of series
parallel digraphs. SIAM Journal on Computing, 11(2):298–313, 1982.

"""

import json
from itertools import groupby
import networkx as nx
from networkx.readwrite import json_graph


class DAG(nx.MultiDiGraph):
    """Two Terminal Series Parallel Directed Acyclic Graph."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    def read_dag():
        """Read a DAG from an edgelist file.  All nodes labels must be unique."""
        dag = DAG()

        num_edges = int(input())
        for _ in range(num_edges):
            source, target = input().split(' ')
            dag.add_edge(source, target)

        return dag

    def get_source(self):
        """Return the source of the DAG."""
        indegree_zero = [n for n in self.nodes() if self.in_degree(n) == 0]
        assert len(indegree_zero) == 1, 'More than one source.'
        return indegree_zero[0]

    def get_sink(self):
        """Return the sink of the DAG."""
        outdegree_zero = [n for n in self.nodes() if self.out_degree(n) == 0]
        assert len(outdegree_zero) == 1, 'More than one sink.'
        return outdegree_zero[0]

    def get_sole_parent(self, node):
        """Return the parent of node, given that it only has one predecessor."""
        in_edges = self.in_edges(node)
        assert len(in_edges) == 1
        return in_edges[0][0]

    def get_sole_child(self, node):
        """Return the child of node, given that it only has one successor."""
        out_edges = self.out_edges(node)
        assert len(out_edges) == 1
        return out_edges[0][1]

    def edge_repetitions(self, node):
        """Each edge incident to node along with a list of its replicas.

        Return: a list of the form [(edge1, [e11, e12, ...]), ...], where
        edgei is incident to node, and eij is a triplet of (node1, node2,
        key), where either node1 or node2 is equal to node, and key is the
        unique edge identifier.

        """
        # When called with keys=True, these methods return a list of tuples
        # of the form (src, tgt, key), representing an edge from src to
        # tgt, with unique identifier key.  Since in NetworkX Graph classes
        # the edges are stored in a dictionary, we need the key to access
        # and delete them correctly.  If we just did dag.remove_edge(src,
        # tgt), we could be removing an edge that we still have yet to
        # analyze, we must call dag.remove_edge(src, tgt, key) instead.
        # This is only relevant if there are multiedges between src and
        # tgt.
        all_edges = self.out_edges(node, keys=True) + self.in_edges(node, keys=True)
        grouped_edges = groupby(all_edges, key=lambda e: (e[0], e[1]))
        return [(edge, list(repetitions)) for edge, repetitions
                in grouped_edges]


class DecompositionTree(nx.DiGraph):
    """DecompositionTree is an nx.Graph with methods for adding P-nodes and S-nodes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root = None

    def _new_label(self, name):
        """Return a string based on label for valid use as a node label.

        Use to avoid repeated node labels.

        """
        if name not in self.nodes():
            return name

        label_fmt = '{}-{}'
        count = 1
        label = label_fmt.format(name, count)

        while label in self.nodes():
            count += 1
            label = label_fmt.format(name, count)

        return label

    def _new_leaf_node(self, source, target):
        """Make new leaf node representing a link between source and target in the original DAG."""
        label = self._new_label('({}, {})'.format(source, target))
        self.add_node(label)
        return label

    def _new_pnode(self, node1, node2):
        """Merge node1, node2 with a P-node."""
        label = self._new_label('P')
        self.add_node(label)
        self.root = label
        self.add_edge(label, node1)
        self.add_edge(label, node2)

        return label

    def _new_snode(self, node1, node2):
        """Merge node1, node2 with an S-node."""
        label = self._new_label('S')
        self.add_node(label)
        self.root = label
        self.add_edge(label, node1)
        self.add_edge(label, node2)

        return label

    def add_pnode(self, source, target, label1=None, label2=None):
        """Merge two parallel nodes between source and target.

        label1 and label2 are the labels of the two edges to be merged that
        were created by a previous call to add_pnode() or add_snode().
        They point to the nodes in this decomposition tree that represent
        the previous merge of two edges.

        """
        # If one of the edges to be merged didn't have label, it means it's
        # one of the original edges of the DAG, and we have to create a
        # leaf node for it.
        node1 = label1 or self._new_leaf_node(source, target)
        node2 = label2 or self._new_leaf_node(source, target)

        return self._new_pnode(node1, node2)

    def add_snode(self, parent, node, child, label1=None, label2=None):
        """Merge two edges in series of the form (parent, node), and (node, child).

        label1 and label2 are the labels of the two edges to be merged that
        were created by a previous call to add_pnode() or add_snode().
        They point to the nodes in this decomposition tree that represent
        the previous merge of two edges.

        """
        node1 = label1 or self._new_leaf_node(parent, node)
        node2 = label2 or self._new_leaf_node(node, child)

        return self._new_snode(node1, node2)

    def parallel_reduce(self, dag, node):
        """Perform all possible parallel reductions on edges incident to node.  Add
        the reduced nodes to the decomposition tree.

        """
        # For every neighbor of node, remove all repeated multi-edges of
        # the form node -> neighbor or neighbor -> node, and just leave a
        # single one.
        edge_repetitions = dag.edge_repetitions(node)

        # At each iteration, we merge two replicated edges into one.  This
        # new edge will carry a 'decomposition_node' label, pointing to the
        # node in the decomposition tree that stands for the merge.  If the
        # edges we are merging already have 'decomposition_node' labels, we
        # must merge the node pointed to by the labels.  Otherwise, we must
        # create a new node.  After each merge, we recompute all edges.
        while any(len(reps) > 1 for edge, reps in edge_repetitions):
            multi_edges = ((e, reps) for e, reps in edge_repetitions
                           if len(reps) > 1)

            try:
                multi_edge, repetitions = next(multi_edges)
                source, target = multi_edge
                key1 = repetitions[0][-1]
                key2 = repetitions[1][-1]
                label1 = dag.edge[source][target][key1].get('decomposition_node')
                label2 = dag.edge[source][target][key2].get('decomposition_node')

                dag.remove_edge(source, target, key1)
                dag.remove_edge(source, target, key2)

                # print('P-reducing {}-{}, ({}, {})'.format(source, target,
                #                                           label1, label2))

                pnode = self.add_pnode(source, target, label1, label2)
                dag.add_edge(source, target, decomposition_node=pnode)

            except StopIteration:
                break

            edge_repetitions = dag.edge_repetitions(node)

    def series_reduce(self, dag, node, parent=None, child=None):
        """Reduce a node that lies between just one parent and just one child.  Add
        the reduced nodes to the decomposiiton tree.

        """
        if parent is None:
            parent = dag.get_sole_parent(node)
        if child is None:
            child = dag.get_sole_child(node)

        # print('S-reducing {}-{}-{}'.format(parent, node, child))

        label1 = dag.edge[parent][node][0].get('decomposition_node')
        label2 = dag.edge[node][child][0].get('decomposition_node')

        dag.remove_edge(parent, node)
        dag.remove_edge(node, child)

        snode = self.add_snode(parent, node, child, label1, label2)
        dag.add_edge(parent, child, decomposition_node=snode)

    def decompose(self, dag):
        """Return the decomposition tree of the DAG."""
        # The TTSP recognition algorithm, from the referenced source.

        # We maintain a list of vertices that initially includes all vertices
        # except the source and the sink.
        source = dag.get_source()
        sink = dag.get_sink()
        # print('Source: {}, sink: {}'.format(source, sink))
        to_visit = list(set(dag.nodes()).difference({source, sink}))
        # to_visit = list(set(dag.neighbors(source)).difference(sink))
        # print('to visit: {}'.format(to_visit))

        # The algorithm proceeds by removing any vertex v from this list and
        # performing as many parallel reductions on the edges incident to
        # (from) it as it is possible.
        while to_visit:
            # print('to visit: {}'.format(to_visit))
            node = to_visit.pop()
            # print(node)
            self.parallel_reduce(dag, node)  # modifies dag!

            # Now we have either 1. the vertex has a single entering edge and a
            # single exiting edge, or 2. the vertex still has at least two
            # distinct in-neighbors or two distinct out-neighbors.  In the
            # first alternative, the vertex is removed by a series reduction
            # and the two vertices adjacent to it added to the unsatisfied list
            # if they are not there already.
            if dag.in_degree()[node] == 1 and dag.out_degree()[node] == 1:
                parent = dag.get_sole_parent(node)
                child = dag.get_sole_child(node)
                # print('p: {}, c:{}'.format(parent, child))
                if parent not in [source, sink] and parent not in to_visit:
                    to_visit.append(parent)
                if child not in [source, sink] and child not in to_visit:
                    to_visit.append(child)

                self.series_reduce(dag, node, parent, child)  # modifies dag!

            else:
                # In the second case, we need to visit every other possible
                # node before being certain that we've arrived at an
                # invalid node.
                if to_visit:
                   to_visit = [node] + to_visit
                else:
                    # We've found an invalid node.  This is not a TTSP.
                    print('{} is invalid.'.format(node))
                    return

        # This process is repeated until the unsatisfied list becomes empty, at
        # which point the same process is applied to the source and the sink
        # (in order to eliminate any multiple edges between them) before
        # stopping.
        self.parallel_reduce(dag, source)  # modifies dag!

        # The following line is not necessary as at this point there are no
        # more nodes other than source and sink, and all edges must be parallel
        # between them.
        # parallel_reduce(dag, sink)

        # The unsatisfied list becomes empty, either because all vertices
        # (except source and sink) have been deleted by series reductions or
        # because every remaining vertex has two distinct in-neighbors or two
        # distinct out-neighbors. In the first case the DAG is TTSP; in the
        # second it is not.
        # print('Remaining edges in  dag: {}'.format(dag.edges()))

    def is_pnode(self, node):
        """Return whether or not node is a P-node."""
        return node.startswith('P')

    def merge_pnodes(self):
        """Collapse each P-node into one."""
        self._merge_pnodes_from(self.root)

    def _merge_pnodes_from(self, node, parent=None):
        """Traverse in post-order and merge all P-nodes starting from node."""
        children = self.successors(node)

        if not children:
            return

        for child in children:
            self._merge_pnodes_from(child, node)

        if self.is_pnode(node):
            for child_pnode in (c for c in children if self.is_pnode(c)):
                grandchildren = self.successors(child_pnode)

                self.remove_edges_from((child_pnode, gc) for gc in grandchildren)
                self.add_edges_from((node, gc) for gc in grandchildren)

                self.remove_edge(node, child_pnode)
                self.remove_node(child_pnode)


def main():
    """Read a DAG from stdin, and decompose it if possible."""
    dag = DAG.read_dag()

    jsondata = json_graph.node_link_data(dag)
    # with open('graph.json', 'w') as outfile:
    #     json.dump(jsondata, outfile, indent=4)

    with open('public/graph.json', 'w') as outfile:
        for link in jsondata['links']:
            link['source'] = jsondata['nodes'][link['source']]['id']
            link['target'] = jsondata['nodes'][link['target']]['id']
        json.dump(jsondata, outfile, indent=4)

    tree = DecompositionTree()
    tree.decompose(dag)
    tree.merge_pnodes()

    jsondata = json_graph.node_link_data(tree)
    jsondata['root'] = tree.root
    with open('public/tree.json', 'w') as outfile:
        json.dump(jsondata, outfile, indent=4)


if __name__ == '__main__':
    main()
