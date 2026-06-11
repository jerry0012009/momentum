# 别把 breakout 的 follow-up 继续写成单一路径：`FT/NFT 双路由 + killzone` 更像 15m 的 honest post-break verdict 骨架
- 时间：2026-03-23 03:12 UTC
- 类型：GitHub 仓库 + Binance 公共数据最小快检 + 论文辅助证据
- 主题标签：breakout-short/v3/final-verdict/follow-up/fibonacci/retest-hold/ema/psar/ft-nft/router/killzone/regime/filter/crypto/15m
- 证据类型：工程证据（仓库源码与README）+ 本地最小代理快检 + 论文证据（机制辅助）

## 1. 这次看了什么
这轮主看 **carlosrod723 / MQL5-Trading-Bot（2025~2026）**。它最值得 desk 偷的旁支，不是“SMC 全家桶”，而是一个很实用的结构：
**在同一套 H4 Fib 上下文里，把 post-break path 明确拆成 `FT（Follow-Through）` 与 `NFT（No Follow-Through）` 两条路，再叠一个时间门（killzone）。**

我把它翻译成当前三条收口线的问题：
> `V3 final-verdict / breakout-short follow-up` 不该再只问“破了没”，而应先问“这是 FT 还是 NFT 路径”；
> `Fib retest_hold` 不该单独扛真相，应作为 FT/NFT 路径里的上下文约束。

## 2. 核心结论
- **一句话结论**：对 15m 来说，先做 `FT/NFT 路径路由`，再做方向判决，比“单一路径 breakout follow-up”更诚实；killzone 更像 FT 路径的放行器，而不是 NFT 的通用救命阀。  
- **一句话证明方式**：先读仓库里 `SFT/FT/NFT/CT` 的策略拆分，再用 Binance USDⓈ-M 公共 15m K 线（BTC/ETH/SOL，120d）做 next-bar-open、8-bar 持有、双边 6bps 成本的最小代理快检，对比 FT/NFT 在 killzone 与 offhours 的净表现。

关键数据点（本地最小快检）：
1. **FT 路径在 killzone 明显改善，offhours 明显恶化**  
   - `ft_long`: all `-13.20 bp` → killzone `+0.81 bp` vs offhours `-16.65 bp`  
   - `ft_short`: all `-7.58 bp` → killzone `+6.54 bp` vs offhours `-11.06 bp`
2. **NFT 路径即使进 killzone 也没被“自动救活”**  
   - `nft_long`: killzone `-5.47 bp`  
   - `nft_short`: killzone `-7.28 bp`
3. **跨资产一致性更偏向 FT，不偏向 NFT**  
   - `ft_long` killzone 下 `pos_asset_ratio=0.67`  
   - `ft_short` killzone 下 `pos_asset_ratio=0.67`  
   - NFT killzone 仅 `0.33`

## 3. 为什么和当前项目有关
- **对 `V3 final-verdict / breakout-short follow-up`**：最直接。先把 post-break 路径判成 FT 或 NFT，再做 continuation / failure 判决，能减少“同一把尺子量两种行情”的误判。  
- **对 `Fibonacci confirmation / retest_hold`**：仓库里 Fib 更像上下文（premium/discount）而不是独立主触发；这和当前“别把 retest_hold 写成单独硬门”的方向一致。  
- **对 `EMA / PSAR raw alpha focus`**：这次证据继续支持“角色分工优先于参数炼丹”——EMA/PSAR更适合当 context/filter/exit 组件，不应替代 post-break 路由层。

## 3.5 策略拆解（必填）
- 方向属性：顺势延续（FT）+ 失败反转（NFT）双路径
- 基础 alpha：breakout 后路径分类（follow-through vs rejection）
- regime：killzone（London/NY overlap）优先用于 FT 路径放行
- filter / veto：`FT/NFT router` + 时段 gate（killzone / offhours）
- risk / sizing / execution overlay：NFT 侧默认降仓或更严格 veto；FT 侧允许正常仓位与 follow-up

## 4. 可复刻的最小实验（下一步怎么测）
**研究假设**：15m 上不是“所有 breakout 后续都同分布”；FT 与 NFT 的成本后分布不同，且 killzone 主要改善 FT。  

**最小口径（公开可得）**：
- 数据源：Binance USDⓈ-M Futures 公共接口 `/fapi/v1/klines`（公开可得，无需私钥）
- 更新频率：15m K线（可扩展到 5m）
- 资产：BTC/ETH/SOL
- 样本：最近 120d
- 执行：`signal on close -> next bar open`，持有 8 bars，双边成本 12 bps

**最小实现步骤**：
1. 用“前4根区间突破 + 连续收盘”定义 FT proxy；
2. 用“前一根假突破长影线 + 当前反向确认”定义 NFT proxy；
3. 按 `killzone(08,09,13,14 UTC)` 与 offhours 拆桶；
4. 对每桶算 `mean_net_bp / win_rate / pos_asset_ratio`。

**下一步正式化测试（建议）**：
- 把当前 8-bar 固定出场升级成 `triple-barrier`（tp/sl/time）版本；
- 将 `FT/NFT router` 接到 `breakout-short V3 final-verdict` 前置层，做 A/B：
  - A：现有单一路径
  - B：先路由再判决
- 重点看：`post-cost return`、`positive window ratio`、`trade count` 是否同时可接受。

## 5. 风险与保留意见
- 本轮是最小代理快检，不是完整策略回测；信号定义还需与你当前主线代码精确对齐。  
- killzone 在 crypto 24/7 市场未必长期稳定，需滚动窗口做稳健性检查。  
- 仓库本体是 MT5/M15 语境，直接迁移到你当前执行栈前，需要先做 friction 对齐（手续费、滑点、成交约束）。

## 6. 来源
1. **Carlos Rodríguez. (2025/2026). _MQL5-Trading-Bot_. GitHub Repository.**  
   - Venue/Type: GitHub Repository  
   - DOI: N/A  
   - Readable URL: <https://github.com/carlosrod723/MQL5-Trading-Bot>  
   - Repo URL: <https://github.com/carlosrod723/MQL5-Trading-Bot>  

2. **Jasiak, J., & Zhong, C. (2024). _Intraday and daily dynamics of cryptocurrency_. International Review of Economics & Finance.**  
   - DOI: <https://doi.org/10.1016/j.iref.2024.103658>  
   - Readable URL: <https://doi.org/10.1016/j.iref.2024.103658>  
   - 用途说明：辅助支持“crypto 存在显著 intraday 时段结构”，用于本轮 killzone 设定的机制背景（非本轮主证据）。

3. **Binance Futures API Docs (public market data).**  
   - Venue/Type: Official API Documentation  
   - DOI: N/A  
   - Readable URL: <https://binance-docs.github.io/apidocs/futures/en/#kline-candlestick-data-market_data>  
   - Endpoint: `GET /fapi/v1/klines`
