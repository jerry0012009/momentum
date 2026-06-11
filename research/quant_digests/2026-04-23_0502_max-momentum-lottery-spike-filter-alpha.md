# 别把 Li et al. (2021) 只读成“又一个 momentum 异象”：对 short-cycle crypto desk，更该先拆的是「低 MAX 走势里的 continuation」这条 raw alpha
- 时间：2026-04-23 05:02 UTC
- 类型：2021 *International Review of Financial Analysis* 论文 metadata / portability audit（Crossref + OpenAlex + CentAUR / title page）+ Binance USDⓈ-M public-data portability probe（8 liquid majors，`15m` parent，近约 `1000` bars）
- 主题类型：raw alpha
- 基础 alpha：**最近上涨里，越不是靠单根极端尖刺（MAX spike）撑出来的走势，越更像可延续的真 momentum；反过来，尖刺型 lottery path 更该打折。**
- 是否可独立复现：是
- 是否可直接落地完整策略（entry/exit/sizing/risk/cost）：是
- 主题标签：raw-alpha / cross-sectional / momentum / max / lottery / spike-filter / path-quality / 15m / 5m / paper / public-data / cost / risk
- 证据类型：论文 metadata 证据 + public-data portability probe

## 1. 这次看了什么
看的是 **Li, Urquhart, Wang, Zhang (2021), _MAX momentum in cryptocurrency markets_**，发表在 **International Review of Financial Analysis**。这篇从标题就很直白：它不是在问“crypto 有没有 momentum”，而是在问 **momentum 里有没有一类更值得买的路径形态**。

我把它先读成一个很 desk-friendly 的问题：**如果过去收益差不多，那些没有单根极端拉升、而是一路慢慢爬上去的币，后面是不是更值得追？**

## 2. 核心结论
- 这篇东西的 base alpha 很清楚：**不是所有“过去涨了”的东西都一样，靠一根大尖刺冲上去的走势，往往不如平滑爬升的走势可追。**
- 对 short-cycle crypto desk，最容易落地的版本不是复杂择时模型，而是一个 **MAX-aware momentum score**：在过去 `L` 根里，既看总收益，也看有没有单根特别夸张的 spike。
- 我做了一个最小 portability probe：在 Binance USDⓈ-M `BTC/ETH/SOL/BNB/XRP/DOGE/ADA/AVAX` 上，用 `15m` bars 做 cross-sectional 排名，比较三类壳：
  1. plain momentum
  2. `ret - recent MAX` 的去尖刺 momentum
  3. 只在低 MAX half 里做 momentum
- 结果很明确：**低 MAX 过滤确实有用，但主要体现在 long leg；long-short 在当前样本里还是不够厚。**
  - `L=16, hold=1` 时，plain top1 long 约 `0.16 bps/次`，`ret-max` 约 `0.16 bps/次`，**低 MAX half top1 long 约 `0.56 bps/次`**。
  - `L=16, hold=2` 时，plain top1 long 约 `0.16 bps/次`，`ret-max` 约 `0.36 bps/次`，**低 MAX half top1 long 约 `0.49 bps/次`**。
  - 但 `top1-bottom1 long-short` 还是负的，说明它更像 **更干净的 momentum entry filter**，还没长成一个能直接扛成本的强 long-short。
- 一句话核心结论：**MAX 不是单独的 alpha，本质上是在告诉你：momentum 里该把“尖刺型假强势”和“平滑型真强势”分开。**
- 一句话证明方式：**论文题眼就是 MAX 与 momentum 的关系，我把它压成一个公开 Binance 的 `15m` cross-sectional probe，看去尖刺后是否比 plain momentum 更能保留延续边。**

## 3. 为什么和当前 desk 有关
它很适合当前阶段，因为它直接回答的是一个更底层的问题：**同样是短周期上涨，什么样的上涨值得追？**

这比单纯再做一个 breakout 参数更有用，因为它把“上涨”再拆了一层：
- 是一路爬上去，还是一根 spike 拉上去？
- 是可复现的 continuation，还是 lottery 式的噪音？

## 3.5 策略拆解（必填）
- 方向属性：cross-sectional momentum / continuation
- 基础 alpha：**低 MAX 路径比高 MAX 路径更容易延续**
- regime：更适合趋势展开、而不是单根脉冲后立刻退潮的阶段
- filter / veto：recent MAX、单根收益占比、路径尖刺度、上行连续性
- risk / sizing / execution overlay：`15m` parent 排名，`5m` child execution；可加 time-stop、maker-first、单 leg 仓位上限、以及对高 MAX 名称降权

## 4. 可复刻的最小实验
- 研究假设：在同样过去收益下，**recent MAX 更低** 的币，下一段延续更强。
- 一个可计算定义：最近 `L=16` 根 `15m` K 线，计算总收益 `ret_L`；再取最近单根最大收益 `MAX_L = max(1-bar return)`；构造 `score = ret_L - MAX_L` 或者直接只在低 `MAX_L` half 里做 momentum。
- 最小回测切口：8 个 liquid majors 上，每根 `15m` bar 做 `top1 long`、`bottom1 short`、`top1-bottom1 long-short` 三种最小壳；先把 child execution 放到 `5m`。
- 最该先看哪 1~2 个指标：**低 MAX 过滤相对 plain momentum 的增量 bps**、**增量是否能覆盖 round-trip friction**。如果 long-short 仍然过不了成本，就把它降成 entry filter，不要硬装成独立 alpha。

## 5. 当前 verdict 与下一步怎么测
### 当前 verdict
- **有用，但还没厚到能直接长成强 long-short alpha。**
- 在当前 `15m` 8 币样本里，低 MAX half 的 long leg 比 plain momentum 更好，说明它确实在剔掉一部分“假强势”。
- 但 long-short 仍为负，意味着它目前更像 **momentum quality filter / router**，而不是成熟的独立组合壳。

### 下一步怎么测
1. **把 MAX 定义做细**：不只看最近单根最大收益，再加 `max bar contribution / total ret`、`max-to-avg ratio`、`上行 bar 占比`，看能不能比单一 MAX 更稳。  
2. **从 top1 扩到 top decile**：8 币 universe 太小，先扩到更大的 liquid universe，再看 low-MAX momentum 的横截面是否更像真 alpha。  
3. **换更快周期**：如果 `15m` 还是太钝，试 `5m`，看“尖刺过滤”是不是更符合 crypto 的短周期结构。  
4. **先作为 router 再上仓**：如果它持续只改善 long leg，就把它明确降级为 momentum / breakout 的 admission filter，而不是独立主策略。

## 6. 风险与保留意见
- 这轮拿到的是论文 metadata / title 线索和公开数据 portability probe，**没有全文方法细节**，所以这里是 desk-oriented 的 first verdict，不是严格复刻。
- `MAX` 只是“尖刺度”的粗代理，不等于论文内部完整定义；若后续拿到全文，再回头对齐定义。
- 当前样本只覆盖近约 `1000` 根 `15m` bar，属于短窗 first verdict。

## 7. 来源
- Li, Y., Urquhart, A., Wang, P., & Zhang, W. (2021). *MAX momentum in cryptocurrency markets*. *International Review of Financial Analysis*, 77, 101829.
- DOI: `https://doi.org/10.1016/j.irfa.2021.101829`
- Readable / landing URL: `https://doi.org/10.1016/j.irfa.2021.101829`
- Crossref: `https://api.crossref.org/works/10.1016/j.irfa.2021.101829`
- OpenAlex: `https://api.openalex.org/works/https://doi.org/10.1016/j.irfa.2021.101829`
- CentAUR author page: `https://centaur.reading.ac.uk/view/creators/90009470.html`
- 本地 probe artifact:
  - `reports/artifacts/quant_digests/2026-04-23_maxmom_proxy_grid.csv`
