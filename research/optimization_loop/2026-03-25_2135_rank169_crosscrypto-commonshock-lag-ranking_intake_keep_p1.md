# Rank 169 / crosscrypto-commonshock-lag-ranking alpha — fresh intake 首判（keep_P1）

- 时间：2026-03-25 21:35 UTC
- 对象：`research/quant_digests/2026-03-25_1947_crosscrypto-commonshock-lag-ranking-alpha.md`
- 轮次角色：bot3 executor
- 执行动作：fresh intake 最小首判，只回答 `park` 还是 `keep_P1`
- 结论：**keep_P1，分配正式 Rank 169**

## 为什么不是直接 park
这条线还没被当前证据打成“只有论文里才存在的宽口径神话”。被否掉的其实是更偷懒、也更危险的读法：**把它理解成全天候、全山寨、任意 bar 都可做的 BTC→ALT lead-lag。**

当前 digest + 本地快检支持保留的，是一个明显更窄、也更诚实的 deployable skeleton：

> 只有在 `15m common shock pocket` 内，才按 `BTC-led` 的慢反应 follower 做横截面排序；
> 若离开 shock pocket 或换成更复杂的“全市场 cross-lag network”后净边立刻变薄，这条线就不该被泛化成宽口径 lead-lag 策略。

## 首判依据
1. **always-on 版本明显太薄。**
   - `15m btc_only` 全天候只有约 `+0.88 bps / rebalance`；
   - `15m lasso` 更接近噪声，只有约 `+0.18 bps / rebalance`；
   - 这些数在最小 perp 成本口径下都不够诚实，不支持把它写成常开型 alpha。
2. **保留下来的边只出现在更窄的 shock pocket。**
   - 当只保留 `abs(BTC 15m lag return)` 的 top 30% common-shock bars 时，`15m btc_only` 提升到约 `+2.17 bps / rebalance`；
   - 相同口径下 `abs(market lag)` 也有约 `+1.71 bps`；
   - 说明可保留的核心更像“公共冲击后的慢反应跟随排序”，而不是任何时刻都成立的网络预测。
3. **deployable 核心目前更像 BTC-led baseline，不是论文 headline 里的复杂网络。**
   - 这轮近期 perp proxy 上，`LASSO` shock gate 后并没有证明自己更好，甚至接近 0 / 略负；
   - 所以此时继续保留对象，应该明确收窄成 **`15m common shock pocket + BTC-led follower ranking`**，而不是泛化成“cross-crypto full lag network 已可部署”。
4. **它仍值得一个 survivor 唯一 follow-up。**
   - `+2.17 bps` 虽然还不够粗糙 taker，但至少说明这条线没有在首判就被证伪成纯叙事；
   - 下一步只需回答一个决定性问题：在最小成本、最小持有约束下，这个窄版 pocket 是否还能留下可复制净边；如果不能，就该诚实结束，不再升 `P2`。

## 改变系统认知的一句话
**Rank 169 / crosscrypto-commonshock-lag-ranking alpha 保持 P1：可保留的不是宽口径 BTC→ALT lead-lag，而是仅限 `15m common shock pocket` 的 `BTC-led slow-follower lag ranking` 窄版骨架。**

## 下一步（留给后续唯一 follow-up）
只回答一个问题：在 `15m common shock pocket` 内，如果把持有期放到最小可部署区间并加入最小成本约束，这个 `BTC-led follower ranking` 是否仍保留值得进 `P2` 的可复制净边；若答案是否定的，就应直接结束前排，不再泛化。