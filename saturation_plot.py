"""Plot saturation verification results."""

import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


with open("/home/claude/saturation_results.json") as f:
    results = json.load(f)

# Organize: results_by_n[n] = list of (beta, gap_mean, gap_std)
results_by_n = {}
for key, v in results.items():
    n = v["n"]
    beta = v["beta"]
    gaps = np.array(v["gaps"])
    results_by_n.setdefault(n, []).append((beta, gaps.mean(), gaps.std()))

for n in results_by_n:
    results_by_n[n].sort()

# Figure with 3 panels:
#   (a) g_1 vs beta for each n
#   (b) eta(beta) = g_1 / (beta * 0.0155) for each n
#   (c) eta_n(beta) = g_1 / (beta * lambda_0(n))  with per-n lambda_0 fit

fig, axes = plt.subplots(1, 3, figsize=(16, 4.8))

LAMBDA_0_DOC = 0.0155
ns_sorted = sorted(results_by_n.keys())

# --- (a) g_1 vs beta ---
ax = axes[0]
for n in ns_sorted:
    rows = results_by_n[n]
    bs = [r[0] for r in rows]
    ms = [r[1] for r in rows]
    ss = [r[2] for r in rows]
    ax.errorbar(bs, ms, yerr=ss, fmt="o-", capsize=3, lw=1.6, label=f"n={n}")
# claimed saturation region
ax.axvspan(35, 51, color="red", alpha=0.08, label="user's claimed saturation region")
ax.set_xlabel(r"$\beta$")
ax.set_ylabel(r"first-tour gap $g_1$")
ax.set_title(r"(a) $g_1$ vs $\beta$ — does it saturate?")
ax.legend()
ax.grid(alpha=0.3)

# --- (b) eta with documents lambda_0 = 0.0155 ---
ax = axes[1]
for n in ns_sorted:
    rows = results_by_n[n]
    bs = np.array([r[0] for r in rows])
    ms = np.array([r[1] for r in rows])
    ss = np.array([r[2] for r in rows])
    eta = ms / (bs * LAMBDA_0_DOC)
    eta_std = ss / (bs * LAMBDA_0_DOC)
    ax.errorbar(bs, eta, yerr=eta_std, fmt="o-", capsize=3, lw=1.6,
                label=f"n={n}")
ax.axhline(1.0, linestyle="--", color="gray", alpha=0.6, label=r"$\eta=1$")
ax.set_xlabel(r"$\beta$")
ax.set_ylabel(r"$\eta(\beta) = g_1/(\beta\cdot 0.0155)$")
ax.set_title(r"(b) $\eta(\beta)$ with doc's $\lambda_0=0.0155$")
ax.legend()
ax.grid(alpha=0.3)

# --- (c) per-n lambda_0 fit, then eta with that ---
ax = axes[2]
fitted_lambdas = {}
for n in ns_sorted:
    rows = results_by_n[n]
    bs = np.array([r[0] for r in rows])
    ms = np.array([r[1] for r in rows])
    # fit: g_1 = lambda_0 * beta + c, but ideally c = 0
    # use simple slope through origin: lambda_0 = sum(b*g)/sum(b^2)
    lam = np.sum(bs * ms) / np.sum(bs ** 2)
    fitted_lambdas[n] = lam
    eta = ms / (bs * lam)
    ax.plot(bs, eta, "o-", lw=1.6, label=f"n={n}, λ₀={lam:.4f}")
ax.axhline(1.0, linestyle="--", color="gray", alpha=0.6, label=r"$\eta=1$")
ax.set_xlabel(r"$\beta$")
ax.set_ylabel(r"$\eta(\beta)$ with per-$n$ $\lambda_0$")
ax.set_title(r"(c) $\eta(\beta)$ with refitted $\lambda_0(n)$")
ax.legend()
ax.grid(alpha=0.3)

plt.tight_layout()
out = "/home/claude/saturation_verdict.png"
plt.savefig(out, dpi=130)
print(f"Saved: {out}")

# --- Print numerical summary ---
print(f"\n=== Per-n lambda_0 fits (g_1 / beta slope) ===")
print(f"{'n':>4s}  {'lambda_0':>10s}")
for n, lam in fitted_lambdas.items():
    print(f"{n:>4d}  {lam:>10.5f}")

print(f"\nReference lambda_0 from document: {LAMBDA_0_DOC:.4f}")
print(f"\n=== g_1/beta (raw 'eta-without-normalization') ===")
print(f"{'n/β':>4s}", *[f"{b:>8d}" for b in [20, 25, 30, 35, 40]])
for n in ns_sorted:
    rows = {b: m for b, m, _ in results_by_n[n]}
    line = [f"{n:>4d}"]
    for b in [20, 25, 30, 35, 40]:
        if b in rows:
            line.append(f"{rows[b]/b:>8.5f}")
        else:
            line.append(f"{'-':>8s}")
    print(*line)
