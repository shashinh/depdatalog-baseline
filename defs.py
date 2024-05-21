from decimal import Decimal
from typing import Tuple
from itertools import product
from gurobipy import Model, GRB, quicksum, LinExpr, Var
import copy

#context class to hold on to everything
class Context:
    def __init__(self, m: Model):
        self.facts = dict[str, Decimal]()
        self.correlation_classes = set['CorrelationClass']()
        self.fact_to_class = dict[str, 'CorrelationClass']()
        self.fact_deps = dict[str, Tuple[list[str], Decimal]]()
        self.facts_undirected = dict[str, list[str]]()
        self.output_deps = dict[str, list[Tuple[list[str], Decimal]]]()
        self.model = m
        self.aux_count = 0
        self.expressions = dict[str, Expression]()
        self.results = dict[str, Tuple[Decimal, Decimal]]()

    def get_correlation_class_for_fact(self, fact: str) -> 'CorrelationClass':
        return self.fact_to_class[fact]


#correlation class, contains all facts that belong in the same connected component (Definition 4)
class CorrelationClass:
    def __init__(self, name: str, facts: list[str], m: Model):
        self.name = name
        self.facts = facts
        self.fact_indices = dict[str, int]()
        self.model = m
        self.sym_vars = self.__gen_sym_vars()
        self.fact_sums = dict[str, LinExpr]()
    
    def get_name(self):
        return self.name
    
    def __gen_sym_vars(self):
        # assign an index to each fact
        i = 0
        for f in self.facts:
            self.fact_indices[f] = i
            i += 1
        
        #create all bit strings of length # of facts
        bit_strings = [''.join(map(str, i)) for i in product(range(2), repeat=len(self.facts))]
        #build symbolic vars for each bit string
        return [SymVar(b, self) for b in bit_strings]


    def __str__(self) -> str:
        return 'correlation class name: ' +\
              self.name + '\n\tsymbolic vars: ' +\
              str(list(map(str, self.sym_vars))) +\
                  '\n\tfacts: ' + str(self.fact_indices)

    def get_index_of_fact(self, fact: str):
        return self.fact_indices[fact]

# corresponds to a joint probability variable, Section 5.1
class SymVar:
    def __init__(self, name: str, corr_class: CorrelationClass):
        self.name = name
        self.corr_class = corr_class
        self.grb_var = self.init_grb_var(self.corr_class.model)
    
    def __str__(self) -> str:
        return self.corr_class.get_name() + '_' + self.name
    
    def init_grb_var(self, m: Model):
        return m.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=1, name=str(self))

# corresponds to an arithmetic DNF, Definition 7
class Expression:
    def __init__(self, terms: dict[frozenset[SymVar], Decimal] = {}):
        #NOTE - an expression c1*V1_001*V2_010 + c2*V1_010*V2_110 is represented as a dict
        #         { {V1_001, V2_010}: c1, 
        #           {V1_010, V2_110}: c2
        #         }
        # where {V1_001, V2_010} is a frozenset containing 2 sym vars
        # why set? because it beats string processing, maintaining them in order,
        #   and keeping track of indices
        # why frozenset? because it is hashable (good old set is not)
        self.terms = terms
        self.corr_classes = set[CorrelationClass]()

    #pretty print yay!
    def __str__(self) -> str:
        l = list[str]()
        for (k, v) in self.terms.items():
            if v != 0:
                sym_vars = [str(i) for i in k]
                s = str(v) + '*' + '*'.join(sym_vars)
                l.append(s)

        return ' + '.join(l)

    def add(self, other: 'Expression') -> 'Expression':
        self_normalized = self.normalize(other)
        other_normalized = other.normalize(self)
        #NOTE - assertion to check normalization
        assert(self_normalized.terms.keys() == other_normalized.terms.keys())

        #NOTE - safe to do since asserted above
        self_plus_other = Expression()
        t = dict[frozenset[SymVar], Decimal]()
        #we can do this safely because:
        #   1. the assertion above ensures the keys are same
        #   2. the key is a set containing all symbolic vars (multiplicands) in the term
        #   3. the value is the constant coefficient that needs to be processed by rule ADD in Fig 5
        for (k,v) in self_normalized.terms.items():
            c1 = v
            c2 = other_normalized.terms[k]

            c = c1 + c2 - c1 * c2
            t[k] = c
        
        self_plus_other.terms = t

        #cleanup, stuff gets very memory intensive
        del(self_normalized)
        del(other_normalized)
        return self_plus_other

    def mul(self, other: 'Expression') -> 'Expression':
        #normalize both operands in the operation
        self_normalized = self.normalize(other)
        other_normalized = other.normalize(self)

        #NOTE - assertion to check normalization
        assert(self_normalized.terms.keys() == other_normalized.terms.keys())

        #NOTE - safe to do since asserted above
        self_times_other = Expression()
        tmp = dict[frozenset[SymVar], Decimal]()
        #we can do this safely because:
        #   1. the assertion above ensures the keys are same
        #   2. the key is a set containing all symbolic vars (multiplicands) in the term
        #   3. the value is the constant coefficient that needs to be processed by rule MUL in Fig 5
        for (k,v) in self_normalized.terms.items():
            c1 = v
            c2 = other_normalized.terms[k]

            c = c1 * c2
            tmp[k] = c
        
        self_times_other.terms = tmp

        #cleanup, stuff gets very memory intensive
        del(self_normalized)
        del(other_normalized)
        return self_times_other


    #apply the normalization process as described in Definition 7
    #given two expressions 'self' and 'other', returns 'self' normalized wrt to 'other'
    def normalize(self, other: 'Expression') -> 'Expression':
        self_sym_vars = next(iter(self.terms))
        #correlation classes used in self
        self_corr_classes = {i.corr_class for i in self_sym_vars}
        
        other_sym_vars = next(iter(other.terms))
        #correlation classes used in other
        other_corr_classes = {i.corr_class for i in other_sym_vars}

        #simple set difference gives correlation classes that have to be sucked into 'self'
        classes_to_normalize_with = other_corr_classes - self_corr_classes

        #nothing to normalize
        if len(classes_to_normalize_with) == 0:
            return self

        e = Expression()
        new_terms = dict(self.terms.items())
        #now this is kind of hacky, just trust that it works

        for cl in classes_to_normalize_with:
            #for each correlation class to be sucked in

            #create an aux dictionary
            aux = dict[frozenset[SymVar], Decimal]()

            #the sym vars that have to be brought in to each term 
            sym_vars_to_normalize = cl.sym_vars
            #cross product
            p = product(new_terms.keys(), sym_vars_to_normalize)
            for (i, j) in p:
                tmp = [v for v in i]
                tmp.append(j)
                # map the constant coefficients back
                aux[frozenset(tmp)] = new_terms[i]
            
            new_terms = dict(aux.items())
        
        #new_terms gives the terms of the normalized expression
        e.terms = new_terms

        return e
        
    def get_correlation_classes_used(self):
        return self.corr_classes
    
    def init_for_correlation_class(self, corr_class: CorrelationClass) -> None:
        sym_vars = corr_class.sym_vars
        self.terms = {frozenset([i]): 0 for i in sym_vars}
    
    def init_for_fact(self, fact: str, corr_class: CorrelationClass) -> None:
        self.init_for_correlation_class(corr_class)
        
        fact_index = corr_class.get_index_of_fact(fact)
        set_coeff_1 = [frozenset([i]) for i in corr_class.sym_vars if i.name[fact_index] == '1']
        self.terms.update(dict.fromkeys(set_coeff_1, 1))

    def multiply_by_const(self, coeff: Decimal):
        e = Expression()
        #deep copy
        e.terms = dict(self.terms.items())
        for i, v in e.terms.items():
            e.terms[i] = v * coeff
        return e
    
    def to_grb_sum(self, ctx: Context) -> LinExpr:
        """ converts an Expression to a GRB quicksum"""
        aux_count = ctx.aux_count
        m = ctx.model
        from util import make_grb_var

        #print(f'building grb sum for {self}')
        #convert expression into a gurobi sum, using aux variables if needed
        #the process will be to convert each term in the expression into a grb quadratic product
        #and then quicksum the whole thing

        #the number of correlation classes involved in this expression will tell us if an aux var is required or not
        #this is not used at the moment. just use aux vars all the time
        is_aux_required = len(self.get_correlation_classes_used()) > 1
        #print(is_aux_required)

        grb_sum_terms = list[Var]()
        for i, v in self.terms.items():
            grb_vars_in_term = [j.grb_var for j in i if v != 0]
            if len(grb_vars_in_term) != 0:
                aux_var = make_grb_var(m, f'aux{aux_count}')
                m.addConstr(aux_var == float(v) * grb_vars_in_term[0], name=f'c_aux{aux_count}')
                aux_count += 1
                acc = aux_var
                for grb_var in grb_vars_in_term[1:]:
                    aux_var = make_grb_var(m, f'aux{aux_count}')
                    m.addConstr(aux_var == acc * grb_var , name=f'c_aux{aux_count}')
                    aux_count += 1
                    acc = aux_var
                
                grb_sum_terms.append(acc)
        

        ctx.aux_count = aux_count
        return quicksum(grb_sum_terms)