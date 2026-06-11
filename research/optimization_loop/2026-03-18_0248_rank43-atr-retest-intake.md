# 2026-03-18 02:48 UTC — Rank 43 ATR retest zone + bounce reclaim intake：进入下一手 clean replication 队列

## 为什么这次选这个
- 先按 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 与 `Next 3 bot3 runs` 执行。
- `Run 1 / EMA` 仍处于 `running paper / waiting_not_due`：最新 authoritative board 继续指向 A 股 `07:00 UTC`、美股 `20:00 UTC`、Crypto `2026-03-19 00:00 UTC` 的下一次 due 窗口，因此这轮不能把 paper refresh 硬做成主点。
- `Rank 17 / Rank 2 / Rank 29 / Rank 32b` 都已经属于 `P3 narrow paper pilot`，这轮没有新的真实 `append/review need`；当前 `P2 / P1` 也为空。
- 因此按 desk 规则，本轮默认应回到 `Run 2 / fresh paper-repo based 5m/15m crypto intake`。当前 authoritative board 已点名优先候选：`TheVision333/trading-bot / ATR retest zone + bounce reclaim`。

## 本轮主点
- **主点**：把 `TheVision333/trading-bot` 这条 repo-based confirmation 候选做成 authoritative intake-stage hard verdict。
- **紧邻子点**：把结论同步到 `docs/TODO.md` 顶板、quant digest 页面与 source intake card。

## active Scout 边际价值比较
- `P3 continuity`：`Rank 17 / Rank 2 / Rank 29 / Rank 32b` 当前都没有真实 append/review need；按 board 不该继续占默认 Scout 主资源。
- `P2 / P1`：当前为空。
- `fresh intake`：本轮有合格 repo source，因此比直接回退 `Run 3 / tiny-live plumbing` 更有边际价值。
- 在 fresh intake 内部，这条 `ATR retest zone + bounce reclaim` 比当前已 park 的 `Rank 39 / 40 / 41 / 42` 更值得拿主资源：
  - 比 `Rank 39` 更冻结（不是只有 entry idea）；
  - 比 `Rank 40` 更贴 breakout confirmation 主线；
  - 比 `Rank 41 / 42` 更像已经冻结到可执行的 repo 模板，而不是研究语境文献。

## 做了什么
1. 读取并审阅外部 source：
   - `strategy/retest_signals.py`
   - `strategy/market_structure.py`
   - `config.py`
2. 把最小规则翻成当前 desk 可执行口径：
   - `trade on = confirmed swing breakout -> ATR retest zone -> no deep invalidation -> bounce reclaim`
   - `trade off = 无 breakout / 超时 / 深穿 / reclaim 失败`
3. 完成两条轻量诚实守门：
   - `trade on / trade off` 能清楚写成状态机；
   - 当前未见一眼可判死刑的 `lookahead / repaint / data leakage`。
4. 产出本轮 artifacts：
   - `reports/artifacts/literature/scout_rank43_atr_retest_bounce_source_intake_card.csv`
   - `research/quant_digests/2026-03-18_0248_rank43-atr-retest-intake.md`
5. 同步更新：
   - `docs/TODO.md`
   - `research/quant_digests/INDEX.md`

## 关键证据
### 1) 规则不是“看图说话”，而是前向状态机
`retest_signals.py` 已明确冻结：
- breakout candle quality：`body >= 50% range`，long close 在顶部 `30%`；
- retest zone：`<= 0.5 ATR`；
- retest timeout：`20` 根；
- invalidation：若 close 反向穿越突破位超过 `1 ATR`，setup 直接取消；
- 真正 entry：必须等 bounce close 重新站回/压回突破位。

### 2) swing 结构确认至少是因果的
`market_structure.py` 里 swing 高低点只有在 `SWING_LOOKBACK=5` 的右侧 bar 走完后才确认，`add_market_structure()` 用的是 `i-n -> i` 的延迟写入，而不是即画即用的 pivot。

### 3) 当前最诚实结论是“值得 clean replicate”，不是“已经有效”
这条线仍有明显风险：
- repo 原生主时框是 `1h / 4h`；
- 直接压到 `15m` 可能导致交易数变稀或过滤过厚；
- 它更像 confirmation layer，不一定能单独扛 alpha。

所以这轮最诚实 verdict 不是 `paper candidate`，而是：**已经够资格进入下一手最小 clean replication 队列。**

## 硬结论
- **一句话结论**：`Rank 43 / ATR retest zone + bounce reclaim` 当前应记为 **`admit_to_clean_replication_queue`**。
- **为什么不是直接 park**：因为它已通过两条轻量诚实守门，且当前确实比直接回退 `Run 3` 更有边际价值。
- **为什么不是 paper candidate**：因为还没做最小 clean replication，成本后收益、trade count、false-break 改善都还没被回答。

## 后续边界
- 下一轮若继续认领它，默认只允许做 **1 次最小 clean replication**：
  - `BTC / ETH / SOL`
  - `15m signal + 1h HTF`
  - `next-bar open`
  - `no-overlap`
  - 极小 ATR/timeout 邻近参数对照
  - 只先回答 `post-cost return / false-break rate / trade_count / time-pocket honesty`
- 若这一步不干净，就快速压回 `park / evidence pool`；不要继续扩成重型 stability pack。

## 验证
- 本轮未跑重型回测；只做 source intake 与规则冻结检查。
- 已产出 intake card、quant digest，并计划刷新首页 index。

## 提交情况
- 未提交。
- 原因：repo 里存在大量与本轮无关的既有脏文件 / 未跟踪产物；本轮只做 selective write-back，不适合混提。
