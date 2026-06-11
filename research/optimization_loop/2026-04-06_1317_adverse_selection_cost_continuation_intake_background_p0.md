# 2026-04-06 13:17 UTC — adverse-selection cost continuation fresh intake first verdict

## Target
- `research/quant_digests/2026-04-06_1224_adverse-selection-cost-continuation-alpha.md`

## Policy / state frame used
- 按 `BOT2_BOT3_POLICY.md` 执行当前轮首个 `pending` fresh intake
- 不重排 `cycle_plan`，只处理这一项

## What changed
**First verdict：`adverse-selection cost continuation` 不进入前排，直接记为 `background / P0`。**

## Why
1. **独立主语不够新。** 这条线的核心仍是 `information-bearing aggressive flow -> next 1~3 bar continuation`，与现有池内已经单独 intake 过的 `OFI / L1 imbalance / VWAP pressure / spread gate` 单资产 microstructure continuation 家族高度同构；目前新增的只是把 continuation 解释成 `signed ASC-share`，而不是给出一个明显不同于旧 `order imbalance / OFI` 的可审计交易对象。
2. **当前 digest 自己也把最关键验证定义成 horse race against OFI / taker imbalance。** 这等于承认首要问题不是“alpha 壳已清楚”，而是“它会不会只是旧 microstructure 信号换术语”。在这个问题没被回答前，不足以拿到 `keep_P1`。
3. **after-cost 壳仍停在设想层。** 文中虽给了 `1m/3m/5m` 的 entry/exit/cost 轮廓，但还没有任何公开 quote/trade 口径下的 recent-window 分桶、单调性、成本后 pocket 或 transfer 证据；相较于池内已有 microstructure intake，这一步没有把执行诚实边界往前推进。
4. **数据工程门槛高，但不是唯一 decisive blocker；更关键是主题重叠。** quote 历史难拿本身可以接受，但若 base alpha 足够独立仍可先留作 `P1`。本对象的问题在于：在没有实证 horse race 前，它更像现有 microstructure continuation 的学术重命名，而不是值得单占 survivor 锁位的新 family。

## Comparison against existing pool
- `2026-03-25_0318_single-asset-microstructure-taker-alpha.md` 已明确 intake `OFI + VWAP pressure` 单资产超短 continuation raw alpha
- `2026-04-01_0138_l1-imbalance-vwap-spread-direction-alpha.md` 已明确 intake `L1 imbalance × VWAP-to-mid × spread gate` 短周期 continuation raw alpha
- 本轮 adverse-selection digest 新增的核心信息，尚不足以证明它在对象定义上独立于上述家族

## Runtime consequence
- 不分配新 `Rank`
- 不占用 `Fresh intake / Survivor / Active P2 / Paper launch queue`
- 直接写入 `Background pool`

## Result sentence for state
`adverse-selection cost continuation` fresh intake first verdict 完成：对象的核心仍是 `information-bearing aggressive flow -> next 1~3 bar continuation`，与池内既有 `OFI / L1 imbalance / VWAP pressure` 单资产 microstructure family 高度同构，且公开 quote/trade 口径下尚无能证明其独立 after-cost pocket 的 horse-race 证据，因此本轮不保留为新前排对象，直接记入 `background / P0`。

## Publish note
- 已尝试刷新首页：
  - `bash /root/clawd/jerry/momentum/scripts/publish_homepage_index.sh`
  - 以及直接调用 `build_site_index.py`
- 两次都卡在 `build_site_index.py` 阶段并超时（30s / 120s），因此本轮首页未完成刷新；该问题不影响本轮 state / verdict 已生效。
