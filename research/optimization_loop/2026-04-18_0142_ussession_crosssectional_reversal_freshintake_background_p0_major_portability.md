# US-session cross-sectional intraday reversal：fresh intake first verdict = background/P0
- 时间：2026-04-18 01:42 UTC
- 对象：`research/quant_digests/2026-04-17_2350_us-session-crosssectional-reversal-alpha.md`
- 轮次角色：bot3
- 动作：fresh intake first-verdict（补 1 个最小 honesty / execution realism blocker：只检查 impact / participation realism 后，这条线能否诚实迁移到更少腿、更高流动性的 liquid-majors 口径）

## 结论
`US-session cross-sectional intraday reversal` 不值得作为新的 front-slot raw alpha 保留；本轮 first verdict 直接收口 `background/P0`。

## 本轮改变系统认知的一句话
repo 已经把这条线的唯一可迁移方向诚实试穿：25 币 spot 横截面在原始 universe 里虽然 gross 强，但一压到 `BTC/ETH/SOL/BNB` 这类更高流动性实现时，impact 确实下降到 `47.5bps/day` 量级，然而 gross alpha 也同步塌到仅 `4.5bps/day`、连 commission 都覆盖不了，因此这不是可迁移到 liquid-majors desk 口径的 raw alpha，而只是依赖 spot 中小币拥挤/冲击环境的薄 pocket。

## 证据
来自 repo notebook `Intraday_Crypto_Reversal_Project.ipynb` 的最小 honesty 证据：

1. **原始 25 币 close-window 结果并非“轻微成本不够”，而是结构性 cost-dead。**
   - gross alpha：约 `+24.0bps/day`
   - commission：`14.0bps/day`
   - spread：`7.4bps/day`
   - impact：`97.0bps/day`
   - total TC：`118.4bps/day`
   - full-model test Sharpe：`-24.22`

2. **repo 自己已经做了最相关的 portability/honesty 试验：large-caps only。**
   notebook 总结明确写道：
   - Restricting to `BTC/ETH/SOL/BNB` 后，**total TC 降到 `47.5bps/day`**；
   - 但 **gross alpha 仅剩 `4.5bps/day`**；
   - 该 gross 已经 **低于 commission 本身**，说明“更高流动性 + 更少腿”并没有留下可诚实排队的 desk-level edge。

3. **这条线的可见 alpha 主体并不在 majors，而是在中小币横截面。**
   notebook key findings 明说：
   - reversal effect **concentrated in mid-cap assets**；
   - large caps are **too efficiently priced** for the same cross-sectional signal to persist。

4. **因此本轮 blocker 已经一次性收口。**
   cycle_plan 要求只补 1 个最小 honesty / execution realism blocker：检查 edge 能否迁移到更少腿、更高流动性的口径。repo 已经给出足够直接的答案：**不能。**

## 为什么不是 keep_P1
若要 `keep_P1`，至少要能把 survivor blocker 收敛成单一可验证 portability 轴，并保留一个仍可能通向 desk 口径的母板。但这里最关键的 portability 轴已经被 repo 自证为负：
- 原始 alpha 的“存在”与我们真正能做的 liquid-majors 口径不是同一个东西；
- 一旦按诚实执行假设压缩实现，剩下的并不是“薄但可打磨”，而是 **核心 edge 已不再覆盖最低摩擦门槛**。

所以它不应继续占用 fresh/survivor 前排资源。

## 运行态动作
- 当前对象 first verdict：`background/P0`
- 不分配 Rank（因为不是 `keep_P1` 或更高）
- fresh intake front slot 可切到下一条待判对象

## 尾部执行记录（非阻断）
- `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 异步进程最终以 `SIGKILL` 结束；按 policy 视为非阻断尾部失败，不回滚本轮 verdict/state/log。
- 邮件发送步骤已独立完成。
