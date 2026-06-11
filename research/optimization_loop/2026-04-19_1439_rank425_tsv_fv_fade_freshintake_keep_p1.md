# Rank 425 / EMA fair-value dislocation × non-panicked TSV flow fade — fresh intake first verdict

- 时间：2026-04-19 14:39 UTC
- 对象：`research/quant_digests/2026-04-19_0146_tsv-fv-dislocation-fade-alpha.md`
- 结论：`keep_P1`
- Rank：`425`

## 本轮只回答的最小 blocker
`15m alt-proxy long fade` 在统一成本、next-bar entry 与样本稀疏约束下，是否仍留下可复制 pocket。

## 本轮使用的最小证据
来源：`reports/artifacts/quant_digests/2026-04-19_tsv_ema_fv_fade_15m_events.csv`

对 `bucket=alt_proxy & side=long` 做最小复核：
- 全部 `15m alt long`：`n=105`，`gross=+1.49bps`，统一 `8bps` 后为负，不足以单独成立。
- 但 digest 已点名的最强 pocket —— `15m alt long & tsv_z>=0`：
  - `n=64`
  - `gross=+13.50bps`
  - `median=+13.71bps`
  - `win_rate=57.8%`
  - 统一 `4/6/8bps` 后仍约 `+9.50 / +7.50 / +5.50bps`
  - 分布在 `ADA/AVAX/DOGE/LINK/LTC/XRP` 六个符号，不是单一币一次尾部事件
- 浓度上仍有 `LINK` 偏强，但 `AVAX/LTC/XRP/ADA` 也保留正均值，因此当前不能把它判成“只有单币硬撑”。

## 诚实收口
这条线**不是**“所有 EMA 偏离都能做 fade”的通用裸 alpha；可保留的仅是更窄的 `15m alt-pocket / long-only / non-panicked TSV` 版本。

但就本轮要求的最小 blocker 而言，它已经满足 `keep_P1`：
- 已经是 next-bar / bar-close 后可诚实执行的事件口径；
- 在统一成本下仍保住正净边际；
- 样本量虽不大，但 `64` 笔覆盖 `6` 个 alt，不是单一尾部幻觉；
- 因此它值得进入一次 survivor follow-up，而不是直接回收 `background/P0`。

## runtime impact
- 分配新正式身份：`Rank 425`
- Fresh intake first verdict：`keep_P1`
- `Surviving candidate slot` 切换为 `Rank 425`，保留唯一一次 follow-up 预算

## 一句话结果
`Rank 425 / EMA fair-value dislocation × non-panicked TSV flow fade` 的 first verdict 已诚实收口：通用 EMA 偏离 fade 不成立，但 `15m alt-proxy long fade + tsv_z>=0` 仍保留 `n=64`、统一 `8bps` 后约 `+5.5bps` 的跨六个 alt pocket，因此本轮保留为 `keep_P1` 并进入 survivor 槽位。

## 尾步执行状态（内部）
- homepage publish：`bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh` 异步返回 `signal SIGKILL`，按 policy 视为**非阻断尾部失败**，不回滚本轮 verdict / state / log。
- email notify：`python3 /root/clawd/skills/codex-quota-email/scripts/send_text_email.py ...` 已成功发送。