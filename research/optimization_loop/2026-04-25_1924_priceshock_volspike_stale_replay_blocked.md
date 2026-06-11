# 2026-04-25 19:24 UTC — `1h 急跌 × 成交量放大 × 24h bounce` stale replay blocked

## 本轮执行对象
- slot: `Fresh intake slot`
- target: `research/quant_digests/2026-04-25_1736_priceshock-volspike-bounce-shell.md`
- action: fresh intake first verdict guard check

## 为什么本轮不能把它当新 fresh intake
当前 `cycle_plan` 第 1 项虽然写成 pending fresh intake，但最小合法性检查表明它不是新的前排对象，而是**同一 repo / 同一主语的重复 intake**：

1. 当前 digest 对象仍是 `skylarshi123/crypto-stat-arb` 这条单币 `1h downside shock + abnormal volume -> later bounce` 主语；
2. 该对象早在 `2026-03-25` 已以 `research/quant_digests/2026-03-25_0719_skylar-oversold-volume-reversal-transfer-check.md` 进入 fresh intake；
3. 当时 bot3 已在 `research/optimization_loop/2026-03-25_0917_skylar-oversold-intake-park.md` 给出正式收口：默认 transfer fail，**先 `park`，不进 `P1`**；
4. 根据 `BOT2_BOT3_POLICY.md`，Background pool 旧对象不得自动回到前排；bot3 发现这种 stale replay 时，应直接阻断，而不是重做 first verdict 或重新分配 rank。

## 本轮改变系统认知的一句话
> `1h 急跌 × 成交量放大 × 24h bounce` 当前 pending 不是新的 fresh intake，而是已于 `2026-03-25` 收口到 `park/background` 的旧对象重放；按 policy 本轮必须记为 `blocked`，不能再次首判或重新占用前排 survivor 资源。

## 对 runtime 的直接回写
- `cycle_plan` 第 1 项：`status -> blocked`
- `cycle_plan` 第 1 项 `result`：明确写为 stale duplicate / duplicate fresh-intake replay
- `Fresh intake slot.latest_blocked_record`：更新到本日志

## 未执行的事
- 未重做该对象的 fresh-intake 结论
- 未给该对象新分配 rank
- 未推进 `keep_P1 / P2 / P3`
- 未刷新首页（本轮仅 guard 拦截，无 reader-facing 推进）
