# 2026-03-15 01:48 UTC · Light Strategy Review

## 本轮一句话判断

这轮的主判断是：**bot3 在“选题重复”这件事上已经明显改善，但顶部接力棒又被推进到 3 条全完成，所以本轮最有杠杆的动作是刷新 TODO 入口层；同时，bot3 当前仍有 timeout 痕迹，按最新经验，若下一轮继续出现执行异常，更该优先考虑 reset bot3，而不是再加提示词限制。**

## 当前 strongest evidence

1. **bot3 已经不再重复重写旧的 ETH+SOL halfsize headline**
   - 最新几条优化记录说明它已经切到了新验证轴：
     - `2026-03-15_0110_ema-ashare-daily-holdout.md`
     - `2026-03-15_0123_breakout-sizing-candidate-selection.md`
     - `2026-03-15_0136_breakout-pure-test-context-honesty.md`
   - 所以当前问题不再是“选题重复”，而更像“旧 baton 已被推进完成，但入口层还没跟上”。

2. **EMA 线已经完成当前这轮最关键的 family 收窄**
   - `A股 daily strict holdout` 已落地：
     - 两格 daily pocket 共 `16` 个 holdout
     - `EMA` 正 holdout 占比约 `62.50%`
     - `PSAR` 约 `43.75%`
   - 其中：
     - `创业板ETF 1d`：`EMA` median net20 约 `12.05%`，高于 `PSAR` 的约 `5.13%`
     - `沪深300ETF 1d`：更像 mixed，但 `EMA` 约 `-2.60%`，仍略好于 `PSAR` 的约 `-4.49%`
   - 当前更诚实的 `EMA baseline family` 口径已经收窄成：
     - `60m crypto` 出局；
     - `A股 weekly` 出局；
     - `A股 daily` 暂时保留，尤其 `创业板ETF 1d` 仍是能替 EMA 守门的 daily pocket。

3. **breakout 线也完成了当前这轮最关键的 candidate selection**
   - `pair-conditioned halfsize` vs `context-conditioned sizing` 的同框架定序已经落地：
     - `pair-conditioned`：
       - overall delta vs gate 约 `+4.44pp`
       - max drawdown 约 `-9.04%`
       - pure-test 条件累计改善约 `+0.76pp`
     - `context-conditioned`：
       - overall delta vs gate 约 `+2.40pp`
       - max drawdown 基本无进一步改善
       - pure-test 条件累计改善约 `+0.08pp`
   - 当前资源顺序已经很清楚：
     - `pair-conditioned` 应保留为 breakout 默认 sizing candidate；
     - `context-conditioned` 更适合降成次级/诊断型分支。

4. **更窄的 breakout pure-test honesty 也已经把次级分支的边界说清楚了**
   - `ETH+SOL @ pure test × up` 只影响约 `3/398` 个活跃小时（约 `0.75%`）
   - overall 只从约 `15.46%` 轻微抬到约 `15.56%`
   - pure-test 条件累计改善仅约 `+0.08pp`
   - 所以这条更窄 context branch 现在更诚实的结论已经是：
     - `late-segment promising, but not worth continuing as a main sizing candidate`

5. **当前新的执行风险不在提示词，而在 bot3 会话状态 / timeout**
   - `openclaw cron list --json` 当前显示：
     - `bot3-momentum-auto-opt-13m` 仍有 `lastRunStatus = error`
     - `lastErrorReason = timeout`
     - `consecutiveErrors = 2`
   - 结合你刚刚给的经验判断，这类症状更该优先怀疑：
     - bot3 上下文空间不够 / 会话状态发散；
   - 因此如果下一轮继续异常，更该优先考虑 **reset bot3**，而不是再加限制 prompt。

## 当前 weakest / should-fix-now

1. **当前最该修的是顶部 relay baton 又 stale 了**
   - 旧 `Current relay baton（2026-03-15 01:05）` 在本轮开始时已经 3 条全打勾；
   - 如果不刷新，bot3 下一轮更容易在已完成项周围继续绕。

2. **当前最不该做的是再继续动 bot3 提示词**
   - 因为选题重复问题已经被拉正；
   - 当前更像会话状态 / timeout 风险，而不是规则边界还不够硬。

## 下一步优先级 Top 1~3

### Top 1. EMA：把 `EMA baseline family` 收成一版更严格的 final survivor map

为什么排第一：
- 因为 EMA 线当前最值钱的，不再是继续补某个 pocket 的单独 slice；
- 而是把 `60m crypto` 出局、`A股 weekly` 出局、`A股 daily` 暂留 这几层结果压成一版真正可执行的 final boundary。

### Top 2. breakout：把 `pair-conditioned halfsize` 推到更严格的 walk-forward / holdout / portfolio honesty

为什么排第二：
- 当前 breakout 主资源应明确回到默认 sizing candidate；
- 不再继续把资源分散在更窄但证据更薄的 context branch 上。

### Top 3. breakout：把更窄的 context branch 正式 park 成诊断型分支，并把资源顺序写死到页面入口

为什么排第三：
- 不是说这条线完全没用；
- 而是它现在已经够清楚地不该继续消耗默认第一资源位。

## 本轮改动

### 1) 已刷新 `docs/TODO.md` 顶部接力棒

把旧的 `2026-03-15 01:05` 版本更新为 `2026-03-15 01:48`，新的未完成 Top 3 变成：
1. `EMA baseline family -> final survivor map`
2. `pair-conditioned halfsize -> 更严格 walk-forward / holdout / portfolio honesty`
3. `context-conditioned branch -> 正式 park + 资源顺序写死`

### 2) 已重建 plans 镜像

执行：
- `python3 /root/clawd/jerry/momentum/scripts/build_plans_site.py`

### 3) 本轮不改 cron / prompt

理由：
- 选题重复问题已经改善；
- 当前更像 bot3 会话状态 / timeout 风险；
- 若继续异常，下一步更该考虑 reset，而不是继续改提示词。

### 4) 本轮不改 `ROADMAP.md`

理由：
- 没有新的项目级方向漂移；
- 这轮更像入口层刷新。

## 网页 / 表达建议

1. **当前不需要继续堆更多 breakout first-pass 文案**
   - pair-vs-context 的定序已经够决策；
   - 现在应把主资源集中到 pair-conditioned 的更严复核。

2. **EMA 页下一步不该继续停在单个 A股 pocket 上，而该开始收 final survivor map**

3. **若要在 breakout 页继续更新，优先做“pair-conditioned 默认候选”的更严复核页，而不是再给 context branch 单独加新说明**

## cron / 节奏建议

1. **bot3-momentum-auto-opt-13m：本轮先不改频率、不改 prompt**
   - 但要重点盯 `timeout`；
   - 若下一轮仍继续报错，按新经验优先考虑 reset bot3。

2. **bot2-strategy-review-40m：继续保持**
   - 本轮 bot2 最正确的动作是：
     - 刷新 baton；
     - 不再叠加提示词治理。

3. **下一轮 bot2 的观察点**
   - 只看：
     1. bot3 是否开始做 `EMA family final survivor map`；
     2. 或是否把 breakout 主资源切回 `pair-conditioned` 的更严复核；
     3. 以及 bot3 是否继续 timeout / 需要 reset。

## 风险与不确定性

1. bot3 当前 `timeout` 痕迹仍在；这轮没直接处理，只是明确了优先处置思路。
2. `EMA baseline family` 虽已大幅收窄，但 final survivor map 还没真正收口成一句固定口径。
3. breakout 的 `pair-conditioned halfsize` 仍只是默认候选，不等于已通过严格 walk-forward / holdout 验证。
