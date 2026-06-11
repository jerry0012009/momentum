# 2026-03-15 07:54 UTC · Light Strategy Review

## 本轮一句话判断

这轮出现了一个**比研究方向更紧急的执行层问题**：`bot3` 的 cron 被重新写成了 `systemEvent`，而当前 job 本身是 `isolated` 模式，结果最近连续 3 轮都被系统直接 `skipped`（报错：`isolated job requires payload.kind=agentTurn`）。因此，本轮 bot2 的最小必要动作不是再讨论哪个 alpha 更值得，而是**先把 bot3 的执行链路修回可运行状态**；否则后面的研究 steering 再正确也会空转。

## 当前 strongest evidence

1. **在 bot3 被 skip 之前，breakout 主线的方向校准是有效的。**
   - 最近连续有效产出已经把 breakout admission gap 压到很硬：
     - `down-tail coverage = 0/100`
     - `mixed-tail protective gate` 有希望
     - `blunt pure-down 0.5x` 不是现成补丁
   - 这说明研究方向本身没有坏，坏的是后续执行链路。

2. **当前最新异常是 execution wiring，不是研究结论冲突。**
   - 最近 bot3 run history 已显示连续 `skipped`：
     - `isolated job requires payload.kind=agentTurn`
   - 也就是说，当前不是 bot3“选错题”或“不会跑”，而是根本没有被正确唤醒。

3. **EMA / breakout / Fibonacci 的 admission ranking 目前不需要改。**
   - `EMA` 仍是 `closest to paper`
   - `breakout` 仍是 `needs one more gate`
   - `Fibonacci` 仍是 `park / archive`
   - 这轮没有新的研究证据推翻这件事。

## 本轮最小必要修复

1. **把 `bot3-momentum-auto-opt-13m` 改回 `payload.kind=agentTurn`**
   - 保持：`sessionTarget=isolated`
   - 保持：`delivery.mode=none`
   - 恢复并重写最新的 deployment-facing prompt（含 breakout hard-gate priority、EMA honesty-only、execution hygiene、publish homepage index、email summary）

2. 修复目标不是“换研究方向”，而是：
   - 停止每 13 分钟白白 skip
   - 让 bot3 重新回到前几轮已经跑顺的 breakout admission 主线

## 下一步优先级 Top 1~3

### Top 1. 先确认 bot3 下一轮不再 skip

当前最重要的不是新结论，而是确认：
- `agentTurn` wiring 已恢复
- bot3 能重新产出 optimization loop 记录和邮件

### Top 2. 恢复后，继续沿 breakout 主缺口推进

恢复运行后，仍然优先：
- `down+flat mixed-tail` protective honesty
- breakout 是否该收敛成更窄 scope 的 conditional alpha

### Top 3. EMA 继续只允许补真实 honesty

若切回 EMA，也仍只应做：
- `沪深300ETF 1d` 的 promotion / forward honesty
- 或 secondary batch 的真正 forward 复核

## 本轮改动

- **本轮不改 `docs/TODO.md`**
- **本轮不改 project-level ranking / verdict**
- **本轮只修 bot3 cron 的 payload wiring**

原因：
1. 当前最紧急问题是 bot3 连续 skip；
2. 不先修执行链路，后面所有 steering 都会失效；
3. 研究方向本身目前没有出现新的跑偏证据。

## 网页 / 表达建议

1. 当前网页口径短期不需要再改；核心问题不是页面表达，而是 bot3 重新恢复执行。
2. 主页 index 本轮按要求轻量刷新即可，确保 Recent Activity 继续反映最新状态。

## cron / 节奏建议

1. **bot2：40m 继续保持。**
2. **bot3：13m 继续保持，但必须先修复 `agentTurn` wiring。**
3. **bot7：继续不改。**

## paper trading admission verdict

- **closest to paper：`EMA baseline family`**
  - 当前最缺 gate：`shadow-only pocket` 的更长 promotion honesty / secondary batch 的真正 forward honesty

- **needs one more gate：`support_breakout_v0`**
  - 当前最缺 gate：`pair-conditioned sizing` 的迁移性证明
  - 最新 hard-gap 读法不变：
    - `down-tail coverage = 0/100`
    - `mixed-tail protective gate` 有希望
    - `blunt pure-down 0.5x` 不是现成补丁

- **park / archive：`Fibonacci`**

## 风险与不确定性

1. 当前最大风险不是研究错，而是 bot3 若继续 skip，会让主线推进突然中断。
2. 由于这个问题是 cron payload/wiring 级别的，哪怕 prompt 内容再好，也会被直接绕过。
3. 因此这轮最合理的 bot2 动作不是继续发明新问题，而是先把执行链路修好，再观察下一轮是否恢复真实产出。 
