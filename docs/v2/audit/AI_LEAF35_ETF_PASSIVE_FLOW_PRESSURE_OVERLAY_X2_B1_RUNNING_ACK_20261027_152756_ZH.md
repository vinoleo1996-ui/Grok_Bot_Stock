# AI · 叶35 B1 ETF Passive Flow Pressure Overlay X2 RUNNING_ACK

- status: IN_WINDOW_EXECUTE_RUNNING
- ET_TS: `20261027_152756` America/New_York
- OUT: `output/ai_factory/_leaf35_etf_passive_flow_pressure/20261027_152756`
- MATCH pins:
  - `.ok` `ARCH_RUN_AUTH_LEAF35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2_HILIQ.ok` sha8=`eb70eef4` / `eb70eef4386ae856f5f0b02733bca718ff96125765556fd72b70fefc82f94921`
  - QUIET `RESEARCH_QUIET.lock` sha8=`ef9b69b4` holder=`leaf35_ETF_PASSIVE_FLOW_PRESSURE_OVERLAY_X2`（勿 lift）
  - SIGNED sha8=`65d89851`
  - script sha8=`434ff42c` only（禁 `25ae4572` 当活脚本）
  - Arch 审 sha8=`df19dd2a`；补丁审 `31a08790`
  - leaf33 sha8=`afbbe7e7` UNCHANGED
- window: `15:19`→`16:49` expires `16:53` ET；prelaunch 时刻仍 IN_WINDOW
- healthz:8795 quiet=true live=false gen/snapshot/kline=false child_pids={}
- pgrep kline/export_static/snapshot/gen: EMPTY
- rss_limit_mb: 1500（禁抬）；peak_proof: REQUIRED；share_PIT=B1
- pid: pending_executor_start
- ≠X2 ACCEPT；≠叶36；leo_notify=false；live=false
