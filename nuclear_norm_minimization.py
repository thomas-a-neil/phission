from cvxpy import Minimize, Problem, Variable, SCS, mul_elemwise, norm, sum_squares
import numpy as np


def phase(unphased, mu=1):
    """
    Matrix completion with phasing
    """
    # import pdb; pdb.set_trace()
    mask = get_mask(unphased)
    X = nuclear_norm_solve(unphased, mask, mu)
    # round to the nearest integer
    return np.matrix.round(X)


def nuclear_norm_solve(unphased, mask, mu):
    """
    Parameters:
    -----------
    unphased : m x n array
        matrix we want to complete
    mask : m x n array
        matrix with entries zero (if missing) or one (if present)
    mu : float
        hyper-parameter controlling trade-off between nuclear norm and square loss

    Returns:
    --------
    X: m x n array
        completed matrix
    """
    X = Variable(*unphased.shape)
    objective = Minimize(norm(X, "nuc") +
                         mu * sum_squares(mul_elemwise(mask, X - unphased)))
    constraints = get_sum_to_0_constraints(unphased, X)  # TODO nthomas: maybe this should be an argument to the fn
    constraints += get_symmetry_breaking_constraints(unphased, X)
    problem = Problem(objective, constraints)
    problem.solve(solver=SCS)
    return X.value


def get_symmetry_breaking_constraints(unphased, X):
    """
    A is our starting matrix, it has 0s in the spot we need to phase
    X is our cvxpy variable that we're solving for.

    We want the first set of indexes for every 0/0 unphased pair for each individual
    """
    constraints = []
    indexes = get_unmasked_even_indexes(unphased)
    seen_individuals = set()
    for i, j in indexes:
        if i not in seen_individuals:
            constraints.append(X[i, j] == 1)
            constraints.append(X[i + 1, j] == -1)
            seen_individuals.add(i)
    return constraints


def get_sum_to_0_constraints(unphased, X):
    """
    A is our starting matrix, it has 0s in the spot we need to phase
    X is our cvxpy variable that we're solving for.

    We need each pair of phased haplotypes to sum to 0 (i.e. one is -1 and the other is 1)
    """
    constraints = []
    indexes = get_unmasked_even_indexes(unphased)
    for i, j in indexes:
        constraints.append((X[i, j] + X[i + 1, j]) == 0)
    return constraints


def get_mask(A):
    """
    Gets a mask indicating non-homozygous elements from haplotype matrix A
    """
    return A != 0


def get_unmasked_even_indexes(A):
    """
    Takes in a matrix A of haplotypes and returns the ones where we will have
    to do phasing (i.e. 0s)

    For use in setting up constraints.
    """
    i, j = np.nonzero(1 - get_mask(A))
    new_i = []
    new_j = []
    # we're going to filter out all of the odds, since we know about those already
    # and maybe it'll be confusing later on? I'm not sure. I guess we could just remove them later.
    # but I'd rather have a set where I can be like (i, j) + (i+1, j) == 1. basically.
    for index in range(len(i)):
        if i[index] % 2 == 0:
            new_i.append(i[index])
            new_j.append(j[index])

    return zip(new_i, new_j)
