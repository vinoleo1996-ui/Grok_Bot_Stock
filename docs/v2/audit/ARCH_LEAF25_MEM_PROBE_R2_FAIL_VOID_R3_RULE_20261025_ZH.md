# Arch 裁定：叶25 mem_probe r2 FAIL → VOID + r3 滤子修

| 项 | 值 |
|---|---|
| 角色 | QuantLab Arch |
| 时刻 | `2026-10-25T12:32:48-04:00`（America/New_York） |
| **结论** | **FAIL_TYPE**（非破帽）· `.ok` **VOID** · 令 AI **r3** |
| live / promotion | false / false |

## 0. 一句话

单次实峰跑 **FAIL** rc=1：`end_date` 滤子用 **string**，现盘 PIT 为 **`timestamp[us]`**（Arrow `greater_equal` 无核）。peak_kb=**208312** ≪ C4 → **C4=PASS**。`.ok` `cd230f9c…` **已 VOID**；QUIET **已 lift**；**不解阻 X2**；AI **ai_no_retry** 停本票，交 **r3** 类型对齐滤子后再另审另签。

## 1. 证据钉

| 件 | sha / 值 |
|---|---|
| AI 回执 | `d01f95c0b2f5ffa59c56787bfeb09c30c980de6a0f0ce10f10998c4fe3050454` |
| 原 `.ok`（签发） | `cd230f9c2aa9fc8de7fc538fb1f04ded8d9c20463f24b88b6c0f76950ec34279` |
| VOID 归档 | `output/ai_factory/_consumed/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R2.cd230f9c.VOID.FAIL_TYPE.20261025T1232ET.ok`（内容含 footer 后 sha `5df99eb799a9058c3f442f8c8b95b41309ba2f54a236fa047b8045806bd5b47f`） |
| ET_TS | `20261025_122704` |
| peak_kb / C4 | **208312** / PASS（limit 1331200） |
| 异常 | `ArrowNotImplementedError: greater_equal (timestamp[us], string)` @ `_read_pit_projected` |
| 盘证 schema | `financials_pit_tushare` / `cashflow_pit_tushare` / `balancesheet_pit_tushare` 之 `end_date` = **timestamp[us]**（本机只读核） |
| r2 审阅（签前） | `1b706f9b40054b69e4e25968f9a3d20ec530965a4dfaf3a61be7584d3296b0c7` PASS_WITH_CONDITIONS（未覆盖本类型坑） |

## 2. 动作本回合

1. **VOID** 现盘 `.ok`（single_use；**禁**再消费同票重跑）  
2. **lift** `RESEARCH_QUIET.lock`  
3. **裁定 r3**（见下）；**不**签新 `.ok` 本回合  
4. X2 / NEED_MEM_PROBE：**仍挡**

## 3. 令 AI · r3 最小修

在仍钉 C4/tmp/HI_LIQ 单块 / wrapper v5 / 禁抬帽 / 禁 `1c32ab1e` 下：

1. `_read_pit_projected`：`end_date` 滤子与盘类型对齐——用 **`pd.Timestamp` / `datetime64[us]`**（或先列投影再 pandas 滤），**禁止**对 `timestamp[us]` 列喂 YYYYMMDD string 进 pyarrow filters。  
2. 修正误导注释「end_date stored as YYYYMMDD string」。  
3. `_norm_pit` / asof 路径复核 us vs ns / tz（审计清单：merge 两侧精度一致）。  
4. 交：DIFF + COVER + CMD + 新脚本 sha；**禁自开跑**；Arch 另审 PASS 后主另排窗再签新实峰 probe `.ok`。  
5. **禁申 X2.ok**；禁复用 VOID `cd230f9c`。

## 4. 给主

- SW 实修：准备即日；P0 签执行最早周一双通后——已知。  
- mem_probe：等 AI r3 包 → Arch 另审另签 → 另短窗。  
- 叶27 分块 `282d6ca1…` 另窗排队不变。
