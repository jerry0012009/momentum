# breakout v0 把 avoid_fluctuating 的 gate 证据正式挂回原型页

## 为什么这次选这个

这轮继续沿 `support_breakout_v0 / breakout-short follow-up` 这条收口线推进，但不新开重回测，而是把一个已经反复被提到、却还没在原型页里量化写死的小问题补完：**如果环境 gate 只先试一个，为什么当前优先看 `avoid_fluctuating`，而不是 `only_downtrend`。**

之所以选这个点：
1. breakout v0 这条线最近已经把成本、split/regime honesty 都收得比较清楚；
2. 页面里虽然一直说“先试 avoid_fluctuating”，但还缺一段直接可见的证据表，容易让这个建议看起来像口头偏好；
3. 现成的 `pytrendline_event_validation_v3_regime_policy_slice_v1` artifact 已经够回答这个问题，不需要重跑下载或重型切片。

## 做了什么改动

1. 更新 `scripts/build_support_breakout_v0_reports.py`
   - 新接入 `reports/artifacts/pytrendline_event_validation_v3_regime_policy_slice_v1/support_breakout_raw_regime_policy_oos.csv`
   - 在 `support_breakout_v0_h24` 原型页新增一段：
     - `如果只先试一个最小环境 gate，为什么当前优先看 avoid_fluctuating？`
   - 这段现在会明确区分：
     - 这是 **event-level OOS gate 对照**，不是这页 v0 策略 PnL 本身；
     - 它只负责回答“哪个 gate 更适合先拿来做最小 follow-up”。
2. 更新 `docs/TODO.md`
   - 在 breakout follow-up 那条收窄任务下补上最新进度说明；
   - 固定写死当前口径：若只做一个最小环境 gate，先试 `avoid_fluctuating`，不是过早切到 `only_downtrend`。
3. 重建可见产物：
   - `reports/site/factors/support_breakout_v0_h24/report.html`
   - `reports/site/plans/momentum_todo.html`

## 验证 / 证据

### 1) 原型页已出现新的环境 gate 证据段

验证命中：
- `reports/site/factors/support_breakout_v0_h24/report.html` 已出现：
  - `如果只先试一个最小环境 gate，为什么当前优先看 avoid_fluctuating？`

这说明本轮结果已经真正落到网站，而不是只留在日志里。

### 2) 当前最关键的数字已经被写死

基于已有 `support_breakout_raw_regime_policy_oos.csv`：

- `avoid_fluctuating`：保留约 `16/19` 个 OOS 事件，retention 约 `84.21%`
- `only_downtrend`：只保留约 `7/19` 个 OOS 事件，retention 约 `36.84%`
- `trade_all`：保留 `19/19`，retention `100%`
- 同一 slice 下：
  - `avoid_fluctuating` 的 OOS mean ret h24 约 `-1.43%`，avg excess 约 `-1.88%`
  - `trade_all` 对应约 `-1.04%` / `-1.55%`

因此当前更诚实的读法是：
- `avoid_fluctuating` 的优势不是“神奇提效”；
- 而是它在 **仍保留大部分 OOS 样本** 的同时，没有比 `trade_all` 明显更钝；
- 相比之下，`only_downtrend` 现在更像过早把样本砍窄。

### 3) TODO 与 plans 镜像已同步

验证命中：
- `docs/TODO.md` 已出现新的 `avoid_fluctuating vs only_downtrend` 进度说明；
- `reports/site/plans/momentum_todo.html` 也已同步出现同样内容。

## 风险 / 边界

1. 这轮补的是 **event-level OOS gate 证据回挂**，不是新策略回测；
2. 因此它不能替代 breakout v0 在 `20bps` / `split` / `regime` 下的真实策略级 PnL；
3. 但它已经足够把“环境 gate 先试谁”这件事从口头建议，推进成网页可见、带数字的 next-step framing。

## 下一步建议

下一步最值得接的是：
1. 真做一版 `breakout v0 + avoid_fluctuating` 在同一 `20bps` 口径下的最小对照；
2. 或继续补 `non-overlap / capital allocation`，看这条 conditional alpha 在更真实执行约束下会不会明显变形。

## Commit

本轮**未提交**。

原因：当前 repo worktree 仍然非常脏，而且 `docs/TODO.md`、`scripts/build_support_breakout_v0_reports.py`、`reports/site/factors/support_breakout_v0_h24/report.html`、`reports/site/plans/momentum_todo.html` 在本轮前就已处于 dirty 状态；此时做 selective commit 仍无法保证只打包本轮改动。
