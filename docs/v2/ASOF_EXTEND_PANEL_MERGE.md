# Asof-extend panel merge (research)

> 2026-10-10 · `promotion_approved=false` · do **not** mutate `data/local_market/1c85...`

## Rule

For instrument `i` and session `t`:

1. Read `d0_as_of` from `data/v2/asof_extend_202610/manifest.json` (default **2026-06-30**).
2. Prefer the **D0** bar when `t <= d0_as_of` and the bar exists under
   `data/local_market/1c85fd9aceaa03c3c4863bec/panels/<i>.parquet`.
3. Else use the **asof_extend** bar when `t > d0_as_of` from
   `data/v2/asof_extend_202610/panels/<i>.parquet`.

Equivalent concat (read-only)::

    concat(D0[session <= cutoff], extend[session > cutoff])

Implemented by `quantlab.data.v2_readers.load_merged_panel` /
`load_merged_calendar`. Consumed by `quantlab.universe.d1_masks.build_d1_masks_for_session`.

## Calendar

Prefer `data/v2/asof_extend_202610/calendar.parquet` (superset through
**2026-10-09**). Fall back to D0 calendar if extend is absent.

## Known extend gaps (research quality notes)

| Column | Extend reality | Eng research handling |
|---|---|---|
| `open_status` | usually `derived` | allowed in research mode; strict mode rejects |
| `amount` | often all-null (Tencent day kline) | U30 waived when median NaN + amount gap (`waive_u30_on_amount_gap`) |
| `turnover` | often null | panel-derived float_mktcap may fail → use V2 float_mktcap carry |
| `limit_up` / `limit_down` | often null | limit blocks do not fire |
| `is_st_at_open` | column missing | ffill from D0 half, else default False + note |

None of these gaps may flip `promotion_approved` or `sw_l1_promotable`.

## float_mktcap on late sessions

V2 table is currently asof **2026-06-30**. For sessions after that date, Eng
**carries** the stale asof with note
`float_mktcap_stale_asof_research_carry` — research-only, not promotion-grade.
