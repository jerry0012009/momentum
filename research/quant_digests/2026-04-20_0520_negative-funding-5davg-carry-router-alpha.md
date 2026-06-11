# 别把这份 Hyperliquid funding screener 只读成“排行榜”：对 short-cycle crypto desk，更该先拆的是「5d 平均 funding 最负那一档 × next 1~3h carry persistence」这条 raw alpha
- 时间：2026-04-20 05:20 UTC
- 类型：GitHub / public-data replication
- 主题类型：raw alpha
- 基础 alpha：`long 最负 funding perp + 外部对冲腿`，赚未来几小时继续收到的 funding carry
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：carry / funding / cross-sectional / relative value / stat-arb / Hyperliquid / 15m child execution
- 证据类型：工程经验 + public-data replication

## 1. 这次看了什么
看的是 `traders-ark/hyperliquid-carry-screener`：它表面只是把 Hyperliquid 各币种 `current / 1d / 3d / 5d` funding 排名做成看板，但更值钱的读法不是“看谁 funding 高”，而是把它当成 **carry raw alpha 的横截面选币器**。

## 2. 核心结论
- 这份 repo 真正可复用的不是页面，而是它公开了 **全市场 funding 历史拉取 + 多窗口平均排名** 这条骨架。
- 我用 repo 自带 `funding_data_main.csv`（`2026-01-20~2026-04-20`，`229` 个币，约 `49.4` 万条 hourly funding）做快检：每小时按过去 `5d` 平均 funding 排名，只做**最负 funding 一档**，下一小时平均可收约 `+4.47 bps`，未来 `3h` 累计约 `+13.07 bps`，命中率约 `87.9% / 92.2%`（`n=2037`）。
- 反过来只做**最正 funding 一档**去 short 并不行：next `1h / 3h` 约 `-2.01 / -6.02 bps`，说明当前这套数据里真正厚的 pocket 不是“short rich-funding”，而是 **long deeply negative-funding**。
- 今日 repo 快照也支持“负 funding 更像 persistent pocket”这个读法：负向 top10 在 `1d∩3d∩5d` 里仍有 `7` 个重合（`BLAST/BLUR/COMP/FET/FTT/MOVE/YZY`）；正向三窗重合虽有 `8` 个，但历史 realized carry 仍明显不如负向。

## 3. 为什么和当前项目有关
这不是慢频“收租综述”，而是能直接补进 desk 原料池的一条 **carry / relative-value raw alpha**：母信号在 hourly funding 排名，执行层完全可以下放到 `15m`，做 funding 结算前后的 child execution、spread veto 和 maker-first 入场。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / carry
- 基础 alpha：过去 `5d` 平均 funding 最负的 perp，未来 `1~3h` 仍更可能继续保持“做多 perp 可收 funding”
- regime：资金费率分化明显、负 funding cluster 持续存在时更有效
- filter / veto：只保留 `5d` 最负一档；可再加 `1d/3d/5d` 共识排名、流动性阈值、单币 funding cap
- risk / sizing / execution overlay：对冲腿做 beta-neutral；按 funding 绝对值或盘口深度缩仓；`15m` 执行避开极薄盘口与大价差时段

## 4. 可复刻的最小实验
- 研究假设：`5d` 平均 funding 最负的币，未来几小时继续维持负 funding 的概率更高。
- 可计算定义：每小时对全市场做 `avg_funding_5d` 排名，选最小值；交易为 `long perp + hedge leg`，持有 `1h / 3h`，只记 funding PnL 与基础交易成本。
- 最小回测切口：Hyperliquid public funding history；先做 `top1`，再扩到 `top3` 等权；执行层映射到 `15m`，比较 funding 结算前 `15m` 入场 vs 即时入场。
- 先看指标：`next 1h/3h realized funding bps`、扣掉双边手续费后的净 carry、排名稳定性（`1d/3d/5d` overlap）。

## 5. 风险与保留意见
- 这轮快检只看 **funding 现金流**，还没扣对冲腿交易成本、basis 偏移和 borrow / inventory 占用。
- repo 数据来自 Hyperliquid 单 venue；若 hedge 放在别处，跨 venue basis 与转仓成本会吃掉一部分 edge。
- 极端负 funding 名单里小币很多，capacity 和冲击成本未审；下一步要先做 liquidity gate，而不是直接把 `top1` 实盘化。

## 6. 来源
- traders-ark. (2026). *hyperliquid-carry-screener*. GitHub.
- Readable URL: `https://github.com/traders-ark/hyperliquid-carry-screener`
- Repo raw snapshot: `https://raw.githubusercontent.com/traders-ark/hyperliquid-carry-screener/main/docs/funding_data.json`
- Repo funding history CSV: `https://raw.githubusercontent.com/traders-ark/hyperliquid-carry-screener/main/funding_data_main.csv`
- Hyperliquid public API used by repo: `https://api.hyperliquid.xyz/info`

## 7. 本地 artifacts
- `reports/artifacts/quant_digests/2026-04-20_hl_funding_carry_rank_summary.csv`
- `reports/artifacts/quant_digests/2026-04-20_hl_funding_carry_rank_events_head.csv`
