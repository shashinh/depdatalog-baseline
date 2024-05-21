# Baseline constraint-based implementation of Section 5 (of Probabilistic Datalog for Conditional Dependencies)

Dependencies:
- gurobi license (obtain one here https://www.gurobi.com/solutions/licensing/)
- ```gurobipy``` python package (obtain here https://pypi.org/project/gurobipy/)

To run:

```python base.py --testdir={/path/to/directory/containing/graph/artifacts} --outdir={/path/to/output/dir}```

For example, running:

```python base.py --testdir=test/ex1/ --outdir=test/ex1/res/```

writes out the results of optimization, the arithmetic DNF for each unknown, and LP files for each optimization objective (which can be used for reproducibility):

```
test/ex1/res/
├── exprs.txt
├── max_obj_p12.lp
├── max_obj_p15.lp
├── max_obj_p16.lp
├── max_obj_p17.lp
├── min_obj_p12.lp
├── min_obj_p15.lp
├── min_obj_p16.lp
├── min_obj_p17.lp
└── results.txt
```



```
test/ex1/res/results.txt
p15     [0.48000000000000004,0.48000000000000004]
p12     [0.6,0.6]
p16     [0.3779999999999999,0.5820000000000001]
p17     [0.42672,0.5328]

test/ex1/res/exprs.txt
p15     1*V1_110 + 1*V1_111
p12     1*V1_010 + 1*V1_011 + 1*V1_110 + 1*V1_111
p16     1*V1_011 + 1*V1_111
p17     1*V0_0*V1_011*V2_1 + 1*V0_0*V1_111*V2_1 + 1*V0_1*V1_011*V2_1 + 1*V2_0*V0_1*V1_110 + 1*V0_1*V1_110*V2_1 + 1*V2_0*V0_1*V1_111 + 1*V2_1*V0_1*V1_111
```

Pass in an optional flag ```--printexprs``` to emit the expressions for each unknown in the console itself.
