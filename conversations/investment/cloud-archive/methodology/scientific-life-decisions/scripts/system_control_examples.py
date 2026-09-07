#!/usr/bin/env python3
"""Two synthetic control counterexamples; no personal forecasts or external actions.

Use python3 system_control_examples.py --self-test for analytic/numeric checks.
Only the Python standard library is needed. Fractions preserve exact recurrences.
"""
import argparse
import cmath
from fractions import Fraction as F
import json
import math


def trajectory(gain, delayed, steps=40):
    """x[t+1]=x[t]+u[t]; x[-1]=x[0]=1; unconstrained noiseless input."""
    previous = current = F(1)
    xs = [current]
    for _ in range(steps):
        observed = previous if delayed else current
        previous, current = current, current - gain * observed
        xs.append(current)
    return xs


def poles(gain, delayed):
    if not delayed:
        return [complex(1 - gain)]
    discriminant = cmath.sqrt(complex(1 - 4 * gain))
    return [(1 + discriminant) / 2, (1 - discriminant) / 2]


def classify(roots):
    radius = max(map(abs, roots))
    if radius > 1 + 1e-12:
        return "unstable"
    if radius < 1 - 1e-12:
        return "asymptotically_stable"
    # Repeated unit roots would require a Jordan-structure check in general.
    return "unit_circle_boundary_not_asymptotically_stable"


def rank2(matrix):
    """Exact rank for this tutorial's 2x2 matrices only."""
    if matrix[0][0] * matrix[1][1] != matrix[0][1] * matrix[1][0]:
        return 2
    return int(any(value != 0 for row in matrix for value in row))


def reachability_observability(b, c):
    # A = diag(4/5, 11/10). The two distinct modes are deliberately specified.
    a1, a2 = F(4, 5), F(11, 10)
    reach = [[b[0], a1 * b[0]], [b[1], a2 * b[1]]]
    observe = [[c[0], c[1]], [c[0] * a1, c[1] * a2]]
    return rank2(reach), rank2(observe)


def self_test():
    checks = 0
    # Compare exact recurrences against the no-delay closed form, including
    # zero gain, immediate correction, oscillation, and the unstable regime.
    for gain in (F(0), F(1, 4), F(1, 2), F(1), F(3, 2), F(5, 2)):
        xs = trajectory(gain, False)
        assert all(value == (1 - gain) ** t for t, value in enumerate(xs))
        checks += 1
    # Independent closed-form two-root solution checks delayed trajectories.
    for gain in (F(1, 2), F(1), F(3, 2)):
        r1, r2 = poles(gain, True)
        alpha = (complex(1 - gain) - r2) / (r1 - r2)
        for t, value in enumerate(trajectory(gain, True, 20)):
            predicted = alpha * r1 ** t + (1 - alpha) * r2 ** t
            assert math.isclose(predicted.real, float(value), abs_tol=1e-9)
            assert abs(predicted.imag) < 1e-9
        checks += 1
    assert classify(poles(F(3, 2), False)) == "asymptotically_stable"
    assert classify(poles(F(3, 2), True)) == "unstable"
    assert classify(poles(F(1, 2), True)) == "asymptotically_stable"
    checks += 1
    # At k=1 the delayed roots are distinct on the unit circle: periodic,
    # bounded, non-decaying. Do not label every non-decaying case unstable.
    periodic = trajectory(F(1), True, 30)
    assert periodic[:6] == [F(1), F(0), F(-1), F(-1), F(0), F(1)]
    assert all(periodic[t] == periodic[t % 6] for t in range(len(periodic)))
    assert classify(poles(F(1), True)).startswith("unit_circle_boundary")
    checks += 1
    assert reachability_observability((F(1), F(0)), (F(1), F(0))) == (1, 1)
    assert reachability_observability((F(1), F(1)), (F(1), F(1))) == (2, 2)
    assert reachability_observability((F(1), F(0)), (F(1), F(1))) == (1, 2)
    checks += 1
    # Hidden state grows even with all displayed output samples equal to zero.
    x = (F(0), F(1))
    for t in range(41):
        assert x[0] == 0 and x[1] == F(11, 10) ** t
        x = (F(4, 5) * x[0], F(11, 10) * x[1])
    checks += 1
    return checks


def report():
    cases = []
    for delayed, gain in ((False, F(1, 2)), (False, F(3, 2)),
                          (True, F(1, 2)), (True, F(1)), (True, F(3, 2))):
        xs = trajectory(gain, delayed)
        roots = poles(gain, delayed)
        cases.append({
            "delay_steps": int(delayed), "gain": str(gain),
            "spectral_radius": max(map(abs, roots)),
            "analytic_classification": classify(roots),
            "x40": float(xs[-1]),
            "peak_absolute_x_in_last_10_samples": float(max(map(abs, xs[-10:]))),
        })
    return {
        "scope": "synthetic, finite-dimensional discrete-time LTI examples only",
        "assumptions": ["specified exact model", "no noise", "unbounded control input",
                        "fixed parameters", "no real-person data or effectiveness claims"],
        "feedback": {"plant": "x[t+1] = x[t] + u[t]", "initial": "x[-1]=x[0]=1",
                     "policy": "u[t]=-k*x[t-delay]", "cases": cases},
        "hidden_mode": {
            "A": [[0.8, 0], [0, 1.1]], "B": [1, 0], "C": [1, 0],
            "initial_x": [0, 1], "input": "zero",
            "ranks_reachability_observability": reachability_observability((F(1), F(0)), (F(1), F(0))),
            "all_output_samples": 0, "hidden_x40": float(F(11, 10) ** 40),
            "B_and_C_both_1_1_ranks": reachability_observability((F(1), F(1)), (F(1), F(1))),
            "limit": "Full rank does not guarantee a feasible input with resource limits or reliable estimation with noise.",
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    result = report()
    if args.self_test:
        result["validation"] = {"status": "passed", "check_groups": self_test()}
    print(json.dumps(result, ensure_ascii=False, indent=2))
