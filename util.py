import sys
from typing import Tuple
from gurobipy import Model, GRB, quicksum, Var
from defs import *
from decimal import Decimal

def read_facts(ctx: Context, gob):
    test_dir = getattr(gob, 'args').testdir

    file = open(test_dir + '/facts.txt')
    for line in file.readlines():
        line = line.strip()
        if line:
            toks = line.split(' ')
            if len(toks) != 2 :
                sys.exit('unexpected number of tokens in facts.txt')
            else:
                ctx.facts[toks[0]] = Decimal(toks[1])

    
def read_deps(ctx: Context, gob):
    test_dir = getattr(gob, 'args').testdir

    file = open(test_dir + '/edges.txt')
    for line in file.readlines():
        line = line.strip()
        if line:
            toks = line.split(' ')
            if len(toks) != 3 :
                sys.exit('unexpected number of tokens in edges.txt')
            else:
                #represents the head of a rule
                source_v = toks[0]
                #represents the body of a rule, potentially a list of events
                dest_vs = toks[1].split(';')
                #represents the probability associated with the rule
                cond_prob = Decimal(toks[2])

                if source_v in ctx.facts:
                    # this represents a dependency b/w input facts
                    for d in dest_vs:
                        #sanity check
                        assert d in ctx.facts, f'source {source_v} dep {d} not a fact'

                    #only save valid conditional probs (this comes into play for the side-channel bms)
                    #  which use correlation classes to show that facts are related, without 
                    #  supplying the actual dependency.
                    if(cond_prob != -1):
                        ctx.fact_deps.setdefault(source_v, []).append((dest_vs, cond_prob))

                    # save off an undirected version, for convenence
                    for d in dest_vs:
                        ctx.facts_undirected.setdefault(source_v, []).append(d)
                        ctx.facts_undirected.setdefault(d, []).append(source_v)
                    
                else:
                    # this represents a dependency for an output fact
                    ctx.output_deps.setdefault(source_v, []).append((dest_vs, cond_prob))


def dfs(undirected: dict[str, list[str]], tmp: list[str], f: str, visited: set[str]):
    visited.add(f)
    tmp.append(f)

    if f in undirected:
        for v in undirected[f]:
          if v not in visited:
            tmp = dfs(undirected, tmp, v, visited)  
    return tmp

def fact_connected(ctx: Context) -> list[list[str]]:
    visited = set[str]()
    cc = list[list[str]]()
    for f in ctx.facts:
        if f not in visited:
            tmp = list[str]()
            cc.append(dfs(ctx.facts_undirected, tmp, f, visited))
    
    return cc


def build_correlation_classes(ctx: Context):
    """initializes correlation classes based on input facts"""

    fact_connected_comps = fact_connected(ctx)
    correlation_class_prefix = 'V'
    count = 0
    for cc in fact_connected_comps:
        cl = CorrelationClass(f'{correlation_class_prefix}{count}', cc, ctx.model)
        ctx.correlation_classes.add(cl)
        count += 1

def build_constraints(ctx: Context):
    """adds the three types of constraints described in Fig 6"""
    add_sum_to_one_constraints(ctx)
    add_marginal_prob_constraints(ctx)
    add_dep_constraints(ctx)

    ctx.model.update()
    #sanity
    #ctx.model.write("constraints-only.lp")

#
def add_sum_to_one_constraints(ctx : Context):
    """applies Rule SUMONE in Fig 6"""

    #for each correlation class
    for cl in ctx.correlation_classes:
        #add a constraint that sums all sym vars to 1 (Rule SUMONE in Fig 6)
        ctx.model.addConstr(
            quicksum(sym_var.grb_var for sym_var in cl.sym_vars) == 1,
            f'sumToOne_{cl.get_name()}'
        )

def add_marginal_prob_constraints(ctx : Context):
    """applies Rule INPUTFACT in Fig 6"""

    # for each correlation class
    for cl in ctx.correlation_classes:
        #for each fact in the correlation class
        for f in cl.facts:
            fact_prob = ctx.facts[f]
            fact_index_in_class = cl.get_index_of_fact(f)
            e = get_expression_for_fact(f, cl, ctx)
            marginal_vars = []
            for i, v in e.terms.items():
                assert(len(i) == 1)
                if v == 1:
                    marginal_vars.append(list(i)[0].grb_var)

            #add constraint based on Rule INPUTFACT in Fig 6)
            sum = quicksum(marginal_vars)
            ctx.model.addConstr(sum == float(fact_prob), f'c_{f}')

            #store off a copy of this expression if needed later
            cl.fact_sums[f] = sum
            


def add_dep_constraints(ctx : Context):
    """applies Rule INPUTDEP in Fig 6"""

    #for each correlation class
    for cl in ctx.correlation_classes:
        #for each fact in the correlation class
        for f in cl.facts:
            #only if there are dependencies defined for this fact
            if f in ctx.fact_deps:
                e_f = get_expression_for_fact(f, cl, ctx)

                for (deps, cond_prob) in ctx.fact_deps[f]:
                    first_dep = deps[0]
                    e_dep = get_expression_for_fact(first_dep, cl, ctx)
                    for dep in deps[1:]:
                        e = get_expression_for_fact(dep, cl, ctx)
                        e_dep = e_dep.mul(e)
                    
                    e_joint = e_f.mul(e_dep)

                    #build constraint by the InputDep rule
                    #obtain a GRB sum for the LHS
                    joint_sum = e_joint.to_grb_sum(ctx)
                    #multiply RHS by the conditional probability
                    e_dep = e_dep.multiply_by_const(cond_prob)
                    #obtain a GRB sum for the RHS
                    dep_sum = e_dep.to_grb_sum(ctx)

                    #introduce an aux var, technically not required -- but readability.
                    joint_var = ctx.model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=1)
                    ctx.model.addConstr(joint_var == joint_sum)

                    ctx.model.addConstr(joint_var == dep_sum)


def make_grb_var(m: Model, name: str) -> Var:
    return m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=1, name=name)

def get_expression_for_fact(fact: str, corr_class: CorrelationClass, ctx: Context) -> Expression:
    if fact in ctx.expressions:
        return ctx.expressions[fact]
    else:
        e = Expression()
        e.init_for_fact(fact, corr_class)
        ctx.expressions[fact] = e
        return e

def build_expressions(ctx: Context):
    """recursively build expressions for each unknown fact
    (EXPENSIVE)"""

    #by this point, all facts should have expressions ready, so assert that
    for f in ctx.facts:
        assert(f in ctx.expressions)
    
    for f in ctx.output_deps:
        e = build_expr(f, ctx)
        ctx.expressions[f] = e

def build_expr(event: str, ctx: Context) -> Expression:
    """build expression for a given output fact"""

    if event in ctx.expressions:
        #already built
        return ctx.expressions[event]
    else:
        deps = ctx.output_deps[event]
        tmp = list[Expression]()
        for i, j in deps:
            #for each outgoing edge, initialize e_conj with the 
            #   first predicate in the body of the rule
            e_conj = build_expr(i[0], ctx)
            for d in i[1:]:
                #apply rule EDGE in Fig 4 to obtain E = E1 \otimes E2 \otimes ... \otimes En
                e_conj = e_conj.mul(build_expr(d, ctx))

            #p * E
            tmp.append(e_conj.multiply_by_const(j))
        
        #apply rule NODE in Fig 4 to obtain expression for the Node (i.e. the unknown fact)
        e_disj = tmp[0]
        for e in tmp[1:]:
            e_disj = e_disj.add(e)

        return e_disj



def build_objectives(ctx: Context):
    """build objectives for each unknown fact"""

    for f in ctx.output_deps:
        e = ctx.expressions[f]
        sum = e.to_grb_sum(ctx)

        obj_var = make_grb_var(ctx.model, f'obj_{f}')
        ctx.model.addConstr(obj_var == sum, name = f'c_obj_{f}')

def run_optimize(ctx: Context, gb):
    """for each output fact, set up objective and optimize min/max"""

    m = ctx.model
    results = dict[str, Tuple[Decimal, Decimal]]()
    opt_runtime = 0
    output_dir = getattr(gb, 'args').outdir
    for out in ctx.output_deps:
        obj_name = f'obj_{out}'
        min = max = -1

        print(f'\noptimizing {obj_name}')

        objective = m.getVarByName(obj_name)
        m.setObjective(objective, GRB.MINIMIZE)
        #m.write(f"{output_dir}/LPs/min_{obj_name}.lp")
        m.optimize()
        if m.status == GRB.Status.OPTIMAL:
            min = m.ObjVal
            print(f'\tOptimal min {min}')
            opt_runtime += m.Runtime
        else:
            print(m.Status)

        m.setObjective(objective, GRB.MAXIMIZE)
        #m.write(f'{output_dir}/LPs/max_{obj_name}.lp')
        m.optimize()
        if m.status == GRB.Status.OPTIMAL:
            max = m.ObjVal
            print(f'\tOptimal Max {max}')
            print(f'{m.Runtime} seconds')
            opt_runtime += m.Runtime
        else:
            print(m.Status)
        
        #store away results as a tuple
        results[out] = (min, max)

    ctx.results = results
    
    print(f'total optimization runtime: {opt_runtime} seconds')

def process_results(ctx: Context, gb):
    results = ctx.results
    #build formatted result strings for output
    output_strs = list[str]()
    output_exprs = list[str]()
    for k, v in results.items():
        s = f'{k}\t[{v[0]},{v[1]}]'
        output_strs.append(s)
        output_exprs.append(f'{k}\t{str(ctx.expressions[k])}')
    
    output_dir = getattr(gb, 'args').outdir
    with open(output_dir + '/results.txt', 'w') as f:
        f.write('\n'.join(output_strs))
        f.close()


    with open(output_dir + '/exprs.txt', 'w') as expr_f:
        expr_f.write('\n'.join(output_exprs))
        expr_f.close()


    #emit results to console
    print()
    print_exprs = getattr(gb, 'args').printexprs
    for k, v in results.items():
        if print_exprs:
            print(f'{k} Arith DNF: {ctx.expressions[k]}')
        print(f'{k}\t[{v[0]},{v[1]}]')

    print()
