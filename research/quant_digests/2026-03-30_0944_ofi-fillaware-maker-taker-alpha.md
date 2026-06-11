# 别把这份 2026 OFI repo 只读成风控壳子：对 desk 更该先测的是「lagged OFI z-score × cost-aware gating × fill-aware maker/taker split」BTC 单币完整 raw alpha
- 时间：2026-03-30 09:44 UTC
- 类型：2026 GitHub 新仓库 + `strategy_core.py` / `alpha/microprice_ofi_alpha.py` source audit + repo 内置 IS/OOS 产物复核 + 2024 SSRN 元数据锚点
- 主题类型：raw alpha
- 基础 alpha：**lagged OFI z-score 预测未来超短 drift**，并用 `microprice edge / queue imbalance / half-spread` 把“方向 edge”直接变成 **maker-or-taker、做/不做、做多大** 的可执行状态机
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha/microstructure/ofi/microprice/queue-imbalance/fill-aware/maker-taker/cost-aware-gating/single-asset/btc/binance/1m/3m/5m/repo/paper/public-proxy/cost
- 证据类型：代码级策略定义 + repo 自带回测产物 + 经典 microstructure 理论锚点 + crypto 论文元数据弱锚点

## 1. 这次看了什么
这次主看 **`jingyaolai17/tardis-python-private` (2026)**。它最值钱的地方不是“又一个 OFI 指标”，而是把一条微结构 raw alpha 从 `signal -> gate -> execution -> kill-switch` 全部写进同一份 `strategy_core.py`：

- `ofi_z = (ofi - rolling_mean) / rolling_std`
- `beta_fwd = cov(ret_fwd_30s_bps, ofi_z) / var(ofi_z)`
- `alpha_bps = beta_fwd * ofi_z`
- `maker_edge = alpha_bps - join_thresh * half_spread_bps`
- `p_maker_fill = (1 - |QI|)^1.5`
- 只有当 `|alpha|` 同时穿过**绝对门槛**和**成本门槛**时才允许入场

一句话核心结论：

> **真正值得 intake 的不是“OFI 能不能预测几秒钟价格”，而是“OFI 这条边怎么在穿过 spread/fee/slippage 之后，仍然留下可交易的净边”。**

## 2. 核心结论
- **base alpha 很清楚：** repo 不是把 OFI 当解释变量，而是直接把 `lagged OFI z-score -> future 30s return` 写成 `alpha_bps`，这是 raw alpha，不是 filter。
- **最值钱的是成本感知 admission rule：** `apply_alpha_gating()` 要求 `|alpha| >= 0.8bps`，且 `|alpha| >= 1.5 × hurdle_bps`；`hurdle_bps` 又显式包含 `half-spread + taker fee + taker slippage + maker slippage`。
- **执行层不是事后补丁：** repo 先判断 `maker_edge > 0` 再决定是否挂 maker，并用 `QI` 估算 `p_maker_fill`，把“信号对不对”和“能不能低成本成交”写成一个联合决策。
- **状态机可直接迁到 desk：** 代码里有 `cooldown_bars=10`、`min_hold_bars=20`（在 `100ms` bar 上分别约 1s / 2s），本质上是在防止微结构 alpha 因 flip-churn 被成本吃死。
- **但 repo headline 业绩暂时不能照单全收：** `IS_OOS_Validation_summary.md`、`IS/OOS csv/json` 和脚本里的数据区间/结果彼此不一致。机器可读产物里，OOS `net_edge_bps_on_executed ≈ 3.87bps`、`total_pnl_after_usd ≈ 159.8`（`$50k` 资本），说明**结构值得偷**，但**收益数字必须重跑复核**。

一句话说明它怎么证明：

> **不是只靠论文口头说 OFI 有效，而是把信号、成本门槛、maker/taker 分流、库存与 kill-switch 全写成代码，并附了 IS/OOS 产物；虽然产物口径有冲突，但策略骨架是可审计的。**

## 3. 为什么和当前项目有关
这轮更值得写它，而不是再补一个泛泛的 regime/filter，原因很直接：

1. **它是 raw alpha，而且是完整策略。** 不是“高 OFI 所以少做”，而是“高 OFI 在穿过成本后该怎么做”。
2. **它补的是 1m/3m 高强度素材池。** 当前 digest 已有不少 `5m/15m` 方向与 pairs 卡，这张卡补的是更快、更 execution-sensitive 的单币微结构线。
3. **它天然能拆成 desk 组件。** `alpha`、`admission`、`maker/taker split`、`toxicity scaler`、`kill-switch` 都能单独 ablation。
4. **它提醒我们别被好看的回测图骗。** 这份 repo 最大价值也许不是 OOS 数字，而是教我们怎么把“净边必须大于 frictions”写进信号本体。

## 3.5 策略拆解（必填）
- 方向属性：BTC 单币 long/short 超短周期 directional alpha
- 基础 alpha：`OFI z-score` 对未来 `30s` drift 的预测
- regime：高波动 / 极端 spread / 高 toxicity 时做缩放，不把它们当 alpha 本体
- filter / veto：`|alpha|` 不过绝对阈值或不过成本阈值则不交易；sign flip 后强制 cooldown
- risk / sizing / execution overlay：`maker_edge` 决定 maker/taker；`QI` 决定 maker fill proxy；库存上限、inventory decay、drawdown kill-switch、linear flatten 都已写进框架

## 4. 真正值得 desk 先偷哪一段
最该先偷的不是 OFI，而是 **“OFI 只有在净边能覆盖 frictions 时才允许变成仓位”** 这条 admission 逻辑。很多微结构信号死掉，不是方向错，而是：
- edge 太小；
- 交易太碎；
- flip 太频；
- maker 想象成交，实际全变 taker。

这份 repo 把这几个坑一次性写出来了，所以它更像一张 **raw alpha + execution shell** 卡，而不是单纯指标卡。

## 5. 可复刻的最小实验
### 5.1 数据源与公开性
- **理想口径：** Binance L2 + trades（repo 通过 Tardis 拉历史，非完全免费）
- **公开最小代理：** Binance `bookTicker` 实时采集 + `aggTrades` 公共流，自己积累 7~14 天；先做 `L1 OFI / microprice / spread` 代理
- **映射频率：** 先做 `1m / 3m`，若成本后存活，再看能否向 `5m` transfer；不建议直接伪装成 `15m` 主信号

### 5.2 最小策略口径
1. 用 `bookTicker + aggTrades` 重建 `L1 OFI`、`QI`、`microprice-mid`、`half-spread_bps`
2. 先用最近 `N=300~600` 个子样本标准化 `ofi_z`
3. 定义 `alpha_proxy = beta_fwd * ofi_z`，`beta_fwd` 可先用 rolling OLS / cov-var
4. 入场条件：
   - `|alpha_proxy| >= max(0.8bps, 1.5 × hurdle_bps)`
   - `hurdle_bps = half_spread + fee + slip`
   - `alpha_proxy > 0` 做多，`< 0` 做空
5. 出场条件：
   - `alpha_proxy` 回到门槛内；或
   - sign flip；或
   - 超时 `1/3/5` 分钟

### 5.3 第一轮先看什么
- 成本前后 `avg trade` 差多少？
- maker share、taker share、fill proxy 分层后，哪一层还留边？
- `1m` 与 `3m` 谁更能抗 flip-churn？
- toxicity scaler 是真降噪，还是把 raw alpha 也一起削没？

## 6. 这张卡最容易错在哪里
- **错法 1：** 只看到 OOS Sharpe，不核对 repo 内不同文件的口径冲突。
- **错法 2：** 把 OFI 当免费方向因子，忽略 spread/slippage 后其实净边不够。
- **错法 3：** 看到微结构 alpha 就强行迁到 `15m`；这条线更像 `1m/3m` 主实验、`5m` 仅做 transfer check。
- **错法 4：** 以为 maker rebate 能自动救活策略；真实难点在于 fill quality，而不是名义费率。

## 7. 为什么值得进入研究池
它值得进池，不是因为 repo 业绩已经可信到可实盘，而是因为它把一个很多人嘴上会说、但很少代码里写完整的命题落地了：

> **微结构 raw alpha 不是“预测方向”就结束，而是必须连同成本门槛、成交方式和 churn 抑制一起定义。**

对当前 desk，这比再补一张纯解释型 microstructure 卡更值钱，因为它能直接产出一轮 `1m/3m` 的诚实 first verdict。

## 8. 来源与链接
1. **Lai, Jingyao? / GitHub handle `jingyaolai17` (2026). _tardis-python-private_. GitHub Repository.**  
   - Venue: GitHub  
   - DOI: N/A  
   - Readable URL: <https://github.com/jingyaolai17/tardis-python-private>  
   - Repo URL: <https://github.com/jingyaolai17/tardis-python-private>  
   - Key files:  
     - <https://github.com/jingyaolai17/tardis-python-private/blob/main/strategy_core.py>  
     - <https://github.com/jingyaolai17/tardis-python-private/blob/main/alpha/microprice_ofi_alpha.py>
2. **Cont, R., Kukanov, A., & Stoikov, S. (2014). _The Price Impact of Order Book Events_. Journal of Financial Econometrics.**  
   - DOI: `10.1093/jjfinec/nbt003`  
   - Readable URL: <https://doi.org/10.1093/jjfinec/nbt003>
3. **Alexander, C., Heck, D., Kaeck, A., & Riordan, R. (2024). _Order Flow Impact and Price Formation in Centralized Crypto Exchanges_. SSRN Electronic Journal.**  
   - DOI: `10.2139/ssrn.4867599`  
   - Readable URL: <https://doi.org/10.2139/ssrn.4867599>

## 9. 下一步怎么测
1. **先做公开数据代理版**：连续抓 7~14 天 Binance `bookTicker + aggTrades`，只复刻 `L1 OFI + spread hurdle + sign flip exit`。  
2. **然后做 friction ladder**：round-trip 先测 `2 / 4 / 6 / 8 bps`，再拆 maker/taker。  
3. **再做 1m vs 3m transfer**：若 `1m` 成本后活、`3m` 也不塌，这张卡才值得升 replication queue。  
4. **最后才补 Tardis/L2**：若公开代理版已有边，再为更高质量 L2 数据付复杂度；反之就别急着买更贵的数据。