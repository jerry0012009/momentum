# Goal：因子评价口径升级、Universe 对照与 Crypto-native 因子扩展

目标：在现有因子库 workflow 基础上，修正当前评价口径中 funding、cost、bucket tail、review reason 不完整的问题；再做 1-2 个 universe 对照研究；最后从已有仓库、已有项目、或 momentum 现有 rank300+ 候选中优先扩展 crypto-native 因子。要求代码简单、清晰、可维护，不重复造轮子，不急于进入生产信号或实盘 gate。

## 总原则

- 因子评价本身是一个 workflow；如果修改评价逻辑，必须同步更新 workflow 的入口、输出、scorecard/meta、页面 JSON、HTML 展示、校验脚本和必要测试，确保后续新因子自动走正确流程。
- 优先复用现有因子库、scorecard、factor evaluation、post-intake、redundancy、ML prototype、signal evaluation 相关代码，不创建新的复杂平行体系。
- 研究输出集中放在现有 factor run / diagnostics / site asset 路径中，避免到处新增分散表格。
- funding 缺失不能静默填 0 后当真实结果；必须报告 coverage、missing symbol/time、partial diagnostic 边界。
- funding 频率可能是 1h、4h、8h 或其他间隔；实现时应基于时间戳和有效覆盖窗口计算，而不是硬编码固定 1h funding。
- 不触碰 broker、exchange、live trading、production execution 相关代码。
- 当前阶段只做研究诊断、workflow 升级和可审计输出，不做交易收益声明。

## 阶段一：升级因子评价 Workflow

目标：把 funding-aware、cost-aware、tail-aware、review-reason-aware 评价纳入现有因子评价流程。

需要完成：

- 梳理现有 factor evaluation workflow：从因子 intake、post-intake、scorecard、review status、页面 JSON 到 HTML 展示，明确哪些脚本和产物需要同步更新。
- 在现有 meta / scorecard / summary 中加入清晰字段，而不是新建复杂表体系：
  - price-only RankIC / spread；
  - after-funding RankIC / spread；
  - funding coverage；
  - cost-adjusted spread 或 break-even cost；
  - bucket tail diagnosis；
  - review reason 拆分。
- 将 `review required` 拆成可解释原因，例如：
  - funding coverage insufficient；
  - funding-adjusted edge flips；
  - RankIC/spread direction conflict；
  - tail concentrated；
  - mean/median split；
  - cost too thin；
  - unstable across horizons；
  - data quality / source coverage issue。
- 确保后续新增因子自动生成这些字段，并能在 factor evaluation 页面看到。
- 保留 price-only 评价用于判断排序信息，但把 after-funding / cost-aware 评价作为经济有效性的重要参考。

完成标准：

- 现有因子评价 workflow 可以一键或按既有步骤重跑。
- 新增 funding/cost/tail/review 字段进入现有 scorecard/meta/page，而不是散落在孤立研究表里。
- 对 funding 覆盖不足的因子有明确状态和解释。
- 页面能解释为什么一个因子是 pass、review、hold，而不是只有模糊标签。
- 相关 schema check、smoke test、页面 JSON check、`git diff --check` 通过。

## 阶段二：Universe 对照研究

目标：判断当前 top50 current-listed universe 是否导致 alpha 过薄、spread 反向、bucket tail 污染。

需要完成：

- 先审计仓库已有 universe、cache、manifest、labels、factor values，不要直接大规模重建。
- 优先做 1-2 个最小 universe 对照，例如：
  - static top50 long window vs dynamic top50 current-listed；
  - dynamic top50 baseline vs crypto-native enriched dynamic top50；
  - 如已有数据支持，再考虑 top20 liquid majors 或 age/liquidity filtered。
- 对照指标应复用升级后的评价口径：
  - price-only RankIC / spread；
  - after-funding RankIC / spread；
  - cost-aware spread；
  - bucket tail diagnosis；
  - conflict/review reason 分布。
- 如果 top20、top100/top150、age/liquidity filtered 尚无完整数据，输出清晰缺口和下一步计划，不要硬造复杂 pipeline。

完成标准：

- 至少完成 1-2 个 universe 的最小事实对照，或明确说明缺哪些 canonical 数据无法完成。
- 给出 top50 current-listed 是否特殊的事实判断。
- 结论整合到现有研究摘要或 factor evaluation / signal evaluation 页面中。

## 阶段三：Crypto-native 因子扩展

目标：在评价尺子校准后，再扩展更可能带来厚 alpha 的 crypto-native 因子。

原则：

- 优先从已有仓库、已有项目、公开 alpha 候选、或 momentum 现有 rank300+ 中获取和改造，不重复造轮子。
- 每批控制在 8-12 个因子，按公式和数据源相似度分批。
- 每批完成后走现有 intake + post-intake + redundancy + scorecard + page workflow。
- 不为单个因子引入脆弱、复杂、不可维护的新数据依赖。

优先方向：

- funding / basis / carry；
- taker buy/sell pressure；
- listing age / event / abnormal volume；
- volatility regime / liquidity / spread / depth proxy；
- BTC/ETH beta residual；
- sector / theme relative strength。

暂缓方向：

- open interest / liquidation / crowding，除非已有可靠 canonical data contract 和覆盖审计。

完成标准：

- 产出下一批 8-12 个 crypto-native 因子候选清单，说明来源、公式、数据需求、适用 horizon、预期解决的问题。
- 已有数据能支持的因子优先 intake；数据不成熟的因子进入 backlog，不强行实现。
- 新因子自动经过升级后的 funding/cost/tail/review workflow。

## 最终交付

- 一个干净、可维护的因子评价 workflow，而不是临时研究脚本堆叠。
- 一个事实驱动的 universe 对照结论。
- 一批来源清楚、数据可支持、公式可解释的 crypto-native 因子扩展计划或落地结果。
- 页面能向研究者解释：哪些因子真的有排序信息，哪些因子扣 funding/cost 后仍有经济意义，哪些只是 tail 或 universe 造成的假象。
- 不做生产、实盘、交易收益声明。
