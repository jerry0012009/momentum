# Rank444 — Reproduction

## 环境要求

### Python 依赖

```
pandas>=2.0
numpy>=1.24
yfinance>=1.2.0
akshare>=1.10    # 仅国内期货/A股需要
```

注意：`requirements-m1.txt` 中列出的是 `yfinance==1.2.0`，但 akshare 未列入依赖文件。

### Python 版本

TODO: verify（代码使用 f-string，至少 Python 3.6+）

---

## 复现命令

### v1 — 基础回测

```bash
cd /root/clawd/jerry/momentum
source .venv/bin/activate        # TODO: verify venv 路径
python scripts/rank444_rsi_bb_backtest.py
```

**输出：** `reports/artifacts/rank444_rsi_bb/backtest_results.json`

**注意事项：**
- 需要网络连接（实时拉取 yfinance / akshare 数据）
- A股标的需要 akshare 可用（可能需要 tushare token 或代理）
- 碳酸锂期货 symbol 尝试多个变体（LC0/lc2401/lc2406/lc2407/LC2401），可能全部失败
- 运行时间：约 2-5 分钟（取决于网络）

### v2 — 完整回测（多频率 + 参数稳定性 + 时间稳定性）

```bash
cd /root/clawd/jerry/momentum
source .venv/bin/activate
python scripts/rank444_full_backtest.py
```

**输出：** `reports/artifacts/rank444_rsi_bb/full_results_v2.json`

**注意事项：**
- 参数网格 108 种组合 × 10+ 标的 × 2 出场模式 → 运行较慢
- 多频率测试（1d + 1h）会触发 yfinance 的 rate limit
- 运行时间：约 10-30 分钟

### v3 — 扩展参数网格（750 组合）

```bash
python scripts/rank444_v3_backtest.py    # TODO: verify 确切文件名
```

**输出：** `reports/artifacts/rank444_rsi_bb/full_results_v3.json`

### v4 — Regime 分析

```bash
python scripts/rank444_v4_regime.py      # TODO: verify
```

**输出：** `reports/artifacts/rank444_rsi_bb/full_results_v4.json`

### v5 — 国内期货

```bash
python scripts/rank444_v5_cn_futures.py  # TODO: verify
```

**输出：** `reports/artifacts/rank444_rsi_bb/cn_futures_v5.json`

### v6 — Long/Short 对比

```bash
python scripts/rank444_v6_long_short.py  # TODO: verify
```

**输出：** `reports/artifacts/rank444_rsi_bb/full_results_v6.json`

---

## 输出产物清单

| 文件 | 大小 | 内容 | 版本 |
|------|------|------|------|
| `backtest_results.json` | ~68 KB | 13标的 × 2出场模式，含逐笔交易 | v1 |
| `full_results_v2.json` | ~67 KB | 10标的 + 多频率 + 参数稳定性 + 时间稳定性 | v2 |
| `full_results_v3.json` | ~252 KB | 750参数组合网格 | v3 |
| `full_results_v4.json` | ~69 KB | 15年 regime 分析（牛/熊） | v4 |
| `cn_futures_v5.json` | ~57 KB | 14个国内期货深度分析 | v5 |
| `full_results_v6.json` | ~63 KB | long-only vs short-only vs long-short | v6 |

---

## 复现性评估

### ❌ 无法保证精确复现

原因：
1. **数据未固化** — yfinance/akshare 每次返回的数据可能不同
2. **无 commit hash 锁定** — 脚本可能已被修改
3. **无随机种子** — 回测本身无随机性，但数据获取有不确定性
4. **akshare 版本敏感** — 不同版本可能返回不同格式

### 部分复现建议

如果只需要验证"策略逻辑是否正确"：
1. 用固定数据集（如从已保存的 JSON 中提取交易列表）重跑
2. 对比 trades 列表是否一致

如果需要完全复现：
1. 先固化数据（从当前 JSON 中提取 OHLCV 或重跑一次并保存 parquet）
2. 锁定 commit hash
3. 记录 Python 版本和依赖版本

---

## 脚本版本清单

| 脚本 | 功能 | 行数 |
|------|------|------|
| `rank444_rsi_bb_backtest.py` | v1 基础回测 | 395 |
| `rank444_full_backtest.py` | v2 完整回测 | 484 |
| `rank444_v3_backtest.py` | v3 参数网格 | TODO: verify |
| `rank444_v4_regime.py` | v4 regime | TODO: verify |
| `rank444_v5_cn_futures.py` | v5 国内期货 | TODO: verify |
| `rank444_v6_long_short.py` | v6 long/short | TODO: verify |
| `rank444_generate_report.py` | v1 报告 | TODO: verify |
| `rank444_generate_report_v2.py` | v2 报告 | TODO: verify |
| `rank444_gen_report_v3.py` | v3 报告 | TODO: verify |
| `rank444_gen_report_v4.py` | v4 报告 | TODO: verify |
| `rank444_gen_report_v5.py` | v5 报告 | TODO: verify |
| `rank444_gen_report_v6.py` | v6 报告 | TODO: verify |
| `rank444_gen_report_final.py` | 综合报告 | TODO: verify |
