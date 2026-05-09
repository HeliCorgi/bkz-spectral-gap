# BKZ Spectral Gap — Empirical Validation

BKZ 格子簡約アルゴリズムの spectral gap を実測し、"effective theory of BKZ" の構造的予言を検証する一連のスクリプト。

## 主な内容

- BKZ-β の reduction 品質指標 (root Hermite factor δ, GSO slope) の測定
- Tour 単位での `E_t = Var(log‖b_i*‖)` の追跡
- First-tour gap `g_1 = -log(E_1/E_0)` を用いた spectral gap 推定
- η(β) collapse / saturation の verification (n=70, 80, 100 across β=20-40)

## セットアップ

```bash
pip install -r requirements.txt
```

`fpylll` のビルドには C++ コンパイラ・MPFR・GMP が必要です。Linux/Mac の環境では概ね動きますが、Windows ではビルドが面倒なため WSL を推奨。

## ファイル構成

| ファイル | 内容 |
|---|---|
| `bkz_experiment.py` | LLL vs BKZ-β の reduction quality 比較 (root Hermite factor、GSO profile) |
| `bkz_gap_experiment.py` | Tour-by-tour の E_t 記録、3 estimator で gap(β) を比較 |
| `bkz_gap_refined.py` | Plateau-floor を考慮した gap 推定 (first-tour 方式の優位性を示す) |
| `saturation_verify.py` | n × β grid で first-tour gap を計測。Incremental save (`saturation_results.json`) |
| `saturation_plot.py` | `saturation_results.json` を読み込んで verdict 図を生成 |

## 主な発見 (現時点)

- **First-tour gap は β に関して線形**: 固定 n では η(β) = g_1/(β·λ_0) ≈ 1
- **λ_0 は n に依存**: n=70 で 0.0157、n=100 で 0.0109
- **β=35 での saturation は estimator artifact**: 多-tour 平均が plateau bias を受けるため見かけ上発生
- 真の現象: g_1 は β=20-40 で単調増加 (n=70/80/100 すべてで確認)

## 実行例

```bash
# Reduction quality baseline
python bkz_experiment.py

# Tour-by-tour gap trace
python bkz_gap_experiment.py

# Plateau-aware gap analysis
python bkz_gap_refined.py

# Saturation verification (incremental, can be stopped/resumed)
python saturation_verify.py cheap     # n=70/80/100, β=20-40
python saturation_verify.py high_beta # add β=45
python saturation_verify.py n120      # add n=120
python saturation_plot.py             # produce verdict figure
```

## 計算コスト目安

n=100, β=40 で 1 tour あたり ~25 秒。β を 1 段上げると概ね 3-4 倍。  
β=45 以上 / n=120 以上は本格的なマシンを推奨。

## ライセンス

研究用の private な作業中コード。
