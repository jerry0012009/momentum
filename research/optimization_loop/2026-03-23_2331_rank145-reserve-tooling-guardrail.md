# 2026-03-23 23:31 UTC · Rank 145 reserve tooling guardrail

- 严格遵循：`docs/TODO.md` 顶部 `TRADING DESK BOARD`、`docs/AUTO_OPTIMIZATION_LOOP.md`、`docs/BOT2_BOT3_OPERATING_CARD.md`
- 路径判断：`Paper / 待开启自动运行 = empty`；`Paper / 正在自动运行` 未见真实 interrupt，因此本轮路径 = `Scout`
- 认领动作：执行 `Next 3 bot3 runs / Run 1 = interrupt reserve / Rank 145 reserve`

## 本轮只做 1 个主点 + 1 个紧邻子点

### 主点
把这轮刚暴露出来的 `python: command not found` / 更早几轮的 `rg: command not found`，收口成 **bot3 自动执行环境 guardrail**，直接降低后续 reserve 分支继续空耗的概率。

### 紧邻子点
把 guardrail 不只写进文档，还同步写进 **实际 `bot3-momentum-auto-opt-13m` cron payload**，让下一轮就能生效，而不是停留在 repo 注释层。

## 本轮核实的可验证事实
1. `docs/TODO.md` 顶板仍明确：`Run 1 = interrupt reserve / Rank 145 reserve`
2. `cron runs / bot3-momentum-auto-opt-13m` 最近错误回执明确显示：
   - `2026-03-23 23:03 UTC` 左右一轮：`python - <<'PY'` 失败，报错 `/usr/bin/bash: line 1: python: command not found`
   - 更早多轮：`rg -n ...` 失败，报错 `/usr/bin/bash: line 1: rg: command not found`
3. `docs/TODO.md` 顶板与 `2026-03-23_2321_strategy-review.md` 已明确把该类报错定性为：
   - `Rank 145 reserve` 分支命令口径问题
   - **不是** autonomous paper runner 的真实 interrupt
4. 当前最有杠杆的小步，不是再给 `Rank 145` 补一张解释页，而是让下一轮 bot3 少踩一次同样的环境坑。

## 本轮实际交付
### 文档 guardrail 写回
- `docs/AUTO_OPTIMIZATION_LOOP.md`
  - 新增 `运行环境硬约束`：默认使用 `python3`、`grep -RIn` / `find`，不要假设 `python` / `rg`
- `docs/BOT2_BOT3_OPERATING_CARD.md`
  - 新增 `4.1 环境口径（避免空耗）`
- `docs/AUTO_OPTIMIZATION_CRON_PROMPT.txt`
  - 新增同样的环境约束提示

### 实际自动链路修正
- 已更新 cron job `bot3-momentum-auto-opt-13m` 的 payload message：
  - 明确写入 `python3` / `grep -RIn` / `find`
  - 明确写入“不要假设有 `python` 或 `rg`”
  - 明确写入“命令口径错误不等于 `Paper interrupt`”的边界

## 这一步改变了什么
之前 desk 已经知道：
- `Rank 145` 只是 `interrupt reserve fallback`
- 最近一次报错不是 paper 健康异常

但如果不把环境约束写进 bot3 的默认执行口径，下一轮自动循环仍可能：
- 在 reserve 分支里继续写 `python - <<'PY'`
- 或继续把 `rg` 当成默认搜索工具
- 然后再烧掉一轮，用一次新的错误来重复证明“这不是 interrupt”

本轮把这个漏洞补成硬约束后，下一轮的默认工作流更接近：

> 先按 `python3` / `grep -RIn` / `find` 的真实环境落地，再去判断 `Rank 145 reserve` 是否值得继续做最小收口。

## 为什么这一步最有杠杆
这不是研究增量，但它直接改善自动执行链路：
- 减少 reserve 分支无意义报错
- 减少 bot2 反复在 strategy review 里解释“这不是 paper interrupt”
- 让 `Run 1 = interrupt reserve / Rank 145 reserve` 更像一个可连续执行的 fallback，而不是偶发踩环境坑的占位符

## 简短 scorecard
- `usefulness = 3/3`
- `time_stability = 3/3`
- `cross_asset_stability = 3/3`
- `cost_trade_stability = 3/3`
- `deployability = 3/3`
- `recommended_action = keep_P1 / interrupt reserve fallback / reserve only`
- `why_now = 最新 bot3 报错已明确不是研究结论问题，而是环境口径问题；现在修 guardrail，能立刻减少下一轮空耗`
- `main_weakness = 这一步修的是自动执行链路，不是新的策略证据；若未来真出现 interrupt 或 >=8% arm-zone drawdown，仍需基于新样本重估 Rank 145`

## 本轮结论
本轮完成了一个小但真正会影响后续续跑质量的交付：
- 没有把命令口径报错误判成 paper interrupt；
- 没有继续给 `Rank 145` 追加低杠杆解释页；
- 把 `python3 / grep -RIn / find` 的真实环境约束同时写进了文档和实际 cron payload。
