# Chip Distribution（筹码分布）

## 1. 定义
筹码分布是“当前仍持有筹码在不同价格区间的占比估计”。

- 不是账户级真值
- 是基于成交量与换手率的递推估计

## 2. 公式
离散价格桶递推：

\[
C_t[i] = (1 - \tau_t) \cdot C_{t-1}[i] + \tau_t \cdot A_t[i]
\]

- `C_t[i]`：t 日收盘后，价格桶 i 的筹码占比
- `τ_t`：当日换手率（`volume / shares`）
- `A_t[i]`：当日成交在价格桶上的分布（默认三角分布）

## 3. 跨标的/跨币种处理
采用**对数价格网格**（0.5% 步长）：

- `step = ln(1 + 0.005)`
- 这样不同价格级别标的可用同一分桶尺度

并输出一份归一化分布：

- `moneyness = ln(price_bin / close_t)`
- 可跨标的比较“当前价附近筹码结构”

## 4. 输入要求
最小字段（silver）：
- `timestamp, symbol, open, high, low, close, volume`

另需 shares（优先级）：
1. 数据内 `shares_col`
2. `config/features/chip_distribution.yaml` 的 `shares.symbol_shares`
3. CLI 传入 `--default-shares`

## 5. 代码位置
- 计算模块：`src/momentum/factors/chip_distribution.py`
- 批处理脚本：`scripts/build_chip_distribution.py`
- 配置：`config/features/chip_distribution.yaml`

## 6. 执行示例
```bash
cd jerry/momentum
source .venv/bin/activate

# 仅跑小米
python scripts/build_chip_distribution.py --symbols 1810.HK
```

## 7. 输出文件
默认输出到：`outputs/chip_distribution/`

- `chip_distribution_asset.csv`
  - `timestamp, symbol, price_bin, chip_pct`
- `chip_distribution_normalized.csv`
  - `timestamp, symbol, moneyness_bin, chip_pct`
- `chip_summary_daily.csv`
  - `timestamp, symbol, close, shares, turnover, avg_cost, cost_p50, cost_p90, winner_ratio, trapped_ratio`
- `run_meta.json`

## 8. 注意事项
- 日线版本是估算，分钟级成交可提升精度
- 公司行为（拆股/配股/回购等）会影响解释，需要后续增强
- `turnover_cap` 默认 1.0，避免异常成交导致不稳定
