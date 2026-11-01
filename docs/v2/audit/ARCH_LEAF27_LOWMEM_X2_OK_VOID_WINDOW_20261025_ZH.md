# Arch 叶27 LOWMEM×x2 — 事故旁证（VOID_WINDOW↔RESTORED）**已废止**

- 更新时刻：2026-10-25T11:55:39-04:00（America/New_York）
- **终态**：正式 VOID 见 `docs/v2/audit/ARCH_LEAF27_LOWMEM_X2_OK_VOID_20261025_ZH.md` sha8=`951141dd`
- 归档：`output/ai_factory/_consumed/…8bcd79dc.VOID.ABORT_RSS.20261025T1152ET.ok`
- **live 路径必须空**；**禁止**再 RESTORED / 再挂回
- 背景（历史）：11:49 曾误 VOID_WINDOW→11:50 RESTORED 供 AI 跑；随后 run1/run2 ABORT_RSS（1933/1877）→主 park→Arch 正式 VOID
- 现盘：无 `RESEARCH_QUIET.lock`（废窗后勿再为 12:45 挂锁）
- live=false
