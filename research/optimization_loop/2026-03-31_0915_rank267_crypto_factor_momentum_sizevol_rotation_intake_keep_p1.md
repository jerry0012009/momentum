# Rank 267 / crypto factor momentum × size/vol rotation / fresh intake keep_P1

- 时间：2026-03-31 09:15 UTC
- 执行轮次：bot3 13 分钟自动执行
- 对应 cycle_plan 小点：`crypto factor momentum × size/vol rotation`
- 来源：`research/quant_digests/2026-03-31_0828_crypto-factor-momentum-sizevol-rotation-alpha.md`
- 新分配 Rank：`267`（检索当前仓库未发现已占用 `Rank 267`）

## 本轮只回答一个问题
这条线是否已经构成一个可独立进入前排的 fresh intake 主语，还是只是“多因子解释层/综述壳”？

## 读取后的关键判断
1. 这条线的主语是明确的，不是泛多因子综述：
   - 第一层是可独立交易的横截面 sleeves：`size`、`low dollar-volume-vol`、`short-horizon momentum`。
   - 第二层是 sleeves 自身的 `factor momentum rotation`：最近表现更强的 sleeve 加权，较弱 sleeve 降权或停权。
2. digest 已给出最小可执行骨架：
   - universe：Binance USDT perp、过去 30d ADV 前 20~40、上市满 90d；
   - ranking：`24h/72h/7d`；
   - holding：`4h/12h/24h`；
   - 执行：`15m` TWAP；
   - 风控：美元中性 + 近 BTC beta 中性；
   - 成本：先用 `10 bps one-way` 做第一轮否决。
3. 因此它已经满足“独立 raw alpha skeleton”这一条，不需要依附 breakout / retest / pattern 才能成立。
4. 但当前证据仍主要来自 academic 周频/日频结论与 desk 级迁移 spec，还没有完成 perp 可交易 universe 下最关键的最小诚实验证：
   - sleeve 静态净边是否仍在；
   - sleeve rotation 是否真的增益，而不是只增加 turnover；
   - 在 beta 中性、资金费/手续费/滑点后是否还剩可审计 pocket。

## 本轮 verdict
`Rank 267` 的 fresh intake 首判成立，记 `keep_P1`。

更具体地说：
> 它已经不是“因子解释层壳”，而是具备独立 entry/portfolio/exit/cost 骨架的 `cross-sectional factor momentum × size/vol rotation` raw alpha；但由于还缺少 perp universe / turnover / cost / beta-neutral 口径下的最小净收益验证，本轮只进入 `keep_P1`，不直接升 `P2`。

## 为什么现在不直接升 P2
因为当前最缺的不是“再读几篇因子论文”，而是一个最小但诚实的实证问题：

- 静态 `size / low-vol / short-horizon momentum` sleeves 在可交易 perp 池里还有没有 gross edge？
- `winner rotation` 能不能在净值上真正筛掉烂 sleeve，而不是只放大换手？
- 如果 rotation 没增益，这条线是否应收缩成“静态 sleeves 主策略 + rotation 砍掉”的更窄 spec？

这些都还没有被最小矩阵验证过，所以还不够进入 `P2 admission`。

## 下一步最便宜的 survivor check（供 bot2 下轮决定是否排）
只做一个 `3 sleeves × 3 ranking lookbacks × 3 holding windows` 的最小矩阵：
- sleeves：`size / low-vol / momentum`
- ranking lookback：`24h / 72h / 7d`
- holding：`4h / 12h / 24h`
- overlay：先比 `static equal-weight sleeves` 与 `winner-only / top-2 sleeves rotation`
- 输出：gross/net spread return、turnover、BTC beta、capacity proxy、rotation 前后 Sharpe 变化

## 本轮改变的系统认知
`crypto factor momentum × size/vol rotation` 不是泛因子综述，而是已经够格进入前排的独立 raw alpha 主语；但它目前仍停留在 `keep_P1`，因为真正决定能否升 `P2` 的 perp 成本后净边还没被最小验证。 
