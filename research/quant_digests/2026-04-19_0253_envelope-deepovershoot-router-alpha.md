# 别把这份 2026 mean-reversion envelope bot 只读成“对称抄底摸顶脚本”：对 short-cycle crypto desk，更该先拆的是「15m deep-overshoot long-side top1 router」这条 raw alpha
- 时间：2026-04-19 02:53 UTC
- 类型：GitHub
- 主题类型：raw alpha
- 基础 alpha：短窗价格相对快速均线出现深度下偏离后，更容易在未来几根 `15m` bar 向局部均值回归；若同一时点多币同时超跌，只做偏离最深的一档。
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：mean-reversion / envelope / overshoot / router / long-only / local-fair-value / binance-perpetual / 15m / 5m
- 证据类型：工程经验 + repo source audit + public-data portability probe

## 1. 这次看了什么
看的是 2026 GitHub 仓 `grantad/crypto-bot`。源码核心不复杂：`SMA/EMA/Donchian` 均值 + 三层 envelope 分批进场，价格回到均值就平仓，外加 stop-loss、close-all 和 risk manager。它的 headline 很像“对称 long/short 均值回复机器人”，但对我们 desk 更值钱的不是整套对称壳，而是其中那条**局部过度下杀后回归快均值**的 raw alpha。

**一句话核心结论：** 这条线当前更像 `15m` 的 long-only 深超跌回归 pocket，而不是可直接双向复制的对称均值回复系统。  
**一句话证明方式：** 我直接按 repo 的“三层 envelope + 回均值退出 + 固定止损 + fee”骨架，映射到 Binance USDⓈ-M `15m/5m` 多币公共数据做 portability probe，再比较 all-sample、long-only 和 top1 router 的成本后表现。

## 2. 核心结论
- repo 原版是完整策略壳：均值定义、三层加仓、回均值 exit、stop、risk manager、maker/taker fee 都写了，**不是纯信号片段**。
- 但 recent Binance portability probe 显示：**对称 long/short 不成立**。`15m` 全样本 `2443` 笔，平均仅约 `-9.62bps net/trade`；short 腿更差，约 `-15.03bps net`。
- 真正有 pocket 的是 **`15m` long-only**：8 个 liquid majors 合并后约 `1223` 笔，`+3.97bps gross`，但全做仍约 `-4.22bps net`，说明需要 router / admission，而不是见信号就全打。
- 一旦改成 **同一决策时点只做 deepest long overshoot top1**，`15m` 约 `501` 笔，提升到 `+11.00bps gross / +2.69bps net`，胜率约 `64.47%`。
- 若进一步只看 `BTC/ETH` 的 `15m` long router，约 `98` 笔，达到 `+18.01bps gross / +9.46bps net`，胜率约 `69.39%`；反过来 `5m` 版本即便做 long top1 仍约 `-7.29bps net`，说明它更像 **`15m` 母信号 + `5m` child execution**，而不是裸 `5m` 主策略。

## 3. 为什么和当前项目有关
这条线补的是我们最近素材池里相对少一点的 **single-asset local-fair-value / overshoot MR 完整壳**。它和很多“下跌反弹”想法的区别在于：repo 已经把 `entry / scale-in / exit / stop / risk blocker / fee` 写成了工程化骨架，所以这轮不只是得到一个“超跌会反弹”的概念，而是得到一条能直接拆成母信号、router、child execution 的完整策略原型。

## 3.5 策略拆解（必填）
- 方向属性：逆势 / 单资产；但当前有效 pocket 明显偏 long-only
- 基础 alpha：deep local overshoot -> revert to fast average
- regime：更像 `15m` 的局部恐慌/过冲，而不是 `5m` 连续裸抄底
- filter / veto：只做 long、不做 short；同一时点只留 deepest/top1；优先 `BTC/ETH`
- risk / sizing / execution overlay：三层 envelope 分批进场；回均值退出；固定 stop；建议 `15m` 触发后用 `5m` 拆分执行而非直接 taker 一把打满

## 4. 可复刻的最小实验
- 研究假设：`15m` 上相对 `SMA6` 深度下偏离的币，未来 `~5` 根 bar 内更容易反弹回局部均值；但要靠 router 才吃得下成本。
- 一个可计算定义：`SMA6` 为 midline，三层下轨用短周期 envelope ladder；触及下轨开 long，可分层加仓；`close >= midline` 平仓；固定 stop；每个决策时点只保留偏离最深的一档。
- 最小回测切口：Binance USDⓈ-M `BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK`，先做近 `60d` 的 `15m`，再把 entry 拆到 `5m` 做 child execution 对照。
- 最该先看：`net bps/trade` 与 `top1 router vs all-sample` 的增益；其次看 `BTC/ETH` 是否持续优于小币。

## 5. 风险与保留意见
- 这轮高价值结论恰恰是：**对称 short 腿明显不行**，别把 repo 原版“both directions”直接照搬。
- 当前 pocket 对交易成本很敏感；all-sample gross 不够厚，router 一旦退化，edge 很容易被吃光。
- envelope 百分比是 portability 映射，不是论文级最优参数；下一步更该测的是 ATR/波动率归一化 band，而不是在固定百分比上细抠小数点。
- 均值回复在事件驱动单边市里容易被 trend day 打穿，因此最好补事件 veto / funding-extreme veto / jump veto。

## 6. 来源
- grantad. (2026). *crypto-bot*.
  - Repo URL: `https://github.com/grantad/crypto-bot`
  - Readable URL: `https://github.com/grantad/crypto-bot/blob/main/README.md`
- Source audit used in this digest:
  - `https://raw.githubusercontent.com/grantad/crypto-bot/main/src/strategy.py`
  - `https://raw.githubusercontent.com/grantad/crypto-bot/main/src/backtester.py`
  - `https://raw.githubusercontent.com/grantad/crypto-bot/main/config/config.yaml`

## 7. 本地 portability probe 产物
- `reports/artifacts/quant_digests/2026-04-19_envelope_mr_summary.csv`
- `reports/artifacts/quant_digests/2026-04-19_envelope_mr_events.csv`
- `reports/artifacts/quant_digests/2026-04-19_envelope_mr_portfolio.json`
- `reports/artifacts/quant_digests/2026-04-19_envelope_mr_router_summary.csv`
