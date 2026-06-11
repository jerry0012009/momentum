# 别把 Guo et al. (2024) 只读成“crypto 也有 cross-autocorrelation”：对 short-cycle crypto desk，更该先拆的是「peer-return spillover × laggard catch-up basket」这条 raw alpha
- 时间：2026-04-21 15:06 UTC
- 类型：论文
- 主题类型：raw alpha
- 基础 alpha：其他币上一根收益会慢半拍传到本币；交易上做多 `peer 上一根更强、自己上一根更弱` 的 laggard，做空相反的 outrunner
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / cross-sectional / lead-lag / spillover / laggard-catch-up / relative-value / 5m / 15m / paper / public-data / cost
- 证据类型：论文证据 + public-data portability probe

## 1. 这次看了什么
看的是 Guo, Sang, Tu, Wang 发表在 *Journal of Economic Dynamics and Control*（2024）的论文 *Cross-cryptocurrency return predictability*。这篇东西最值钱的，不是“crypto 之间有关联”这句废话，而是更具体的一句：**别的币刚刚走出来的收益，会对本币下一步回报形成可交易的预测力。**

## 2. 核心结论
- 论文摘要层面的主结论很硬：Binance 数据上，**其他币的滞后收益对目标币未来收益有显著预测力**，而且用 adaptive LASSO、PCA 等方法做都还成立。
- 作者不是只做回归显著性，还明确说：**按过去收益构造的 long-short 组合，在样本外、扣交易成本后仍有可观回报**。
- 对我们 desk 来说，最值得拿来复现的，不是整篇慢频预测框架，而是一个更短周期、能立刻动手的翻译：`peer lag gap = 其他币上一根均值收益 - 本币上一根收益`。
- 我用 Binance USDⓈ-M 10 个 liquid majors 做最小 transfer：`15m` 上，`peer_lag_gap` strongest-only 的 top1-vs-bottom1 版本 gross 约 `+0.22 bps/bar`、胜率约 `51.5%`、60 天 gross 累积约 `+12.6%`；但粗扣 `4 bps` round-trip 后约 `-3.78 bps/bar`，说明 **alpha 方向在，厚度不够，不能直接拿大币 taker 版硬上**。
- `5m` 更薄：同口径 gross 只有约 `+0.03 bps/bar`，基本可直接判定为 **不能裸做**。
- 额外一条有用信息：`15m` 的 quote-volume 加权 peer 版本在最强 `q90` pocket 里 gross 约 `+0.30 bps/bar`，说明这条线更像 **shared feature / router / admission score**，而不是 broad always-on 主策略。

## 3. 为什么和当前项目有关
这轮和当前主线的关系非常直接：我们最近已经补了不少单资产 trend / MR，也补了 pairs / basis / funding，但 **“cross-coin lead-lag spillover” 这种横截面 raw alpha 母体还不够系统**。这篇论文正好补的是：
- 不是传统 pair spread，也不是 market-beta neutral 残差；
- 而是 **同一 crypto 横截面里，信息在币之间慢扩散**；
- 所以它天然能服务 `5m/15m` 的 basket router、laggard catch-up、leader-vs-follower 子模块。

一句话核心结论：**别的币先动、你跟得慢，本身就可能是一条 alpha。**

一句话证明方式：**作者用 Binance 数据做跨币收益预测回归与样本外组合检验，并报告扣成本后仍保留超额收益。**

最值得复用/复现的点：**把“peer lagged return”当成一个明确可算的共享因子，再看它该驱动 laggard catch-up、outrunner fade，还是只做 admission score。**

## 3.5 策略拆解（必填）
- 方向属性：横截面 / 相对价值
- 基础 alpha：peer-return spillover × laggard catch-up
- regime：更适合信息扩散没被完全压平、横截面分化仍存在的时段；大盘单边一致冲击后可能更弱
- filter / veto：优先加 `leader breadth`、`dispersion`、`signal spread percentile`、`quote-volume concentration`，避免所有币一起同步乱跳时硬做
- risk / sizing / execution overlay：先做 `top1` 或 `top2-vs-bottom2` 小篮子；默认 1 bar hold；先按 market-neutral 等权；成本口径先粗扣 `4 bps` round-trip；若后续厚度只剩亚 bps，必须转 maker-first / child execution / mid-cap selective pocket

## 4. 可复刻的最小实验
**研究假设**：如果别的币在上一根 bar 已经先走出明显收益，而本币还没完全跟上，那么本币下一根更可能 catch up。

**一个可计算定义**：
- `peer_lag_gap_i,t = mean(r_{-i,t-1}) - r_{i,t-1}`
- 每根 bar 做多 `peer_lag_gap` 最大的 1~2 个币，做空最小的 1~2 个币
- 下一根开盘进、持有 1 根 bar、下根开盘平

**最小回测切口**：
- 资产：Binance USDⓈ-M `BTC/ETH/SOL/BNB/XRP/DOGE/ADA/LTC/LINK/AVAX`
- 周期：先 `15m`，再看 `5m`
- 样本：我这轮快检用了约 `60d(15m)` / `20d(5m)`

**这轮快检最该先记住的数**：
- `15m top1`：gross `≈ +0.22 bps/bar`，胜率 `≈ 51.5%`，gross cum `≈ +12.6%`
- `15m q90(volume-weighted peer) pocket`：gross `≈ +0.30 bps/bar`
- `5m top1`：gross `≈ +0.03 bps/bar`

**下一步怎么测**：
1. 把 universe 从 10 majors 扩到 top30 quote-volume，专门看 **mid-cap follower pocket** 是否比 majors 厚；
2. 不再只用简单均值，改成论文提示过的 `adaptive LASSO / PCA spillover score`；
3. 加 `leader breadth` 与 `dispersion` gate，看这条线是更像 `catch-up continuation` 还是 `overreaction fade`；
4. 如果 15m 仍只有亚 `1 bps` gross，就把它降级成 **shared cross-sectional feature**，服务其他 alpha 的 router，而不是 standalone 主信号。

## 5. 风险与保留意见
- 我这轮能拿到的是 DOI / Crossref / OpenAlex 元数据、作者主页与 IDEAS 摘要页；**全文没有顺手抓到可直接读的 PDF**，所以关于论文细节（比如具体频率、确切组合构造、成本口径）要保留一层谨慎。
- 我的 public probe 是 desk 化简化版，不是论文原模原样复刻；因此它回答的是“这个母体 alpha 能不能往 `5m/15m` transfer”，不是“论文结论真伪复审”。
- 当前在 liquid majors 上，edge 明显被成本吃穿；所以更合理的定位是：**这是条 raw alpha 母体，但目前更像 selective router / shared feature，不像 broad taker strategy。**

## 6. 来源
- Li Guo, Bo Sang, Jun Tu, Yu Wang. (2024). *Cross-cryptocurrency return predictability*. *Journal of Economic Dynamics and Control*, 163, 104863.
- DOI: `10.1016/j.jedc.2024.104863`
- Readable URL: `https://doi.org/10.1016/j.jedc.2024.104863`
- IDEAS abstract: `https://ideas.repec.org/a/eee/dyncon/v163y2024ics0165188924000551.html`
- Author page / citation: `https://guoli0618.github.io/publication/paper4_JEDC_crypto`

## 7. 本地产物
- Probe summary: `reports/artifacts/quant_digests/2026-04-21_crosscrypto_predictability_probe_summary.csv`
- 15m trades: `reports/artifacts/quant_digests/2026-04-21_crosscrypto_predictability_15m_trades.csv`
- 5m trades: `reports/artifacts/quant_digests/2026-04-21_crosscrypto_predictability_5m_trades.csv`
