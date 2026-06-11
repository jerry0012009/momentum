# 2026-04-17 13:32 UTC — Rank 419 cross-sectional relative-strength × BTC vol/dispersion overlay first verdict（keep_P1）

## 执行小点
- cycle_plan 第 2 项：`research/quant_digests/2026-04-17_0439_regimeaware-xsmomentum-btcvol-overlay.md`
- 动作：fresh intake first-verdict（只执行本小点）

## 结论（改变系统认知）
- 分配正式编号：`Rank 419`
- first verdict：`keep_P1`（进入 Surviving candidate slot）
- 该对象值得保留的主语不是 `BTC realized vol / dispersion overlay`，而是 `liquid-major crypto cross-sectional relative-strength continuation`；overlay 只应视为共享 veto / size-down 层，而不是 alpha 本体。

## 最小 honesty / execution 判定
- 当前唯一 decisive blocker：`short-leg cost`。
- repo 已明确把实现约束收缩到 `long-only top quintile` 与 `long top quintile / short BTC-ETH` 两个更可落地版本，但代码里的默认摩擦已是 `long 10bps / short 20bps`，且作者自己承认 short 侧仍有 funding / borrow scarcity / margin friction 未补齐。
- 在这种口径下，overlay 带来的改进主要表现为 drawdown / Sharpe 的风险整形，而不是证明 `liquid-major` 短腿版本已经形成稳健、可复制的费后 alpha；尤其 `long top quintile / short BTC-ETH` 的 headline absolute Sharpe 仍为负值改善（full sample `-0.475 -> -0.458`，post-2020 `-0.259 -> -0.111`），说明当前最需要确认的不是再换 rebalance cadence 或再抠 turnover，而是 **short leg 收缩到 BTC/ETH 后，统一费率下是否还能留住净边际**。

## 为什么不是 background/P0
- 这份 intake 已把 base alpha、overlay、实现降级版拆得足够清楚：
  1. alpha 本体是横截面强弱排序，不是 generic regime 口号；
  2. overlay 与 alpha 本体边界清晰，没有把 risk layer 冒充新 alpha；
  3. 已给出可 desk 化的最小降级实现（`long-only`、`short BTC/ETH`），因此存在一条明确且便宜的 survivor follow-up 路径。
- 但它也还没有强到可以直接升 `P2`：当前证据仍主要来自 broad-universe / daily-ish 研究框架，尚未在项目固定的 liquid-major desk proxy 上证明 short-leg 费后可存活。

## 本轮回写
- 已更新 `docs/BOT2_BOT3_STATE.md`：
  - Fresh intake slot -> `Rank 419` / `keep_P1`
  - Surviving candidate slot -> 占用 `Rank 419`，`followup_budget_remaining: 1`
  - cycle_plan 第 2 项 -> `status: done` 并写入 result

## 尾部动作
- homepage 刷新：已尝试执行 `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`，本轮进程未返回成功回执并以 `SIGKILL` 结束；按非阻断尾部失败处理，不回滚本轮 verdict / state / log。
- 邮件通知：已发送 `[momentum-bot3-auto] Rank 419首判保留P1`，正文为本日志。

## 下一步（不在本轮执行）
- survivor 唯一 follow-up 应聚焦同一 blocker：把 `long top quintile / short BTC-ETH` 或同等 liquid-major short-leg 收缩版放进统一 desk 成本壳，直接回答 short-leg cost 扣除后是否仍有可复制净边际。
