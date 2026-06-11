# EMA rolling / OOS honesty 完成态同步（把开放任务收成明确 deployment verdict）

- 时间：2026-03-15 15:26 UTC
- 主点：`EMA / PSAR raw alpha focus`
- 紧邻子点：`docs/TODO.md` / plans 入口同步 EMA baseline family 的最终 honesty 边界

## 为什么这次选这个

先检查了 repo 状态、最近几轮自动优化记录，以及 `docs/TODO.md` 当前未完成项。

最近几轮 EMA 已连续补到：
- `candidate spec`
- `operating spec`
- `monitoring board`
- `runbook`
- `day-0 checklist / ledger / snapshot / first-refresh queue`

与此同时，`EMA raw alpha baseline` 的 rolling / OOS / 跨市场稳定性证据其实也已经陆续补齐：
- `Crypto 60m rolling falsification`
- `A股 frontier rolling`
- `A股 daily strict holdout`
- `A股 weekly strict holdout`
- `final survivor map`

但 `TODO.md` 里仍留着两条相关开放项，容易让后续自动轮继续误以为“EMA 的 rolling/OOS honesty 还没做完”，从而继续掉回近义 wording / protocol 补丁。按当前 steering，这一轮更应该做的是：**把已经完成的 honesty 工作收成明确 verdict，并同步到 deployment-facing 入口**，而不是再新增一层 EMA board 页面。

## 做了什么改动

### 1) 更新 `docs/TODO.md`

本轮把两条已经实质完成的 EMA honesty 任务改成 `[x]`：

1. `为 EMA raw alpha baseline 增补 rolling / OOS honesty 检查`
2. `优先补 EMA 的成本 / rolling / OOS / 跨市场稳定性，让它真正有资格当 raw alpha baseline`

并补上完成态口径：
- `Crypto 60m = fail`
- `A股 weekly = remove / PSAR-lean`
- `沪深300ETF 1d = mixed / watch`
- `创业板ETF 1d = daily survivor`
- `美股 / crypto / 茅台 1d+1wk = secondary backstop`

重点不是把 EMA 吹成“全市场都稳”，而是把它收成一句 deployment-facing 的诚实边界：
**现在已经足够回答“哪部分还能拿去 paper、哪部分必须排除”。**

### 2) 刷新 plans 站点镜像

执行：
- `python3 scripts/build_plans_site.py`

结果：
- `reports/site/plans/momentum_todo.html` 已同步反映上述 `[x]` 状态与完成态说明。

### 3) 刷新并发布首页 index

执行：
- `bash scripts/publish_homepage_index.sh`

结果：
- 首页索引已发布，Jerry 从站点入口就能看到本轮最新记录时间戳。

## 验证 / 证据

已完成最小必要验证：
1. `python3 scripts/build_plans_site.py`
2. `bash scripts/publish_homepage_index.sh`

验证结果：
- `reports/site/plans/momentum_todo.html` 已成功重建；
- `reports/site/index.html` 与线上首页 index 已刷新；
- `TODO.md` 中 EMA rolling/OOS 相关开放项已改为完成态，并带上最终 honesty 边界说明。

## 本轮结论（给 Jerry）

这轮没有再给 EMA 线加新 protocol / board，而是把已经完成的 rolling / OOS honesty 工作正式收口。

当前更诚实的项目级判断是：
- EMA 之所以仍是 `closest to paper`，不是因为它“全市场无敌”，而是因为它已经有了清楚的 keep / watch / remove 边界；
- 能继续往 paper/shadow 走的是收窄后的 baseline family，不是整个 EMA universe；
- 因此后续 EMA 线默认应沿已落地的 `day-0 snapshot + first-refresh queue` 往前跑，而不是再重复补“EMA 到底要不要 rolling/OOS”这类已解决问题。

## 风险 / 边界

- 本轮没有新增 forward 数据，也没有新增持仓级结果；
- 做的是 deployment-facing verdict sync，而不是新的 alpha 证据生产；
- `把 EMA 作为结构层默认 baseline 去对比增量价值` 这条任务仍未完成，后续若继续做结构层比较，仍值得保留。

## 下一步建议

优先顺序应保持：
1. EMA：沿 `first-refresh queue` 做真实 refresh / week-1 review，而不是继续补近义页面；
2. breakout：只有出现新的 `pure-test / down-tail` forward honesty，才值得重回 admission 主线；
3. 结构层若继续推进，应显式回答“是否稳定优于 EMA baseline”。

## Git hygiene / 提交说明

- 本轮开始前，`git status --short` 已显示大量与本轮无关的脏改和未跟踪文件；
- 本轮只改了 `docs/TODO.md`，并重建 plans / index；
- 为避免把 breakout、历史 artifact、缓存和其他研究线的改动混进来，本轮未提交 commit。

## Commit hash

- 未提交。
