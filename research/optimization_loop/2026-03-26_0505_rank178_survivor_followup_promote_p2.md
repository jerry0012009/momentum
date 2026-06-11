# Rank 178 / cross-chain-attention-spread-alpha — survivor follow-up 收口（promote_P2）

- Time: 2026-03-26 05:05 UTC
- Target: `Rank 178 / cross-chain-attention-spread-alpha`
- Slot before action: `Surviving candidate slot`
- Verdict: `promote_P2`

## 本轮只回答的一句话
`Rank 178` 的 survivor follow-up 已经足够把对象推进到 `Active P2`：在 intake 现成 `event_panel` 口径下，`leader-chain attention shock -> long leader / short rival basket` 这条 **5-leg cross-chain relative-value spread continuation** 在强 shock 事件上即使扣掉保守多腿成本、并在 BTC 未来 1h 相对平静时仍保留厚净边；但 `3-leg` 压缩版目前还不能当成已成立事实，因此进入 P2 时必须把对象 scope 冻结为 **先验证 5-leg baseline，再决定能否压缩执行**。

## 这次 follow-up 做了什么
本轮只补 survivor 阶段最小但 decisive 的 honesty 检查，不重开 intake：

1. **对 intake 产物里的 `event_panel.csv` 做强 shock 复核**
   - 过滤条件沿用 intake digest 的强版本：`lead_z >= 2.0`、`vol_ratio >= 1.5`、`lead_gap >= 1.5%`
   - 样本数：`423` 次事件
   - `long leader / short equal-weight rivals` 未来 `1h` 平均 spread：`+87.01 bps`
   - 胜率：`69.98%`

2. **把保守多腿成本直接从 spread 毛边里扣掉**
   - 即使按较严的 gross round-trip 成本口径：
     - 扣 `18 bps` 后：平均净边仍约 `+69.01 bps`
     - 扣 `24 bps` 后：平均净边仍约 `+63.01 bps`
     - 扣 `30 bps` 后：平均净边仍约 `+57.01 bps`
   - 对应胜率仍分别约：`63.36% / 61.70% / 60.52%`
   - 结论：**full basket baseline 不是一层极薄、碰到成本就消失的毛刺。**

3. **把 spread 与 BTC 未来 `1h` 回报做最小 beta honesty check**
   - 用同时间戳的 Binance `BTCUSDT` 15m 数据对齐 `event_panel`
   - OLS 口径下：
     - spread 对 BTC 未来 `1h` 的斜率约 `0.394`
     - 截距 alpha 仍约 `+82.92 bps`
   - 进一步只看 `|BTC next 1h return| <= 1%` 的相对平静窗口：
     - 样本数：`379`
     - 平均 spread 仍约 `+75.97 bps`
   - 结论：**这条线并不只是“跟着 BTC 风险偏好一起涨”的单腿 beta continuation。**

4. **额外用同步抓取的 Binance 公共 15m 数据重放一个更严苛的执行版 sanity check**
   - 我把 `ETH/SOL/BNB/AVAX/ARB/BTC` 全样本重新同步拉了一遍，按更偏执行视角的统一 replay 口径重算；这个 replay 下：
     - full 1v4 spread 强 shock 平均只剩约 `+9.21 bps`
     - 压缩 `3-leg` 版本强 shock 平均约 `+10.58 bps`
     - 若分别扣 `30 bps / 18 bps`，两者都会转负
   - 这和 intake artifact 的 `event_panel` 结果存在**显著口径差异**，说明：
     - 当前 alpha 还没到“执行规格完全锁死”的程度；
     - **尤其不能把 `3-leg compression` 当成已经被证实。**

## 本轮为什么仍然是 `promote_P2`，而不是直接 park
因为 survivor 阶段要回答的是：这条骨架值不值得进入更正式的 admission，而不是现在就把所有执行细节盖棺定论。

当前更诚实的判断是：
- **值得保留并升级的对象存在。** intake 主口径下，full basket spread 在强 shock 条件上毛边厚、扣保守成本后仍厚，且 BTC 平静窗口里也没有塌掉；这已经足够支持进入 P2。 
- **但 scope 必须收窄。** 真正进入 P2 的，不是泛泛“跨链 attention 叙事”，也不是“3-leg 压缩版已经成立”，而是：
  - `leader-chain attention shock -> long leader / short equal-weight rival basket (1v4 baseline)`
- **P2 的主问题也因此被明确出来：** 先做 admission 口径的 `spec lock + replay reconciliation`，再决定这条东西能不能压缩成更实盘友好的 `3-leg` 执行版。

## 为什么不是直接 park_to_background
若本轮看到的是：
- full basket 本身扣成本后也没边；或
- 只要剥离 BTC 就完全消失；或
- artifact 与 replay 一致指向“只是 intake 幻觉”

那就应该 park。

但现在不是这个情况：
- artifact 口径下的净边还明显厚；
- BTC 条件化后仍有可观 spread；
- 真正不稳的是**执行规格/压缩版本**，不是 raw alpha 骨架本身已经被证伪。

所以更诚实的动作不是 park，而是**带着冻结过的 scope 升到 P2**。

## 对 runtime 的直接影响
- `Surviving candidate slot` 本轮收口完成，`Rank 178` 不再占用 survivor 槽位
- `Active P2 slot` 切换为 `Rank 178 / cross-chain-attention-spread-alpha`
- 进入 P2 时应明确：
  - **保留**：`leader-chain attention shock -> long leader / short equal-weight rival basket`（5-leg baseline）
  - **未证实，不得默认带入**：`3-leg rival basket compression` 已成立
- 下一个 admission 不应重复“它是不是还有点 raw edge”，而应直接围绕：
  - intake artifact 与同步 replay 的口径差异来自哪里
  - baseline 5-leg spread 的 spec lock / honesty reconciliation
  - 只有在 baseline 站稳后，才继续判断能否压缩到 `3-leg`

## 关键数字（供后续 state / review 复用）
- Intake artifact 强 shock：`423` 事件，平均 spread `+87.01 bps`，胜率 `69.98%`
- 扣 `30 bps` 后净边：`+57.01 bps`
- `BTC |next1h| <= 1%` 子样本：`379` 事件，平均 spread `+75.97 bps`
- 同步 replay 版 full 1v4：平均约 `+9.21 bps`
- 同步 replay 版 compressed 3-leg：平均约 `+10.58 bps`

## 单句结果（供 state / cycle_plan 回写）
`Rank 178 / cross-chain-attention-spread-alpha` 的唯一 survivor follow-up 已诚实收口为 `promote_P2`：当前足以进入 admission 的对象是 `leader-chain attention shock -> long leader / short equal-weight rival basket` 这条 5-leg cross-chain relative-value spread baseline；但 `3-leg` 压缩版尚未被证实，不得一并当成已成立事实。