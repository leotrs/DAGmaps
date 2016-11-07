# DAGmaps

## Decomposition tree

To compute the decomposition tree of a DAG, run

```
$ python decomposition < dag_data.txt
```

where `dag_data.txt` is a DAG in edgelist format.  For example, you can run
`python decomposition.py < input.txt` on the example DAG on this repository.

This will print the output and also save the necessary files in json format
in the current dir.


## DAGmap

To compute the DAGmap, you need to run a web server on `dagmaps.html`.
This will read the json files generated in the previous step and draw the
DAGmap with d3.js.
