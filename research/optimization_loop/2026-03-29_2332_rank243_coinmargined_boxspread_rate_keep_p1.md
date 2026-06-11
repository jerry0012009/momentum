# Rank 243 / coin-margined same-expiry box-spread implied-rate alpha — fresh intake keep_P1

- 时间：2026-03-29 23:32 UTC
- 执行角色：bot3
- 当前执行小点：`coin-margined same-expiry box-spread implied-rate alpha`
- 对应来源：`research/quant_digests/2026-03-29_2218_coinmargined-boxspread-rate-alpha.md`
- Assigned Rank: `Rank 243`

## 结论
**first verdict = `keep_P1`。**

这条对象足够独立，应该正式记为：
`Rank 243 / coin-margined same-expiry box-spread implied-rate alpha`

更准确的 desk 主语是：**`USD-normalized executable box APR`**，也就是在同标的、同到期、不同执行价的 coin-margined options box spread 上，寻找经统一结算单位后仍存在的 rich/cheap implied financing pocket，并用 `mid vs executable` 的四腿诚实对照来判断它是否真能吃到。

## 为什么不是泛 options 平台 / background only
这条线已经满足 fresh intake 应有的独立对象边界：

1. **本体清楚**
   - 不是“options 平台里有个 box 模块”；
   - 而是明确的 `same-expiry box implied-rate dislocation` raw alpha。

2. **最小实验清楚**
   - 同 expiry strike pair 重建 long/short box；
   - 统一到 USD / 可比结算单位；
   - 同时输出 `repo_raw_profit`、`USD-normalized mid profit`、`USD-normalized executable profit`；
   - 再比较 `mid APR` 与 `executable APR` 的塌缩幅度。

3. **honesty cut 也清楚**
   - 当前最关键的不是继续找更多 paper pocket，
   - 而是先回答：单位修正后，这些 pocket 在四腿 bid/ask + fee 下还剩多少。

4. **与现有前排对象正交**
   - 它补的是 crypto options relative-value / implied financing 这一支，
   - 不是已有 perp momentum / funding carry / pairs family 的重述。

因此它不该被写成“泛 options 套利平台”，也不该因为 repo 口径有问题就直接扔回 background；更诚实的位置是 **先保留为 `keep_P1`，给一次 survivor follow-up 去做 executable honesty cut。**

## 为什么这轮不能直接升 P2
当前 blocker 很单一，而且足够 decisive：

### 唯一高杠杆 blocker
**repo 当前在 coin-margined 语境里混用了 `K_high-K_low` 的 USD payoff 和 BTC 计价 premium；在把 premium 统一映射到同一结算单位、并换成四腿 executable 口径之前，quoted box profit 不能当成可实现 APR。**

digest 里已经给出很明确的负面例子：
- repo 原公式会把某些 box 误读成接近 `+$9,000` 的“利润”；
- 单位修正后 pocket 会明显缩小；
- 再换成四腿 executable bid/ask 后，mid 上看似为正的机会可能直接转负。

这已经足够说明：
- 这条线**值得独立保留**；
- 但当前还不能把 “mark/mid 上看见 pocket” 直接写成 admission 级别的可交易 edge。

所以本轮最诚实的 verdict 只能是 `keep_P1`，而不是 `promote_P2`。

## 本轮会改变系统认知的话
`Rank 243 / coin-margined same-expiry box-spread implied-rate alpha` 已足够收敛成一条独立的 options relative-value raw alpha：应以 `USD-normalized executable box APR` 为正式主语保留到前排，而不是泛写成 options 套利平台；但当前 repo 仍存在 coin-margined 单位混用，且尚未完成四腿 executable 口径，因此这轮只够 `keep_P1`，不直接升 `P2`。

## 唯一合法下一步（survivor follow-up）
若给这条对象唯一一次 survivor follow-up，应该只做一件事：

1. 只抓 Deribit BTC 近 2~3 个近月 expiry；
2. 只扫近 ATM、宽度 `500~5000 USD` 的 strike pair；
3. 用统一结算单位重算 box payoff 与 premium；
4. 同时输出 `mid APR` 与 `executable APR`；
5. 明确回答 executable 口径下是否仍周期性留下正 edge pocket。

如果这一步证明 executable edge 仍能过线，再考虑升 `P2`；
如果一上 executable 口径就系统性塌掉，就应在 survivor 用尽后转 background。

## 一句话 result
`Rank 243 / coin-margined same-expiry box-spread implied-rate alpha` 已形成边界清楚、可复现、且能直接做 `mid vs executable` honesty 对照的新对象，因此正式记为 fresh intake `keep_P1`；但在完成 USD-normalized 四腿 executable 口径前，不得写成 `P2`。