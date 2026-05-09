"""
Saturation verification.

For each (n, beta) pair, measure first-tour gap g_1 = -log(E_1/E_0)
across multiple seeds. Compare eta(beta) = g_1/(beta * 0.0155) across n
to determine whether the saturation/collapse failure observed at beta>35
is a real phenomenon or a finite-n / fpylll-implementation artifact.

Saves incrementally to JSON so the run can be stopped & resumed at will.
"""

import os
import json
import time
import sys
import numpy as np

from fpylll import IntegerMatrix, LLL, BKZ, FPLLL
from fpylll.algorithms.bkz2 import BKZReduction


RESULTS_PATH = "/home/claude/saturation_results.json"


def compute_E(M, n):
    return float(np.var([0.5 * np.log(M.get_r(i, i)) for i in range(n)]))


def first_tour_gap(seed, n, k, q, beta):
    FPLLL.set_random_seed(seed)
    A = IntegerMatrix.random(n, "qary", k=k, q=q)
    LLL.reduction(A)
    bkz = BKZReduction(A)
    M = bkz.M
    M.update_gso()
    E0 = compute_E(M, n)
    par = BKZ.Param(block_size=beta)
    bkz.tour(par)
    M.update_gso()
    E1 = compute_E(M, n)
    return -np.log(E1 / E0), E0, E1


def load_results():
    if os.path.exists(RESULTS_PATH):
        with open(RESULTS_PATH) as f:
            return json.load(f)
    return {}


def save_results(results):
    with open(RESULTS_PATH, "w") as f:
        json.dump(results, f, indent=2)


def main():
    # Budget-limited config. Pass plan as CLI arg: "cheap" or "all"
    plan = sys.argv[1] if len(sys.argv) > 1 else "cheap"

    if plan == "cheap":
        # Quick first pass: all n at low/medium beta
        ns = [70, 80, 100]
        betas = [20, 25, 30, 35, 40]
    elif plan == "high_beta":
        # Add high beta - more expensive
        ns = [70, 80, 100]
        betas = [45]
    elif plan == "n120":
        # Add n=120 if time permits
        ns = [120]
        betas = [20, 25, 30, 35, 40]
    else:
        raise ValueError(f"unknown plan: {plan}")

    seeds = [1, 2, 3]
    q = 521

    results = load_results()
    print(f"Plan: {plan}")
    print(f"ns = {ns}, betas = {betas}, seeds = {seeds}")
    print(f"already cached: {len(results)} entries\n")

    for n in ns:
        k = n // 2
        for beta in betas:
            key = f"n{n}_b{beta}"
            if key in results:
                cached = results[key]
                print(f"  cached  {key}: g_1 = "
                      f"{np.mean(cached['gaps']):.4f} ± {np.std(cached['gaps']):.4f}")
                continue
            gaps, E_pairs = [], []
            t0 = time.time()
            for s in seeds:
                g, e0, e1 = first_tour_gap(s, n, k, q, beta)
                gaps.append(g)
                E_pairs.append([e0, e1])
            elapsed = time.time() - t0
            results[key] = {
                "n": n, "beta": beta, "k": k, "q": q,
                "seeds": seeds, "gaps": gaps,
                "E_pairs": E_pairs, "time_sec": elapsed,
            }
            save_results(results)
            print(f"  done    {key}: g_1 = "
                  f"{np.mean(gaps):.4f} ± {np.std(gaps):.4f}   "
                  f"({elapsed:.1f}s)")

    print(f"\nTotal entries: {len(results)}")


if __name__ == "__main__":
    main()
