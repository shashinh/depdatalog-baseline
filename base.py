import sys
import os
import gurobipy as gp
from gurobipy import GRB
from defs import *
from util import *
from itertools import product

#just a dirty global context to hold unimportant data
class gob:
    pass

gb = gob()

def main():
    #init a gurobi model
    m = init_model()
    ctx = Context(m)

    read_inputs(ctx)
    build_correlation_classes(ctx)
    build_constraints(ctx)

    build_expressions(ctx)
    build_objectives(ctx)

    #optimize each unknown (output) fact
    print('constraint system built, dispatching to Gurobi..')
    m.update()

    run_optimize(ctx, gb)
    process_results(ctx, gb)

def init_model():
    env = gp.Env(empty=False)
    env.setParam("OutputFlag", 0)
    env.start()
    m = gp.Model("Baseline", env=env)
    m.setParam('NonConvex', 2)
    return m

def read_inputs(ctx: Context):
    read_facts(ctx, gb)
    read_deps(ctx, gb)

if __name__ == "__main__":
    import time
    start_time = time.perf_counter()
    import argparse
    
    parser = argparse.ArgumentParser(description='Solve queries using constraint optimization')
    parser.add_argument('--testdir', metavar='path', required=True, help='directory containing the graph artifacts (edges.txt, facts.txt)')
    parser.add_argument('--outdir', metavar='path', required=True, help='directory to write results to')
    parser.add_argument('--printexprs', nargs='?', default=False, const=True, required=False, help='print arithmetic DNF for each solved query')
    args = parser.parse_args()

    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    setattr(gb, 'args', args)
    main()
    end_time = time.perf_counter()
    print('completed in:' , end_time - start_time, 'seconds (total in Python)')