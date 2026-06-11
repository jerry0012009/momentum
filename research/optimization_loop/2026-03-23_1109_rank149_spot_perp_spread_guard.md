# 2026-03-23 11:09 UTC — Rank 149 / spot-perp spread mean reversion raw alpha 守门

## 本轮路径
- Path: `Scout`
- 来源：`docs/TODO.md` 顶板 `Run 2 = 下一条 fresh intake / raw-alpha reserve 守门`
- 触发原因：`Rank 148` 已在 10:58 UTC 完成 follow-up 并 authoritative `park`，本轮应切到下一条 fresh intake。

## 本轮只做的一小步
把最新 fresh intake **spot-perp spread mean reversion** 从“也许只是 basis/funding overlay”推进到一个更可执行的 desk 结论：

> **给它新 rank：`Rank 149`，并先升到 `P2 / promote_P2 / fresh intake admitted`。**

这不是在说它已经 ready for paper；只是说明它已经值得占据下一轮 bot3 的主 Scout 资源位，去做最关键的成本诚实检查。

## 主点（本轮唯一主判断）
### `Rank 149 / spot-perp spread mean reversion raw alpha`
**结论：应当作为独立 `raw alpha` 家族进入 active Scout，而不是继续只当 overlay。**

### 依据（来自 2026-03-23 11:05 quant digest + 本地产物）
- 研究对象：同标的 `spot vs perp` spread 回归，定义为 `(perp - spot) / spot`。
- 本地快检样本：`BTC/ETH/SOL`，近 `927` 根 `5m` bar。
- 极端偏离后的下一根回归概率：
  - `BTC`: `z > 1.5` 时压缩概率 `85.2%`；`z < -1.5` 时向上回归概率 `83.1%`
  - `ETH`: `90.9% / 89.0%`
  - `SOL`: `89.2% / 80.2%`
- 粗糙 gross toy strategy（`entry=|z|>1.5`, `flat=|z|<0.25`）样本内累计：
  - `BTC ≈ +125.1 bps`
  - `ETH ≈ +125.8 bps`
  - `SOL ≈ +148.0 bps`
- 核心意义：
  - 它有 **独立 alpha 骨架**（entry / exit / pairing / sizing / margin / risk），不是单纯给已有 breakout 家族加 veto。
  - 它天然补足 desk 目前最缺的 `relative-value / stat-arb / basis-carry` raw-alpha 支线。

## 紧邻子点（只推进 1 个）
### 下一刀必须是什么
**不是**再加故事、再补 literature、再做更花的预测器；
**而是**直接补：
- `post-cost`
- `funding`
- `spot-leg friction`
- `capital tie-up / margin usage`

如果这四个约束一上就把 edge 吃光，它应回落到 `keep_P1` 甚至 `park`；
如果成本后仍站得住，才有资格讨论 `P3 / Paper launch queue`。

## 本轮 scorecard（简短）
- `novelty to desk`: `A`
- `reader-facing clarity`: `A-`
- `raw-alpha independence`: `A`
- `gross evidence`: `B+`
- `cost honesty`: `D`（还没补，所以下一轮必须做）
- `paper readiness now`: `C-`
- **authoritative verdict now**: `P2 / promote_P2 / next run must do honesty cut`

## 已写回 authoritative 顶板
本轮已更新 `docs/TODO.md`：
1. `Active Scout` 顶部新增 `Rank 149`
2. `Next 3 bot3 runs` 的 `Run 1` 改为 `Rank 149` 的成本诚实检查
3. `Recent evidence` 新增本轮守门结论

## 可验证产物
- Quant digest：`research/quant_digests/2026-03-23_1105_spot-perp-spread-mean-reversion-raw-alpha.md`
- 本地产物目录：`reports/artifacts/quant_digests/spot_perp_spread_mr_20260323/`
- 更新文件：`docs/TODO.md`

## 下轮 handoff
下一轮 bot3 只做这一刀：

> 对 `Rank 149` 跑最小 `post-cost + funding + spot-leg friction + capital tie-up` 诚实检查，直接回答：`P3` 还是回落。
