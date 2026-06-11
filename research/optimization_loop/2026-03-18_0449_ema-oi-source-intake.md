# 2026-03-18 04:49 UTC — OI participation gate source intake

## 为什么这次选这个
- 先按顶板重读 `Run 1 -> Run 2 -> Run 3`：
  - `Run 1 / EMA` 当前仍是 **`running paper / waiting_not_due`**，没有新的 due-now / overdue refresh；
  - `Rank 17 / Rank 2 / Rank 29 / Rank 32b` 这些 `P3 narrow paper lane` 继续由专属 cron / 最小 monitoring 托管，当前没有新的 append/review 状态变化；
  - `Rank 43`、`Rank 40`、`Rank 44 / BotScalpingTwinRange`、`Rank 27b`、`FibTrend-Pro` 都已在各自允许预算内给出 hard verdict 并压回 `park / evidence pool`。
- 因此本轮默认落到 `Run 2 / Scout Fast Lane`，并且必须先比较当前 active fresh Scout 候选的边际价值。
- 这轮实际比较的是：`Rank 46 / OI participation gate`、`Rank 47 / EMA-ADX-VOL skeleton`、`Rank 35b`。
- 当前更高边际价值的主资源位是 **`Rank 46 / 15m-EMA-9-15-OI-Flip-Signals / OI participation gate`**：
  - 它比 `Rank 47 / EMA-ADX-VOL skeleton` 更窄，不重写 entry，只先回答一件当前真正会改 desk judgment 的小问题：`OI > OI-SMA20` 能不能在 **不明显砍掉 trade count** 的前提下压低 `2~4 bar whipsaw`；
  - 它比 `Rank 35b` 更优先，因为前者是 fresh repo-based 15m source，后者仍是 derived fallback；
  - Binance 公共 OI 接口直接支持 `15m`，所以这条线更容易拿到诚实的最小 clean replication verdict。

## 这轮做了什么
### 主点
- 把 `Rank 46 / OI participation gate` 从“仅有 quant digest 线索”推进到 **`source intake / honesty gate passed`**。
- 新增 artifact：
  - `reports/artifacts/literature/scout_repo_ema_oi_participation_source_intake_card.csv`
  - `reports/site/reading/repo_scout/ema_oi_participation_source_intake.html`

### 紧邻子点
- 最小改写 `docs/TODO.md` 顶部 authoritative board，在 `Next 3 bot3 runs` 处补写 `2026-03-18 04:49 UTC` 的新边际价值比较与回退顺序：
  - **`OI participation gate > EMA-ADX-VOL skeleton > Rank 35b > Run 3 / tiny-live plumbing`**
- 同时把它的当前定位冻结成：
  - **`P1 weak candidate（source intake / 两条轻量诚实守门已过）`**
  - **`guard-passed / admit_to_clean_replication_queue`**

## 验证 / 证据
- 本轮没有重跑重型 clean replication，只做 source-intake / honesty-gate 这一步应做的小而完整切片。
- 两条轻量诚实守门已冻结成可执行口径：
  1. **`trade on / trade off` 清楚可写**
     - 方向仍由 `EMA 9/15`（或后续复用 `EMA / PSAR` baseline）负责；
     - `OI > SMA20(OI)` 只负责回答“这次 15m 动作是否值得执行 / 加权”；
     - 若 EMA 未同向，或 OI 未高于短均值，则不交易 / 不加权。
  2. **未见一眼可判死刑的 `lookahead / repaint / leakage`**
     - repo 中 buy / sell 共用同一个 OI 条件，说明它更像 participation gate，而不是方向预测器；
     - 当前最大的诚实风险不是未来函数，而是 repo 在 OI 缺失时会 fallback 到 `volume`，因此下一轮 clean replication 必须把 `true OI` 与 `volume fallback` 分 bucket，不得混算。
- 本轮最小文件存在性检查已通过：
  - `ok_csv`
  - `ok_html`
- `docs/TODO.md` 已成功写回 `04:49 UTC` authoritative 补充。

## 当前硬结论
- **`OI participation gate = guard-passed / admit_to_clean_replication_queue`**
- 它当前比 `Rank 47 / EMA-ADX-VOL skeleton` 更值得先拿下一轮 budget，不是因为它更完整，而是因为它更像一条**单轴 participation 过滤层**，能更快回答当前 desk 的小而关键问题：
  - 能不能在不明显砍样本的前提下压低 `2~4 bar whipsaw`。
- 因此当前最诚实的 Scout 回退顺序应是：
  - **`OI participation gate > EMA-ADX-VOL skeleton > Rank 35b > Run 3 / tiny-live plumbing`**

## 风险 / 边界
- 这轮还不是 clean replication，更不是 `paper candidate`；只是把它从 digest 线索推进到可执行队列。
- OI 上升不等于方向标签；上涨时 OI 升可能是新多， 下跌时 OI 升也可能是新空。方向仍必须让价格规则来定。
- Binance `openInterestHist` 公开窗口较短，因此下一轮若最小 replication 有信号，再讨论是否值得补日常抓取与更长窗 OOS；这一轮不提前扩写。

## 下一步建议
1. 若下一轮 `EMA` 仍是 `waiting_not_due`，默认只给这条线 **1 次最小 clean replication**：
   - `BTC/ETH/SOL 15m`
   - `next-bar open + no-overlap`
   - 四臂：`raw EMA(or EMA+PSAR)`、`+oi_level_gate`、`+oi_level_gate+oi_delta_gate`、`+volume_fallback_gate`
2. 最先回答四个便宜问题：
   - `4/8/12 bar follow-through`
   - `2~4 bar whipsaw ratio`
   - `net expectancy @ 6/10bps`
   - `trade_count retention`
3. 若它不能在不显著砍样本的前提下压低 whipsaw，就快速压回 `park / evidence pool`；不要继续磨 source-intake wording。

## Commit hash
- 未提交。
- 原因：当前 git 工作区存在大量与本轮无关的脏文件 / 未跟踪文件；本轮不安全混提。
