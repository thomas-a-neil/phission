import msprime
import numpy as np


def simulate_haplotype_matrix(sample_size,
                              Ne=1e4,
                              length=5e3,
                              recombination_rate=0,
                              mutation_rate=2e-8,
                              random_seed=None):
    """
    Returns an n individual x m SNP haplotype matrix of 0s and 1s.

    TODO nthomas: some way to request a number of SNPs. Depends on Ne, so probably
    need to oversimulate, then truncate. Or just let the user do that downstream.
    """
    tree_sequence = msprime.simulate(
         sample_size=sample_size,
         Ne=Ne,
         length=length,
         recombination_rate=recombination_rate,
         mutation_rate=mutation_rate,
         random_seed=random_seed)

    haplotype_matrix = tree_sequence.genotype_matrix().T
    # we take the transpose to get individuals in rows, SNPs in columns
    return haplotype_matrix


def compress_to_genotype_matrix(haplotypes):
    """
    Assumes 0s and 1s in haplotype matrix (output of msprime)

    e.g.
    array([[1, 1, 1, ..., 1, 1, 0],
           [1, 1, 0, ..., 1, 1, 0],
           [1, 0, 1, ..., 0, 0, 0],
           ...,
           [1, 1, 1, ..., 1, 1, 0],
           [1, 0, 1, ..., 0, 0, 0],
           [1, 1, 1, ..., 1, 1, 0]])
    """
    return haplotypes[::2] + haplotypes[1::2]


def get_incomplete_phasing_matrix(genotypes):
    """
    Assumes 0s, 1s, and 2s in genotype matrix

    array([[0, 0, 0, ..., 0, 0, 2],
           [0, 0, 1, ..., 0, 0, 2],
           [0, 1, 0, ..., 2, 2, 2],
           ...,
           [0, 0, 0, ..., 0, 0, 2],
           [0, 1, 0, ..., 1, 1, 2],
           [0, 0, 0, ..., 0, 0, 2]], dtype=uint8)

    Returns:
        a matrix with 0s and 1s in homozygous positions. -1s in unphased, heterozygous positions
    """
    to_duplicate = 0*(genotypes == 0).astype(int) + -1*(genotypes == 1).astype(int) + 1*(genotypes == 2).astype(int)
    n, m = to_duplicate.shape

    incomplete_haplotypes = np.zeros((2*n, m))
    incomplete_haplotypes[::2] = to_duplicate
    incomplete_haplotypes[1::2] = to_duplicate
    return incomplete_haplotypes
