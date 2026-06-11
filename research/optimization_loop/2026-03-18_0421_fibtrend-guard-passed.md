# 2026-03-18 04:21 UTC — FibTrend-Pro 两条诚实守门通过，进入最小 clean replication 队列

## 本轮为什么选这个
- 先读 `docs/TODO.md` 顶部 `TRADING DESK BOARD` 后，`Run 1 / EMA` 当前仍是 `running paper / waiting_not_due`，没有新的 `due-now / overdue` lane。
- 当前 `P3` 的 `Rank 2 / Rank 17 / Rank 29 / Rank 32b` 继续由专属 refresh / monitoring 托管，没有新的 `append/review` 状态变化。
- `Rank 43`、`Rank 40`、`Rank 44 / BotScalpingTwinRange`、`Rank 27b` 都已在允许预算内给出 hard verdict 并压回 `park / evidence pool`。
- 因此这轮按顶板顺序落到 `Scout Seat`，且应优先认领 `04:08 UTC` 新出现的 fresh repo source：`Rank 45 / FibTrend-Pro / Fib 0.618 reclaim + volume>SMA24 + SMA200/EMA trend gate`，而不是直接跳去 `Rank 35b` 或回头磨 `P3 continuity`。

## 本轮主点
- 只做 `FibTrend-Pro` 的两条轻量诚实守门：
  1. 规则能否清楚写成 `trade on / trade off`
  2. 是否有明显 `lookahead / repaint / data leakage`

## 做了什么改动
1. 新增 source-intake 生成脚本：
   - `scripts/build_repo_fibtrend_source_intake.py`
2. 生成 deployable artifact：
   - `reports/artifacts/literature/scout_repo_fibtrend_confirmation_source_intake_card.csv`
3. 生成 reader-facing 页面：
   - `reports/site/reading/repo_scout/fibtrend_confirmation_source_intake.html`
4. 将本轮 verdict 写回 `docs/TODO.md` 顶部 desk board：
   - 新增 `2026-03-18 04:19 UTC` 补充，明确 `FibTrend-Pro = guard-passed / admit_to_clean_replication_queue`
   - 更新 `Next 3 bot3 runs` 当前窗口排班为：
     - `Rank 45 / FibTrend-Pro minimal clean replication > Rank 47 / EMA-ADX-VOL skeleton > Rank 35b > Run 3 / tiny-live plumbing`
5. 重建 reader-facing desk 页面：
   - `python3 scripts/build_todo_page.py`
   - 输出：`reports/site/plans/momentum_todo.html`

## 这轮两条守门的硬结论
### 1) `trade on / trade off`：通过
- 共享核心已经能冻结成：
  - `trade on` = `close` 重回 rolling-50 bar 的 `Fib 0.618` 强侧 + `volume > SMA(volume, 24)` + `close > SMA200`
  - `ATR` 版本再额外加 `EMA9 > EMA26` 作为 continuation confirm
- `trade off` 也能直接写清：
  - 价格没站回 `Fib 0.618`
  - volume 不过 `SMA24`
  - `close <= SMA200`
  - 或 ATR 版本里 `EMA9 <= EMA26`
  - 若 `close < Fib 0.5`，setup 直接失效/退出

### 2) `lookahead / repaint / leakage`：未见一眼判死刑的问题，但 replication 必须收紧执行口径
- 从源码结构看，`Fib / SMA / EMA / ATR / volume` 都是 trailing 计算，当前没看到明显未来函数。
- 但原 Pine 默认是 bar-close 条件判断；同时 rolling `highest/lowest(50)` 会包含当前 bar。
- 这不等于直接 lookahead，但如果 replication 不强制 `next-bar open + no-overlap`，就容易把“当前 bar 才确认的条件”和“同一 bar 乐观成交”混成一件事。
- 所以下一轮的 clean replication 必须把这条执行边界钉死，而不能照抄 TradingView 默认回测口径。

## 当前 hard verdict
- **`FibTrend-Pro = guard-passed / admit_to_clean_replication_queue`**
- 更直白地说：
  - 它通过了 source-intake 阶段的两条轻量诚实守门；
  - 值得拿 **1 次最小 clean replication** 预算；
  - 但它仍只是 repo skeleton，不是已验证 alpha；
  - 如果下轮最小 replication 后，成本/交易数/false-retest 仍不诚实，就应快速压回 `park / evidence pool`。

## 对下一轮排班的影响
- 当前默认顺序收紧为：
  1. `Run 1`：只看 `EMA` 是否出现新的 due-now / overdue
  2. `Run 2`：`FibTrend-Pro minimal clean replication`
  3. 若这条线最小 replication 硬 fail，再回退比较 `EMA-ADX-VOL skeleton > Rank 35b > Run 3`
- 这意味着下一轮不该再重复 source-intake 文案，也不该提前回头认领 `Rank 35b`。

## 验证 / 证据
- 外部证据核对：
  - README：明确写了 `Fib 0.618/0.5 + volume>SMA24 + SMA200`，且承认高周期 `4H/1D/1W` 更可靠
  - `FibTrend_ATR.pine`：额外出现 `EMA9 > EMA26`、`ATR` 止损止盈与 trailing 退出
- 本地验证：
  - `reports/artifacts/literature/scout_repo_fibtrend_confirmation_source_intake_card.csv` 已生成
  - `reports/site/reading/repo_scout/fibtrend_confirmation_source_intake.html` 已生成
  - `reports/site/plans/momentum_todo.html` 已重建
  - `docs/TODO.md` 顶部已写回 `04:19 UTC` verdict 与新的 run order

## 风险 / 边界
- 这轮没有偷跑 clean replication，也没有把 `FibTrend-Pro` 直接升成 `P2/P3`。
- README 明说它更偏高周期，所以 15m 上更像确认层骨架，不应被误写成现成主信号。
- 当前 workspace 仍有大量与本轮无关的脏文件，因此不做混合提交。

## Commit
- 未提交。
- 原因：工作区存在大量与本轮无关的脏文件 / 未跟踪文件，当前不适合安全 selective commit。
