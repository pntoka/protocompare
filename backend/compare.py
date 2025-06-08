import json
import numpy as np
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment

def compare(emb_a, emb_b):

    emb_a = emb_a / np.linalg.norm(emb_a, axis=1, keepdims=True)
    emb_b = emb_b / np.linalg.norm(emb_b, axis=1, keepdims=True)
    # Compute similarity matrix (cosine -> similarity)
    sim_matrix = 1 - cdist(emb_a, emb_b, metric="cosine")  # shape (n_a, n_b)

    # Hungarian algorithm to find maximal alignment
    cost_matrix = -sim_matrix  # maximize similarity -> minimize negative similarity
    row_ind, col_ind = linear_sum_assignment(cost_matrix)

    # Aggregate score: mean similarity of assigned pairs, penalize unmatched steps
    matched_sims = sim_matrix[row_ind, col_ind]
    # Simple penalty: unmatched steps count as similarity 0
    unmatched = abs(emb_a.shape[0] - emb_b.shape[0])
    overall = sum(np.max(sim_matrix, axis=0)/emb_a.shape[0])
    return float(overall), list(zip(row_ind.tolist(), col_ind.tolist())), sim_matrix
