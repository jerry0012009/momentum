# jerry/momentum

## Current Mainline

This repository's active work is the **crypto USDT perpetual cross-sectional factor library**.

当前主线是**加密永续合约截面因子库**。

The current stage is research diagnostics: build factors, evaluate them consistently, keep the process reproducible, and prepare a maintainable base for later signal construction and backtesting. This is **not** production, live trading, investment advice, or alpha verification.

当前阶段是研究诊断：标准化构建因子、评价因子、保持可复现，并为后续信号合成和回测打基础。不是生产系统、不是实盘、不是投资建议、不是 alpha 验证。

## Start Here

The only developer entry point for factor-library work is:

- [docs/factor_library/START_HERE.md](docs/factor_library/START_HERE.md)

Use that file to add factors, run factor evaluation, inspect outputs, and understand which files are source code versus generated artifacts.

因子库开发只从这个入口开始：新增因子、运行评价、查看结果、区分源码和自动生成产物，都看这里。

Current generated state:

- [research/factor_runs/crypto_top50_factor_library/factor_library_state.md](research/factor_runs/crypto_top50_factor_library/factor_library_state.md)

## Boundaries

- Do not create parallel factor pipelines, one-off factor evaluators, or `*_v2.py` entry points.
- Do not manually edit generated outputs under `research/factor_runs/` or display pages under `reports/site/factor-library/`.
- Change source scripts or input data, then regenerate outputs.
- Historical strategy research, old phase notes, and archived reports are preserved for audit context only; they are not the current factor-library entry path.

边界：不要新增平行流程、一次性评价脚本或 `*_v2.py` 入口；不要手改 `research/factor_runs/` 和 `reports/site/factor-library/` 里的生成结果；要改就改源码或输入，然后重新生成。

## Public Display

The factor-library site is a display surface, not the developer control surface:

- [reports/site/factor-library/index.html](reports/site/factor-library/index.html)
- [reports/site/factor-library/factor-evaluation.html](reports/site/factor-library/factor-evaluation.html)
- [reports/site/factor-library/signal-evaluation-summary.html](reports/site/factor-library/signal-evaluation-summary.html)
