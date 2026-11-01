# AI 情报师：宏观与财报扩展的自动化设计（草案）
1. 日历文件 data/v2/intel/event_calendar.csv
   - 字段：event_id, type(earnings/macro/fed_speech), ticker_or_series, datetime_et, confirmed(bool), source_url, consensus_json, importance(high/med), a_share_map。
   - 每周日手工或半自动更新一次。来源：BLS/BEA/美联储日程页、公司 IR。二手来源记 confirmed=false。
2. 模式
   - pre：事件前 T-24h，输出预期和情景表（偏热/符合/偏冷）及传导链。
   - post：事件后 T+30min，抓取官方稿件，计算实际值与共识的差，重写简报对应章节，并按严重度打 high 标记。
   - holdings：每天读取最新纸面权重，只读，用模板生成观点表。
3. 实现
   - 在 research/intel/intel_run.py 增加 --mode macro_pre|macro_post|holdings 参数，复用 intel_common。
   - 输出 MACRO_EARNINGS_BRIEF_latest.md，同时在 history/ 下留时间戳副本。
4. 约束：只读权重；python3；RSS≤1.5GB；不起 8787；无来源的数字一律写「不确定」；live=false。
5. 暂不建设：实时行情接入；CME 直连（需要验证访问方式）。
