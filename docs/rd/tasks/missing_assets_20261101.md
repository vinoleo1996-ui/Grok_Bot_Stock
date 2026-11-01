# 2026-11-01 补传资产（已挂现有 Release）

这四个文件已经挂到**现有** tag [`quantlab-data-2026-11-01`](https://github.com/vinoleo1996-ui/Grok_Bot_Stock/releases/tag/quantlab-data-2026-11-01)，没有新建 Release，也没有把二进制写进 git。

| Release 资产 | 解压 / 下载后的约定路径 | 说明 |
| --- | --- | --- |
| `stock_patches_2026-11-01.tgz` | `third_party/Stock-patches/` | 补丁 0012–0021、`Stock-fixes.bundle`、`Stock-repo`。解压目标就是这个目录，不要并进 `quantlab/`。 |
| `ENG_PING_PATHS.json` | `output/d1/ENG_PING_PATHS.json` | 清单快照。本份上传里所有 `promotion_approved*` 都已强制为 false。 |
| `dividends_corporate_actions_2026-11-01.tgz` | `data/v2/corporate_actions/` | 内含 `dividend_tushare.parquet` 与 `dividend_by_exdate_tushare.parquet`。 |
| `README_MISSING_ASSETS.md` | （只读说明） | 与本页对照，不进 git 树。 |

`gh api repos/vinoleo1996-ui/Grok_Bot_Stock/releases/tags/quantlab-data-2026-11-01` 已能看到上述四个资产名。`strategy_promotion_approved` 仍为 false。本页不改选股公式，也不改 `v2_readers`。

## 分红路径（读取器仍指错）

规范表是：

`data/v2/corporate_actions/dividend_tushare.parquet`

不是 `data/v2/dividends/dividends.parquet`。`docs/v2/ACCEPTED_DEFAULTS.md` 与 `docs/rd/tasks/release_audit_20261101.md` 也按这个规范写。按除权日的同伴表是同目录的 `dividend_by_exdate_tushare.parquet`。

当前检出的 `quantlab/data/v2_readers.py` 第 27 行：

`DEFAULT_DIVIDENDS = ROOT / "data" / "v2" / "dividends" / "dividends.parquet"`

`V2DataRoots.dividend_path` 和 `load_dividends()` 的默认值都跟这条。Release 里没有、也不会再提供 `dividends.parquet`。本轮只记缺口，不改读取器。调用方在文件不存在时继续 `FileNotFoundError`，不要另写一张同名空表。

## ENG_PING

资产 `ENG_PING_PATHS.json` 下载后放到 `output/d1/ENG_PING_PATHS.json`。这份里 `promotion_approved_overall`、顶层 `promotion_approved`，以及嵌套的全部 `promotion_approved*` 都是 false。它只记录数据验收路径，不能把 `strategy_promotion_approved` 写成 true。`quantlab/promotion_gate.py` 在总闸为 `None` 时会跟随 ENG_PING；本份 overall 已是 false。

## Stock-patches

解压 `stock_patches_2026-11-01.tgz` 到 `third_party/Stock-patches/`。这是外部补丁包，不是本仓选股公式。上传时从包里的 `Stock-repo/config/secrets.env` 去掉了真实 API key，改成与 `secrets.env.example` 相同的占位内容；仓库是公开的，不能把密钥挂到 Release。

## 流通市值日频仍无 on-disk `available_at`

`data/v2/float_mktcap/float_mktcap_daily_tushare.parquet` 已在 v2 分卷里（见 `docs/rd/tasks/release_audit_20261101.md`）。盘上仍没有 `available_at`。不要用 `trade_date` 冒充公布时点。`quantlab/data/v2_readers.py` 的 `_drop_unpublished` 在缺 `available_at` 列时抛 `ValueError("available_at_missing")`，按会话读日频表会 fail-close。这是正确行为，本轮不改。

## 本轮不做

- 不改 `DEFAULT_DIVIDENDS`，不重写 `v2_readers`。
- 不改选股或配权公式。
- 不把 `strategy_promotion_approved` 或任何 `promotion_approved*` 写成 true。
- 不把这些二进制提交进 git。
