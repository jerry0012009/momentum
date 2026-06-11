# Rank 225 / Deribit option volume shock × OTM directional gate：survivor follow-up 收口为 keep_P1 后转 background

- 时间：2026-03-28 16:26 UTC
- 对象：`Rank 225 / Deribit option volume shock × OTM directional gate`
- 来源：`research/quant_digests/2026-03-28_1403_deribit-option-volume-shock-otm-flow-gate.md`
- 轮次类型：bot3 auto optimization
- 结论：`keep_P1 后转 background`

## 这轮做了什么
按 `cycle_plan` 的唯一合法 survivor follow-up，直接用公开 recent/live 数据做最小 after-cost A/B：

1. **信号侧**：Deribit `public/get_last_trades_by_currency` recent BTC option trades；排除 combo trade；
2. **元数据侧**：Deribit `public/get_instruments`；
3. **执行腿**：BTCUSDT 公开 K 线；
4. **对照组**：
   - `volume shock only`
   - `volume shock + dir_z`
   - `volume shock + dir_z + volinfo veto`
5. **口径**：
   - `15m` 为主，持有 `4 bars`（1 小时）
   - `5m` 为辅，持有 `12 bars`（同样 1 小时）
   - round-trip 总成本先按 **12 bps** 保守扣减

这轮没有做新的主题扩写，而是只回答一件事：**direction gate 相对裸 `volume shock` 有没有留下最小独立净增益。**

## 方法备注（为什么这轮够做 survivor 收口）
这是 public-only 的 recent/live 最小实验，不是完整 production replication：

- Deribit 公开 recent trades 足够做这轮 survivor 的“是否值得继续前排占资源”判断；
- 短期限 `OTM/DOTM` 过滤因为 public recent 侧没有直接下发完整 greeks，这轮先用 **到期日 + strike 相对 index_price 的 moneyness 近似** 来做短期限 OTM/DOTM 桶；
- 这个近似足以做 `keep_P1` vs `promote_P2` 的预算判断，但**还不够**支撑更重的 admission 级别承诺。

所以，本轮的门槛不是“把 paper 完整复刻到论文精度”，而是“用最小诚实 recent/live A/B 判断它值不值得继续留在前排”。

## 结果摘要
### 15m 主口径（约近 14 天 recent/live）
- 可用 option trades：`7,649`
- 聚合后 bars：`97`
- 有 short-dated OTM/DOTM gate 流的 bars：`65`
- `volshock` 基础触发 bars：`2`

#### after-cost A/B
- `volume shock only`
  - 触发数：`2`
  - 成本后平均净收益：`-20.21 bps`
  - 中位数：`-20.21 bps`
  - 胜率：`0.00`
- `volume shock + dir_z`
  - 触发数：`2`
  - 成本后平均净收益：`-20.21 bps`
  - 中位数：`-20.21 bps`
  - 胜率：`0.00`
  - long：`1` 次，平均 `-36.41 bps`
  - short：`1` 次，平均 `-4.02 bps`
- `volume shock + dir_z + volinfo veto`
  - 触发数：`2`
  - 成本后平均净收益：`-20.21 bps`
  - 中位数：`-20.21 bps`
  - 胜率：`0.00`
  - long：`1` 次，平均 `-36.41 bps`
  - short：`1` 次，平均 `-4.02 bps`

### 5m 辅口径（约近 5 天 recent/live）
- 可用 option trades：`7,642`
- 聚合后 bars：`289`
- 有 short-dated OTM/DOTM gate 流的 bars：`104`
- `volshock` 基础触发 bars：`5`

#### after-cost A/B
- `volume shock only`
  - 触发数：`2`
  - 成本后平均净收益：`-17.30 bps`
  - 中位数：`-17.30 bps`
  - 胜率：`0.50`
- `volume shock + dir_z`
  - 触发数：`1`
  - 成本后平均净收益：`-42.49 bps`
  - 中位数：`-42.49 bps`
  - 胜率：`0.00`
  - long：`1` 次，平均 `-42.49 bps`
  - short：`0` 次
- `volume shock + dir_z + volinfo veto`
  - 触发数：`1`
  - 成本后平均净收益：`-42.49 bps`
  - 中位数：`-42.49 bps`
  - 胜率：`0.00`
  - long：`1` 次，平均 `-42.49 bps`
  - short：`0` 次

## 本轮判断
这轮不能把 `Rank 225` 升到 `P2`。

原因很直接：

1. **在这轮 public recent/live 最小实验里，`direction gate` 没有相对裸 `volume shock` 留下独立净增益。**
   - `15m` 主口径里，三组 A/B 结果基本一样，说明 `+dir_z` 与 `+volinfo veto` 没有把结果往上推；
   - `5m` 辅口径里，反而是 gated 版本更差，而且样本更稀。
2. **触发本身偏稀，意味着它现在更像“主题上值得记住的结构线索”，而不是已经证明值得进 admission 的前排对象。**
3. **这轮 survivor follow-up 的任务已经完成了。** policy 要的是用最便宜、最诚实的一次检查做收口；现在答案已经够明确：这条线还没证明自己值得继续占用 survivor / P2 资源。

## 会改变系统认知的话
`Rank 225 / Deribit option volume shock × OTM directional gate` 在 public recent/live 的同口径 after-cost A/B 中，没有证明 `+dir_z` 或 `+volinfo veto` 相对裸 `volume shock` 留下独立净增益；其中 `15m` 主口径仅 2 次基础触发且三组都为负、`5m` gated 版本更差，因此这条 survivor 本轮不升 `P2`，按预算收口为 `keep_P1 后转 background`。

## 为什么不是 promote_P2
`promote_P2` 至少要看到一点像样的 admission-worthy 迹象：
- 要么 `15m` 主口径已经有正的 after-cost 粗边；
- 要么 direction gate 明确改善裸 `volume shock`；
- 要么虽然样本稀，但 gated 版本至少表现出“更少但更好”的苗头。

这轮三个条件都没看到。

## 为什么也不是 drop
它仍保留 `keep_P1` 而不是直接 `drop`，是因为：
- 论文拆法本身仍有启发性；
- public API 路径真实存在；
- 若未来有更 faithful 的 delta/moneyness 历史、或更长 recent/live 录制，仍可能重新检查。

但那已经不该继续占当前前排 survivor 预算了，所以本轮把它**转回 background**。

## runtime 应如何回写
- `Surviving candidate slot`：清空为 `none`
- `followup_budget_remaining`：归零
- `Background pool.latest_parked`：写入本轮 verdict
- `cycle_plan[1]`：
  - `result` = `Rank 225 / Deribit option volume shock × OTM directional gate` 在 public recent/live 的同口径 after-cost A/B 中没有证明 direction gate 相对裸 volume shock 留下独立净增益，因此本轮不升 P2，按预算收口为 keep_P1 后转 background
  - `status` = `done`
