# bot3 自动优化日志：Crypto-Stat-Arb P2 admission（honesty / execution realism）

> Post-hoc identity note（2026-03-24 10:53 UTC）：该对象现已正式分配 `Rank 154`；后续 desk 口径统一写作 `Rank 154 / Crypto-Stat-Arb`。
- 时间：2026-03-24 10:46 UTC
- 路径判断：Scout
- 主点：Active P2 slot admission follow-up
- 紧邻子点：honesty / execution realism（daily close 执行、funding 记账、trade buffer / 成本口径）
- 认领动作：`cycle_plan` 第 1 项

## 本轮执行
1. 读取 policy 与 runtime state，确认本轮唯一合法动作是给 `ryanczm/Crypto-Stat-Arb` 做 1 次最小 P2 admission honesty 检查。
2. 直接从公开 repo 拉取 `rsims.py` 与 `model_df.pkl`，核对回测器的真实记账顺序，而不是只复述前两轮摘要。
3. 发现 repo 的执行顺序是：先按 `current_positions` 吃完 `previous_prices -> current_prices` 的价格变动和当期 funding，再用 `current_target_weights` 按 `current_prices` 调仓；这等价于**信号在当日 close 才成立、也按当日 close 成交**的口径，天然比 next-day / next-bar 更友好。
4. 在不改策略定义的前提下，做最小保守重放：把权重整体滞后 1 天，再分别比较 `same-day funding`、`lagged funding`、以及更保守的手续费 / `trade_buffer` 组合。

## 关键结果
### 1) daily-close 执行假设确实偏友好，但还没把组合边际吹成幻觉
在 `combined`、`10bps/side`、`trade_buffer=5%` 下：
- repo-like（同日权重执行）：CAGR 约 `45.5%`，Sharpe `1.32`，MDD `-33.0%`，平均日换手 `7.3%`
- **权重滞后 1 天**：CAGR 约 `42.2%`，Sharpe `1.26`，MDD `-28.5%`，平均日换手 `7.2%`
- **权重 + funding 都滞后 1 天**：CAGR 约 `42.8%`，Sharpe `1.27`，MDD `-28.5%`

读法：把同日 close 执行修正成更诚实的 1 日滞后后，组合表现有回落，但不是塌成接近零；说明这条线存在一点 execution optimism，**但 survive 不是靠同 bar / 同日 fill 幻觉硬撑**。

### 2) funding 不是装饰项，但“同日 funding 记账”没有把结果夸大太多
在 `combined`、`权重滞后 1 天`、`10bps/side`、`buffer=5%` 下：
- `same-day funding`：CAGR 约 `42.2%`，Sharpe `1.26`
- `lagged funding`：CAGR 约 `42.8%`，Sharpe `1.27`
- `no funding`：CAGR 约 `34.2%`，Sharpe `1.08`

读法：funding 对这套 cross-sectional 组合是**真实贡献项**，拿掉 funding 会明显降档；但把 funding 从 same-day 改成 lagged 后并没有显著恶化，说明 repo 的 funding 记账时点不算主要夸大源。

### 3) 真正的脆弱点不是 10bps，而是 buffer 设太松或太紧都会伤边际
在更诚实的 `lagged weights + lagged funding` 口径下，`combined` 对 `trade_buffer` 很敏感：
- `10bps / buffer=0%`：CAGR 约 `25.7%`，Sharpe `0.73`，换手 `61.9%/日`
- `10bps / buffer=2%`：CAGR 约 `43.4%`，Sharpe `1.05`，换手 `24.5%/日`
- **`10bps / buffer=5%`：CAGR 约 `42.8%`，Sharpe `1.27`，换手 `7.2%/日`**
- `10bps / buffer=10%`：CAGR 约 `4.4%`，Sharpe `0.35`

成本再抬高也没立刻打死它：
- `15bps / buffer=5%`：CAGR 约 `40.9%`，Sharpe `1.23`
- `20bps / buffer=5%`：CAGR 约 `39.1%`，Sharpe `1.19`

读法：`5%` buffer 不是明显偷鸡参数，反而像把高频抖动压下去后的一个合理甜点；真正夸张的是 **0% buffer 的高换手版本**，那条线一加摩擦就明显失真。

## 本轮结论
- verdict：`keep_P2`
- 一句话结果：`ryanczm/Crypto-Stat-Arb` 在把权重与 funding 统一改成更诚实的 1 日滞后后，`combined` 仍保持明显正边，说明它不是靠同日 close / funding 记账幻觉硬撑；但这套边际明显依赖 `trade_buffer≈5%` 的低换手实现，因此当前最诚实结论仍是 `keep_P2`，未到可直接升 `P3` 的稳健度。

## 简短 scorecard
- execution realism：7/10
- funding accounting honesty：7/10
- buffer / friction robustness：6/10
- direct P3 readiness：5/10
- 本轮总评：**keep_P2，不升 P3，不退 background**

## 对下一轮的明确交接
- bot2 下一轮应据此重排：这条线的核心 admission 缺口已经从“会不会纯粹是 same-day 偏乐观”收敛为“是否值得继续留在 P2，还是该基于 regime / universe / implementation scope 做 promote-or-park 决策”。
- bot3 本轮不再扩做 compare、fresh intake 或 launch handoff。