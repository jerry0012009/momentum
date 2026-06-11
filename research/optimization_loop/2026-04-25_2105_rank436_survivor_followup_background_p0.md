# Rank 436 survivor 唯一 follow-up：1h parent × 15m child / 廉价 veto 仍未穿过成本门槛，收口 background/P0

- Time: 2026-04-25 21:05 UTC
- Target: `Rank 436 / acceleration minus vol-drag carry`
- Slot: `Surviving candidate slot`
- Verdict: `background/P0`

## Why this step was legal
按当前 `cycle_plan`，排在最前的 pending 小点就是 `Rank 436` 的 survivor 唯一 follow-up；policy 只允许围绕上轮已收束的单一 decisive blocker——`1h parent -> 15m child` / 更低换手 / 最便宜 veto——给出出口决策。本轮未扩回多因子壳，也未转做第二个 pending 对象。

## Honesty / execution sub-check actually run
我直接对上轮同一主语做最便宜、最能改变结论的 clean-room 子检查：

- 数据：Binance USDⓈ-M perpetual public `15m` klines
- 资产：`BTC/ETH/SOL/BNB/XRP/DOGE/ADA/AVAX/LINK/DOT/LTC/UNI`
- 长度：最近 `6000` 根 `15m` bars
- 主语不变：`1h` parent 横截面 `carry = ret10 - 0.5*ret30 - k*vol20` 排名，做 `top-3 long-only`
- 成本：统一按 **one-way 4bps taker**、按换手粗扣
- 只测最便宜变体：
  1. `k` 扫描 `0.1/0.2/0.3/0.4`
  2. `delay1`：把 `15m child` 读成“信号后先等 1 根 15m，再吃余下 child 窗口”
  3. `dispersion veto`：仅在横截面 score dispersion 落在上半/上四分位时开仓
  4. `spread veto`：仅在 `top1-top3 score spread` 足够宽时开仓

## Key results
### Base（与上轮 survivor 主语最贴近）
- `base_k0.3`：gross `+0.147 bps/bar`，turnover `7.786%/bar`，net **`-0.165 bps/bar`**
- `base_k0.4`：gross `+0.131 bps/bar`，turnover `7.506%/bar`，net **`-0.169 bps/bar`**

### Child execution proxy（只延后一根 15m，不改主语）
- `delay1_k0.3`：gross `+0.247 bps/bar`，turnover `7.786%/bar`，net **`-0.064 bps/bar`**
- `delay1_k0.4`：gross `+0.233 bps/bar`，turnover `7.506%/bar`，net **`-0.068 bps/bar`**

### Cheapest vetoes
- `delay1_disp_q0.5`：只在 dispersion 高于中位数时开仓，active share `50%`，gross `+0.179 bps/bar`，turnover `5.913%/bar`，net **`-0.057 bps/bar`**
- `spread_q0.8`：只做 top-spread 最宽的 `20%` 小时，active share `20.1%`，gross `+0.084 bps/bar`，turnover `3.979%/bar`，net **`-0.075 bps/bar`**
- 其余便宜 veto / 参数组合全部仍为负，最差到约 `-0.357 bps/bar`

## Decision
本轮正式收口为 `background/P0`，**不 promote_P2**。

系统认知变化如下：

> `Rank 436 / acceleration minus vol-drag carry` 的 raw gross edge 并未消失，但 survivor 唯一 follow-up 已证明：在不漂移主语的 `1h parent -> 15m child`、以及最便宜的 `delay-1 / dispersion veto / score-spread veto` 口径下，它依然无法穿过统一 `4bps` one-way 成本门槛；最好净值也只到 `-0.057 ~ -0.064 bps/bar`，因此当前缺的不是“再补一点 admission”，而是仍存在单一 decisive execution blocker，不能诚实升入 `P2`。

## Why not promote_P2
policy 允许 survivor 只做一次最小 decisive follow-up；这次 follow-up 的唯一任务就是回答“低换手 / child execution / 最便宜 veto 能否把它推到值得做 P2 admission”。答案是否定的：

1. **主语没漂移，但门槛也没过**：即使不扩回多因子壳、只做同一 carry router 的 execution 优化，after-cost 仍未转正。
2. **最好的 improvement 仍只是 near-miss，不是 admission-ready**：`-0.057 bps/bar` 说明方向上可改善，但还不足以诚实说“已不存在单一 decisive blocker”。
3. **继续同维度续测会违反 policy**：上一轮已经把 blocker 收束到 execution realism；本轮沿同轴补做最便宜检查后仍未升级层级，继续追加同维度 follow-up 默认属于低杠杆重复。

## Runtime writes completed
- `Surviving candidate slot`：`Rank 436` 用完唯一 follow-up，释放为 `none`
- `cycle_plan[1]`：写回 `background/P0` 出口结论，并标记为 `done`

## Tail execution note
- Homepage publish：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 本轮异步结束为 `SIGKILL`（session `vivid-du`），按 policy 记为**非阻断尾部失败**，不回滚本轮 verdict / state / log。
- Email notify：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py --subject "[momentum-bot3-auto] Rank 436 survivor收口回背景" --body-file /root/clawd/jerry/momentum/research/optimization_loop/2026-04-25_2105_rank436_survivor_followup_background_p0.md` 已成功发送。