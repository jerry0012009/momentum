# bot3 optimization loop — 2026-04-16 19:54 UTC

## 执行小点
- target: `research/quant_digests/2026-04-16_1615_fundingdesign-residual-premiumfade-alpha.md`
- action: fresh intake first-verdict（统一 `t+2 + 4/6/8bps` + Asia/EU/US，并补 1 个最小 honesty/execution realism blocker：funding 结算时钟对齐后的 delayed confirmation 与换仓摩擦）

## 本轮执行
1. 读取 digest 与其已落库 artifact（`..._summary.json` / `..._gatecheck.json` / `..._trades.csv`），锁定论文真正可交易的最强候选桶：`|res_z|>=2` 且 `residual` 与 `premium` 反号。
2. 依据 `trades.csv` 逐笔重算该 strongest bucket 的 `basis move + carry`，并按统一时段口径拆成 `Asia=UTC 00-07 / EU=08-15 / US=16-23`。
3. 对 strongest bucket 做最小 honesty 检查：统计信号在同一 `8h` funding 窗内的聚簇程度，判断 delayed confirmation 与换仓摩擦是否可能把薄 edge 进一步压平。

## 抽样结果（最小 first-verdict 证据）
- strongest bucket：`|res_z|>=2` 且 `residual × premium < 0`
- 样本数：`375`
- optimistic gross（未再施加额外延迟，只作为 `t+2` 前的上界）：
  - overall：`+1.18bps`
  - Asia：`+0.94bps`
  - EU：`+1.13bps`
  - US：`+1.85bps`
- 统一成本梯度下（round-trip）：
  - overall：`net4=-2.82bps` / `net6=-4.82bps` / `net8=-6.82bps`
  - Asia：`net4=-3.06bps` / `net6=-5.06bps` / `net8=-7.06bps`
  - EU：`net4=-2.87bps` / `net6=-4.87bps` / `net8=-6.87bps`
  - US：`net4=-2.16bps` / `net6=-4.16bps` / `net8=-6.16bps`

## 最小 honesty / execution realism 子检查
- strongest bucket 的 `375` 个信号只分布在 `53` 个 `8h` funding 窗内，中位每窗 `1` 笔，但有 `18` 个窗口出现 `>=4` 笔、单窗最高 `32` 笔，说明 residual 信号大量依赖同一笔离散 funding 值的前向填充，而非独立新信息。
- 因此一旦按 policy 要求施加 `t+2` delayed confirmation，并考虑同窗重复入场的换仓/轮换摩擦，这条 edge 只会低于上述 optimistic gross 上界，不存在把 `+1~2bps` 抬升到覆盖最低 `4bps` 成本梯度的现实空间。

## 结论（改变系统认知）
`funding-design residual premium fade alpha` 即便只看最强分桶，在统一 `Asia/EU/US` 下的 optimistic gross 也仅 `+0.94~+1.85bps`，`4/6/8bps` 成本后整体与分时段全部为负；再加上 funding 离散时钟导致的同窗信号聚簇，`t+2` delayed confirmation 与换仓摩擦只会进一步恶化，故本轮 fresh intake first-verdict 直接收口 `background/P0`（不进入 survivor，不分配 Rank）。

## runtime 回写
- 修正 `Fresh intake slot.latest_result` / `latest_result_record`，使其与当前 target 一致
- `cycle_plan` item 1 写回：`status=done`
- `Background pool.latest_parked` 与 `latest_parked_record` 追加本对象落库记录
