# factors

## 职责
- 计算可复用因子（尽量保持纯函数）

## 当前状态
- 目录占位完成

## M1 进展
- 已新增 `chip_distribution.py`（筹码分布估算）
- 已新增 `endpoint_nadaraya_watson.py`（因果版 NW 平滑）
- 已新增 `confirmed_extrema.py`（显式延迟确认的极值点，锚点值来自原始 `high/low`）
- 已新增 `pytrendline_bridge.py`（MIT 外部库 `pytrendline` 的轻量接入层）

## M1 下一步
- 补均线、ATR 等基础因子
- 把筹码分布输出接入策略特征工程
- 继续围绕 `NW + confirmed extrema` 做更成熟的外部逻辑对齐，不急着扩展业务层
