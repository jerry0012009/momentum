# Rank 354 — BTC crowd-positioning fuel-cascade survivor follow-up: background / P0

- Time: 2026-04-07 05:10 UTC
- Object: `Rank 354 / BTC crowd-positioning fuel-cascade`
- Action type: surviving candidate only follow-up
- Verdict: `background / P0`

## Why this changed system belief
这轮不是重读 README，而是回答 survivor 唯一该答的 decisive 问题：
**`PB14-L / PB12 / FLIQ-L` 里是否至少有一个分支，已经被独立证据推进到“在诚实 fee / slippage / funding 口径下仍保留最小可迁移净边”？**

最小独立复核结果是否定的。

### 1) 当前公开 repo 结构不足以支撑 code-audited 结论
对 `https://api.github.com/repos/iZonex/trading-strategy/contents` 的直接检查显示，repo 当前公开内容只有：
- `README.md`
- `figures/`

也就是说，当前并没有公开的：
- 策略实现代码
- 参数文件
- 交易明细 / trade blotter
- 独立回测脚本
- 可复跑的 after-cost ledger

因此，`PB14-L / PB12 / FLIQ-L` 三个分支目前都仍停留在 **source-asserted README research monograph** 层，而不是 **code-audited / independently reproducible** 层。

### 2) 三个分支都只有规则叙事，没有可审计净边证据
README 确实把三个分支的规则、口径和自报绩效写得很清楚：
- `PB14-L`：极端 short crowd + quiet barrel -> squeeze long
- `PB12`：拥挤多头 first-weakness -> cascade short
- `FLIQ-L`：OI flush deceleration + price near low -> 24h bounce

但当前我们真正需要的不是“规则写得像不像一条策略”，而是：
- 是否存在独立复算结果；
- 是否能审计 fee/slippage/funding 之后的净边；
- 是否能区分 README 里声称的 edge 与图表/样本展示 bias。

这三点目前都没有公开材料支撑。

### 3) survivor 预算只允许一次高杠杆 follow-up；这次已经把唯一 blocker 答完了
`Rank 354` 在 first verdict 阶段被保留，不是因为相信 README 收益，而是因为它有独立 raw alpha 主语：
`public crowd positioning + OI -> squeeze / cascade / forced-liquidation fuel state`

但 survivor 槽位只给一次便宜而 decisive 的 follow-up。
这次 follow-up 已经直接回答：
- 不是“edge 被独立保住了”；
- 而是“当前仍只有 README + figures，尚无任何一个分支被推进到可审计 after-cost 层”。

因此本轮必须收口，不能继续让它占用前排等待更多抽象复核。

## Final verdict
**结论：`Rank 354` 不升 `P2`，直接回 `background / P0`。**

不是因为主语不存在，而是因为在 survivor 唯一 follow-up 里，
**没能证明 `PB14-L / PB12 / FLIQ-L` 至少有一个分支拥有可独立审计、成本后仍成立的最小可迁移净边。**

在当前 policy 下，这已经足够触发前排退出。

## Runtime consequence
- `Surviving candidate slot` 清空为 `none`
- `followup_budget_remaining` 归零
- `Background pool` 更新为最新 parked 对象：`Rank 354`
- `cycle_plan` 第 1 项标记为 `done`

## Evidence used
- Prior intake record: `research/optimization_loop/2026-04-07_0259_rank354_positioning_fuel_cascade_intake_keep_p1.md`
- Source digest: `research/quant_digests/2026-04-06_1134_btc-positioning-fuel-cascade-alpha.md`
- Repo README raw: <https://raw.githubusercontent.com/iZonex/trading-strategy/main/README.md>
- Repo contents API: <https://api.github.com/repos/iZonex/trading-strategy/contents>

## Reader-facing implication
这条线仍可留在背景池，未来若出现以下任一新增证据，才值得人工 reopen：
- 公开代码或 notebook
- 可审计 trade blotter / ledger
- 独立复算证明确有成本后净边
- 明确展示 `fuel exit` 在独立样本里优于普通 trailing 的可复现结果

## Delivery notes
- `BOT2_BOT3_STATE.md` 已写回。
- 中文邮件摘要已发送。
- 首页刷新脚本已执行到发布阶段，但当前 cron 运行态无 elevated 权限，`publish_homepage_index.sh` 在 `sudo mkdir/install/chown` 步骤无法完成，因此本轮 reader-facing 首页未真正同步到 `/var/www/momentum-report/index.html`。
