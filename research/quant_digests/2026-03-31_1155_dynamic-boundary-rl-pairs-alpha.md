# 别把 RL pairs 先读成黑箱择时：这篇 2024 论文 + 作者 repo 更该先测的是「静态 spread + 动态 band action」完整 raw alpha 骨架
- 时间：2026-03-31 11:55 UTC
- 类型：论文 + GitHub
- 主题类型：raw alpha
- 基础 alpha：高度协整/强共动交易对上的 spread 均值回归（long cheap leg / short rich leg）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / pairs / stat-arb / relative-value / mean-reversion / reinforcement-learning / dynamic-threshold / 1m / 3m / 5m / 15m
- 证据类型：论文证据 + 工程实现证据

## 1. 这次看了什么
这次看的是 **Hongshen Yang、Avinash Malik (2024)** 的论文 **_Reinforcement Learning Pair Trading: A Dynamic Scaling Approach_**，再配合同一作者公开的实现仓库 **`Hongshen-Yang/RL-pair-trading-kim`**。这组材料最值得我们 desk intake 的，不是“RL 又能打败传统策略”这句老话，而是一个更具体、也更可复刻的骨架：**pair spread 的 base alpha 仍然是均值回归，RL 只是在每个短 trading window 里，动态选择 entry band / stop band 这一组动作。**

## 2. 核心结论
- **一句话核心结论：** 真正该拿来测的不是“RL 预测下一根”，而是 **同一个 pairs mean reversion alpha 上，动态 band selection 能不能比固定 z-score 更稳。**
- 论文里最关键的设定很朴素：在 `1m` 数据上，对 `BTC-GBP` 与 `BTC-EUR` 做 pair trading，比较传统静态边界和 RL 动态边界；论文摘要给出的结果是：**传统非 RL 年化利润约 `8.33%`，RL 版本约 `9.94% ~ 31.53%`**，样本量 **`n = 263,520`**。
- 作者公开 repo 把这件事写得很清楚：状态几乎只有 **spread z-score**；动作不是“买/卖/平”三选一，而是 **6 组不同的 `entry threshold + stop-loss threshold`**；默认 `trading window = 15`、formation/lookback 例子是 `30`。
- repo 的 `env_kim.py` 还把规则明文化了：若 `|z|` 先穿 entry band 就开仓；若后续 `z-score` 过零就平仓；若穿 stop band 就止损；若到窗口末尾还没收敛就 **forced exit**。这已经是一个能直接写成 `entry / exit / risk / cost` 的完整短周期策略。
- 但更值钱的是反例：同一作者 repo 的 notebook 在 **`2023-10 ~ 2023-11` 训练、`2023-12` 测试** 的 Binance spot `BTCEUR / BTCGBP` 例子里，**PPO / A2C / DQN 的 net worth 最后大约掉到 `0.61 / 0.75 / 0.65`**。也就是说，**动态 band 这个想法值得 intake，但“RL 一上就赢”完全不该先验相信。**
- **一句话说明它怎么证明：** 论文靠的是 `1m` 样本上的 out-of-sample 策略对照；repo 则把动作空间、reward shaping、成本参数和最近样本失败案例都暴露出来，方便我们做诚实 transfer check。

## 3. 为什么和当前项目有关
它和我们当前 desk 的关系非常直接：这是一个 **可独立复现的 raw alpha 家族**，而且不是继续围着 breakout / retest 打转。对于 `1m / 3m / 5m / 15m` 来说，它提供的是 **relative-value / stat-arb** 的完整操作系统：
1. 先找可交易 pair；
2. 定义 spread；
3. 定义 band；
4. 规定窗口内开平仓、止损和超时退出；
5. 再问“动态 band”是否真的比静态 band 更值钱。

对当前素材池来说，最值得复用的不是 PPO/A2C/DQN 这些模型名词，而是 **“把 threshold 选择本身做成 action space”** 这个工程拆法。它能服务于 pairs，也能服务于别的 short-cycle mean reversion / relative-value alpha。

## 3.5 策略拆解（必填）
- 方向属性：相对价值 / pairs / stat-arb
- 基础 alpha：两条强共动价格序列的 spread 偏离会向历史均衡回归
- regime：仅在协整/共动关系稳定、双腿流动性足够、价差没有结构性断裂时启用
- filter / veto：pair 资格筛选、rolling spread 稳定性、最大可接受持仓时长、窗口末强制平仓
- risk / sizing / execution overlay：双腿等美元或 beta-neutral；entry/stop band 动态选择；显式交易成本；止损 + time stop；优先在高流动性同标的不同报价腿或高度协整大币对上测试

## 4. 可复刻的最小实验
- **研究假设：** 在高共动 crypto pair 上，`dynamic band selection` 能通过少做差交易、早切坏交易，提升 `after-cost spread return`，哪怕 base alpha 仍然只是普通的均值回归。
- **一个可计算定义：** 每个 `15` 根 bar 组成一个 trading window；用过去 `30` 根 bar 估计 ODR/TLS spread 残差并转成 z-score；动作空间固定为 6 组 `(entry, stop)`，例如 repo 里的 `0.5/2.5` 到 `3.0/5.0`；当 `|z|` 穿 entry 开仓，`z` 过零平仓，穿 stop 止损，窗口结束强制平仓。
- **最小回测切口：** 先别直接上复杂 cross-asset pair，先做 **Binance spot 同标的不同报价腿**（如 `BTCUSDT/BTCFDUSD`、`ETHUSDT/ETHFDUSD`）的 `1m` 与 `5m`；若这个最干净的 sandbox 都跑不赢静态 band，再考虑更泛化的 majors pair 或跨 venue pair。
- **最该先看 2 个指标：**
  1. `after-cost net spread return`（RL / 动态 band 是否真优于固定 `z-entry/z-exit`）
  2. `forced-exit rate + stop-loss rate`（动态 band 的价值，通常就体现在这两个坏结果是否显著下降）
- **第一组对照臂：** `static z>1.5 entry / z-cross-0 exit / z>3.5 stop / 15-bar timeout` 对比 `dynamic action policy`；先不追求 SOTA，只追求它是否在最近样本里仍有稳定增益。

## 5. 风险与保留意见
- 这篇 2024 论文的 headline 很亮眼，但 **标的非常窄**：`BTC-GBP` / `BTC-EUR` 这种同底层、不同法币报价腿，天然比普通币对更容易出现可回归 spread；把它迁移到更一般的 crypto pairs，难度明显更高。
- repo 的公开 notebook 已经提醒我们：**近样本 transfer 很脆弱**。如果训练窗口、交易窗口、reward 罚分、成本设定稍变，结果可能立刻翻负。
- repo 默认 `tc = 0.002`，也就是相当重的成本假设；这对 `1m` stat-arb 很诚实，但也说明：**这类策略不是先问方向准不准，而是先问时间止损和坏交易切断够不够快。**
- RL 很容易把“静态 rule 已经足够”包装成“模型提效”。所以 intake 时必须先锁死：**同一 pair、同一 spread、同一成本、同一超时规则，只比较 band policy 是否增值。** 否则结论不干净。

## 6. 来源
- **Yang, H., & Malik, A. (2024). _Reinforcement Learning Pair Trading: A Dynamic Scaling Approach_. Journal of Risk and Financial Management, 17(12), 555.**
- DOI: `10.3390/jrfm17120555`
- Readable URL: `https://doi.org/10.3390/jrfm17120555`
- Open-access PDF URL: `https://www.mdpi.com/1911-8074/17/12/555/pdf?version=1733886143`
- Repo URL: `https://github.com/Hongshen-Yang/RL-pair-trading-kim`
- **Kim, T., & Kim, H. Y. (2019). _Optimizing the Pairs-Trading Strategy Using Deep Reinforcement Learning with Trading and Stop-Loss Boundaries_. Complexity, 2019, 3582516.**
- DOI: `10.1155/2019/3582516`
- Readable URL: `https://doi.org/10.1155/2019/3582516`
- PDF URL: `https://downloads.hindawi.com/journals/complexity/2019/3582516.pdf`
