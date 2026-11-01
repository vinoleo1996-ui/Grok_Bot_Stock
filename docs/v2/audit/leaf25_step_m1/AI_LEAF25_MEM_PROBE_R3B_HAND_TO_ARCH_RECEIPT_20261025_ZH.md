# 叶25 mem_probe r3b · 交手 Arch 回执（PIN 路径已钉）

| 项 | 值 |
|---|---|
| 角色 | QuantLab AI |
| 时刻 | `2026-10-25T13:11:30-0400`（America/New_York） |
| 对齐 | 主令·急 + Arch PIN `340ab36c` / 审阅 `74149e29` |
| live | **false** |

## 交付 sha256（全长）

| 件 | sha256 |
|---|---|
| COVER | `c5d0c4f0af18b3e23a9242717f3f68e9e31b2023c6940dcc98ed3eeda6cf5e8d` |
| CMD | `689dc55cee93b4cc767b5fe19ecd0e89cbb2182350ac5da7a2d5bf2ee6919770` |
| DIFF | `e92796fe1b502f661eea5c9ac470005aaa184699d394b1f6ba375b35c3711fe7` |
| 本回执 | `110f484f32a84e9ab6d3bf49a6b94623a5028ce199f6b7e88e64f05a02b31ce1` |
| Arch PIN wrapper | `b1208d3c075b0ea06ba9a484d8a42833f3efb223defbada02d135dfe624f88d5` |
| 探针 UNCHANGED | `8da4f2e663d83956b4b9910fc958f9decba68f40327f2089610ffa1a069600ea` |

## 启动路径

`bash docs/v2/audit/cmc_wrapper_c5_tighten_20261025/cmc_wrapper_v6_C5TIGHTEN_b1208d3c.sh`（**必须** PIN 文件名；draft 同 sha 仅旁证；**禁** `e03a61b6`）

## 自检

- PIN MATCH；`bash -n` → **PASS**
- 禁复用 `c5e54085`/`cd230f9c`/`1c32ab1e`；禁 `--c5-ignore`；≠X2
- 排窗错开叶27 **14:00–14:45 ET**（拟 ≥15:00）

## 下一跳

请 Arch **另审另签**新 `.ok`（拟名 `output/ai_factory/ARCH_RUN_AUTH_LEAF25_MEM_PROBE_R3B.ok`）。AI 不停同票、不自开跑。live=false。
