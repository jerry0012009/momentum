# 2026-04-08 21:44 UTC · bot6 park-reframe · Rank 7

## 0) 本轮选择
- 本轮对象：`Rank 7`
- 选择原因：用户本轮限定看 `Rank 1~37` 已 park 条目；在这一段里，`Rank 7` 距上次 park-reframe 复盘（`2026-03-25 20:03 UTC`）已超过 7 天，且已有 `Rank 7b / 7c` 两条窄派生可作为对照，适合做一次低频复核。

## 1) 原 rank 为什么 park？
- 原始 blocker 不是“某个小参数没调对”，而是 **direct blended entry vote 这层职责本身不诚实**：把 continuation、retest、趋势对齐、风险过滤混成一个统一入场器，结果只有极稀疏 pocket 看起来勉强存活。
- clean replication 与后续 honesty recheck 的共同结论是：一旦把交易数调回更可交易的密度，`6~20bps` 成本下跨资产结果会一起转负；说明改善主要来自 **砍样本**，不是稳定 edge。
- 因此原 `park` 的审计含义仍成立：**Rank 7 作为 standalone adaptive trend combo / blended vote entry，不值得重开。**

## 2) 它更像 hard park 还是 soft park？
- 结论：**soft park，但已经很接近 hard park（针对 Rank 7 本体读法）**。
- 理由：主题本身不是完全没信息；残余信息早已被更诚实地降级到 `Rank 7b`（session 级单 lane allocation overlay）与 `Rank 7c`（mid-score band-pass overlay）。
- 也就是说，soft 的部分只存在于“角色降级后的 residual”，不是原 rank 本体仍可救。

## 3) 现有证据里有没有“可救信号”？
- 有，但都是**已被消费过的可救信号**：
  - `Rank 7b` 已把它收敛成 `one-regime-per-session` 的 allocation overlay；
  - `Rank 7c` 已把它收敛成 `mid-score band-pass` 的 admission/sizing overlay。
- 本轮新增旁证主要来自：
  - `2026-04-08_2006_laggedfeature-consensusgate-direction-shell.md`
  - `2026-04-08_0405_htf-ema-rsi-pullback-trend-shell.md`
- 这两条新 digest 的共同方向，不是支持把 Rank 7 再救回一个新的 blended combo，而是继续说明：
  1. **agreement / consensus 更适合当 shell 或 gate**，不是自动变成独立 alpha；
  2. **HTF trend + pullback** 更像新的单策略宿主，而不是给 Rank 7 再多加一层投票组件。
- 所以可救信号存在，但没有形成超出 `7b / 7c` 的新 residual。

## 4) 最值得改的唯一一刀是什么？
- 本轮判断：**没有新的唯一一刀。**
- 原 Rank 7 唯一诚实的一刀，仍然只到：
  - `Rank 7b`：把 blended entry vote 降级成 session 级 lane allocation overlay；或
  - `Rank 7c`：把 blended entry vote 降级成中段放行、尾部降仓/否决的 band-pass overlay。
- 再往前硬切新一刀，大概率只是把同一 residual 换措辞重讲，不足以形成新的独立 reframe hypothesis。

## 5) 是否值得形成新的 derived hypothesis？
- 结论：**不值得。**
- 本轮最终 verdict：`keep_park`

## 6) 为什么这次不 draft 新 hypothesis？
- 因为新证据没有推翻原 blocker，只是在继续强化一个旧结论：
  - `combo / consensus / alignment` 这类信息，若还有价值，也更适合做 **overlay / shell 的从属层**；
  - 一旦把它重新写成新的 direct-entry 方案，就很容易再次滑回“低 retention 美化”的老问题。
- 同时，`2026-04-07 23:29 UTC` 已有 `Rank 7c residual intake guard — stay in park_reframe`，高置信指出：这条 residual 目前**更适合继续留在 park_reframe 队列，而不是入前排 fresh intake**。

## 7) 本轮结论（按固定问答模板压缩）
1. 原 rank 为什么 park？
   - 因为 blended combo 作为 direct entry 主要靠极稀疏交易数减亏，成本与可交易性一恢复就转负。
2. 更像 hard park 还是 soft park？
   - 对 Rank 7 本体读法已接近 hard；整体仍记作 `soft park`，因为 residual 已被 `7b / 7c` 吸收。
3. 有没有可救信号？
   - 有，但已被 `7b / 7c` 消费；本轮没有新增未消费 residual。
4. 最值得改的唯一一刀是什么？
   - 无新增唯一一刀；仍只到既有 `7b / 7c`。
5. 是否值得形成新的 derived hypothesis？
   - 不值得，维持 `keep_park`。

## 8) 对队列文件的落点
- `docs/PARK_REFRAME_QUEUE.md`：仅追加一条 `Recently reviewed`
- `research/park_reframe/INDEX.md`：仅追加本轮索引
- 不改 `docs/TODO.md`
- 不新增 `Rank 7d`

## 9) Git / 提交
- 本轮只做最小文件更新。
- 未做 git commit：当前工作区存在与本轮无关的脏文件/临时文件，避免混入 bot6 这次的最小改动。