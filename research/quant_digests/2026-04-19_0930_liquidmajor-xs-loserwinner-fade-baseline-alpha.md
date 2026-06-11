# 别把这份 2026 repo 只读成“trend 打败 mean reversion”：对 short-cycle crypto desk，更该先保留的是「liquid-major 横截面 loser→winner fade 基线」这条 raw alpha

- 时间：2026-04-19 09:30 UTC
- 类型：2026 GitHub repo source audit（`README.md` + `03_backtest.ipynb`）+ Binance USDⓈ-M `15m` liquid-major baseline probe（本地 artifacts）
- 主题类型：raw alpha
- 基础 alpha：横截面短窗里“最近相对跌得最狠的币，后续更容易相对反弹；最近相对涨得最猛的币，后续更容易相对回吐”（loser long / winner short）
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：否（当前 baseline 费后为负）
- 主题标签：raw-alpha / cross-sectional / relative-value / mean-reversion / loser-winner / liquid-majors / intraday / 15m / 5m / cost / router
- 证据类型：repo + notebook 输出 + 本地可复算表格

## 1) 先把一句话说清楚（base alpha 判定）
这份仓库最该留给 desk 的，不是“20d momentum 在 OOS 失效”这句 headline；**最该保留的是：横截面 loser→winner fade 这条 raw alpha 本体仍有统计关系，只是原始执行形态成本太高。**

换成人话：
- 不是去猜“全市场涨跌方向”；
- 而是同一时点在一篮子币里，做“相对落后 vs 相对领先”的回吐交易。

## 2) 这次看了什么
主要看 `prams2104/crypto-momentum-backtest`：
- README 明确给了 train/validation/OOS 的分段结论；
- `03_backtest.ipynb` 里给了信号构造（`20d momentum`、`1d reversal`）、`shift(1)` 执行、turnover/cost、alpha t-stat。

repo 的关键信息（作者自报）是：
- `1d reversal` 在 OOS (`2025-2026`) 统计上显著（alpha/t-stat 好看）；
- 但 turnover 极高，20 bps 成本后净值翻负。

所以正确读法是：
- **alpha 关系存在**；
- **执行壳不合格**。

## 3) short-cycle desk 该怎么接（本地 15m baseline）
为了把“日频 1d reversal”翻成 desk 可执行语言，我保留同一经济含义做了轻量 baseline（本地 artifacts）：
- Universe：10 个 liquid majors（BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LINK/AVAX/LTC）
- Bar：`15m`
- 观察窗：最近 `60d`
- 规则：`L=8` 根回看（约 2h）做横截面 loser/winner 排序，持有 `H=8` 根（约 2h）

结果（`reports/artifacts/quant_digests/2026-04-19_intraday_xs_fade_summary.csv`）：
- `baseline_top1_bottom1`：
  - `n=5649`
  - `mean=+4.63 bps`（gross）
  - `win_rate=55.76%`
  - `net_after_8bps=-3.37 bps`
  - `net_after_16bps=-11.37 bps`
- `baseline_q20`（尾部截断版）也仍是费后负值：
  - `mean=+3.80 bps`
  - `net_after_8bps=-4.20 bps`

结论很直接：
- **raw alpha 的 gross 方向是存在的；**
- 但按当前最朴素执行，`15m` 下已经被 8~16 bps 成本打穿。

## 4) 为什么这不是重复 old thesis
这次不是“再讲一次 daily reversal 显著但 cost-dead”。
这次多做了一步 desk 相关的翻译：
- 用 liquid-major + `15m` 的同构 baseline，直接回答“现在这条线在 short-cycle 还能不能当母体”；
- 答案是：**能当 baseline，但不能直接上 production。**

也就是：
- 它现在更像 `router / admission` 的母板，
- 不是裸跑就能吃到净 alpha 的成品策略。

## 5) 最小可复现实验（下一步怎么测）
先别加复杂模型，按“最小改动、最大信息增益”走三步：

1. **调仓降频实验（先做）**
   - 同样 `15m` 信号，但组合只在 `1h / 2h / 4h` 重排一次；
   - 目标：压 turnover，看 `net_after_6/8bps` 能否翻正。

2. **极端尾部 admission（再做）**
   - 只交易横截面分位最极端 `top/bottom 10%~20%`；
   - 目标：牺牲频率换单笔 edge，提升 post-cost expectancy。

3. **child execution（最后做）**
   - 把 `15m` 的组合信号下沉到 `5m` 分批执行（maker-first + timeout）；
   - 目标：把 roundtrip friction 从“假设 8bps”压到更可实现区间。

### 成败门槛（建议）
- 如果 `1h/2h` 调仓 + 极端尾部后，`net_after_6bps` 仍长期 ≤ 0：
  - 这条线降级成 negative-control baseline；
  - 后续所有 XS reversal 新想法必须先打赢它再升格。

## 6) 风险与保留
- 这条线最大的风险不是“预测失效”，而是“执行成本与容量”。
- 当前证据还停在公开 K 线层，没有订单簿冲击与真实排队成交。
- `extreme` 子桶样本很少（例如 n=3 的高均值桶），不能当稳定 pocket。

## 7) 来源
- Repo：
  - <https://github.com/prams2104/crypto-momentum-backtest>
- README：
  - <https://raw.githubusercontent.com/prams2104/crypto-momentum-backtest/main/README.md>
- Notebook：
  - <https://raw.githubusercontent.com/prams2104/crypto-momentum-backtest/main/03_backtest.ipynb>
- GitHub metadata：
  - <https://api.github.com/repos/prams2104/crypto-momentum-backtest>
- 本地实验产物：
  - `reports/artifacts/quant_digests/2026-04-19_intraday_xs_fade_meta.json`
  - `reports/artifacts/quant_digests/2026-04-19_intraday_xs_fade_summary.csv`
  - `reports/artifacts/quant_digests/2026-04-19_intraday_xs_fade_events.csv`
