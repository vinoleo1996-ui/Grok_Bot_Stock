# AI · 叶35 ETF Passive Flow Pressure Overlay X2 RUNNING_ACK

- status: IN_WINDOW_EXECUTE_RUNNING
- ET_TS: `20261027_135145` America/New_York
- OUT: `output/ai_factory/_leaf35_etf_passive_flow_pressure/20261027_135145`
- MATCH pins:
  - `.ok` `ARCH_RUN_AUTH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_HILIQ.ok` sha8=`10927bd9`
  - QUIET `RESEARCH_QUIET.lock` sha8=`c8d95fee` holder=`leaf35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2`（勿 lift）
  - SIGNED sha8=`3b25f9d7`
  - script sha8=`25ae4572` UNCHANGED
  - Arch 审 sha8=`ea395dc4`
  - leaf33 sha8=`afbbe7e7` UNCHANGED
- window: `13:38`→`15:08` expires `15:12` ET；prelaunch 时刻仍 IN_WINDOW
- pgrep kline/export_static/snapshot/gen: EMPTY
- rss_limit_mb: 1500（禁抬）；peak_proof: REQUIRED
- pid: `470069`（execute STARTED；IN_WINDOW）
- ≠X2 ACCEPT；leo_notify=false；live=false
