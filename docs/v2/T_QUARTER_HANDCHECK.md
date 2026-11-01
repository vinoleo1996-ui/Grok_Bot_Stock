# T 国债期货单季手工核对（合成数据）
脚本：`scripts/t_quarter_handcheck.py`（独立于引擎的逐日 pandas 计算 vs `run_weight_schedule(futures=...)`）。
**价格是合成的**：box 上没有国债期货日线（`data/v2/futures/raw/daily` 只有 IF/IH/IC/IM），Data 补齐后需用真实结算价重跑。

情景：2 手 T2412 多头，2024-09-23 开盘建仓；交割月首个交易日 2024-12-02 开盘平旧开新换到 T2503（`roll_days=0`，不进交割月）；2024-12-31 开盘平仓。
乘数 10,000（价格按百元面值报价，面值 100 万），手续费 3 元/手，保证金 2%。

结果：逐日 VM、保证金、现金三列与引擎最大绝对差 < 1e-9 元。

```
           contract  settle      vm  fee   margin       cash
date                                                        
2024-09-20      NaN     NaN     0.0  0.0      0.0  3000000.0
2024-09-23    T2412  105.60  1600.0  6.0  42242.0  3001594.0
2024-09-24    T2412  105.42 -3800.0  0.0  42166.0  2997794.0
2024-09-25    T2412  105.42   100.0  0.0  42168.0  2997894.0
           contract  settle      vm   fee   margin       cash
date                                                         
2024-11-28    T2412  105.10 -1600.0   0.0  42040.0  2991494.0
2024-11-29    T2412  104.98 -2300.0   0.0  41994.0  2989194.0
2024-12-02    T2503  104.79  -200.0  12.0  41916.0  2988982.0
2024-12-03    T2503  104.73 -1200.0   0.0  41892.0  2987782.0
2024-12-04    T2503  104.54 -3900.0   0.0  41814.0  2983882.0
           contract  settle      vm  fee   margin       cash
date                                                        
2024-12-30    T2503   104.3  1400.0  0.0  41722.0  2979282.0
2024-12-31      NaN     NaN   300.0  6.0      0.0  2979576.0
fills: [('2024-09-23', 'T2412', np.float64(2.0), 105.525, np.float64(6.0), 'order'), ('2024-12-02', 'T2412', np.float64(-2.0), 105.04, np.float64(6.0), 'roll_out'), ('2024-12-02', 'T2503', np.float64(2.0), 104.855, np.float64(6.0), 'roll_in'), ('2024-12-31', 'T2503', np.float64(-2.0), 104.32000000000001, np.float64(6.0), 'order')]
hand: VM -20400.00 fees 24.00 final cash 2979576.00 | engine: VM -20400.00 fees 24.00 nav 2979576.00 roll_cost 12.00 margin_peak 42386.00
max abs diff per column: {'vm': 2.6147972675971687e-10, 'margin': 0.0, 'cash': 4.656612873077393e-10}
OK: engine == hand calc
```

## 真实行情复核（2026-10-12）
`python scripts/t_quarter_handcheck.py --real`：T2412/T2503 用 data/v2/futures/raw/daily 的真实日线（交易所 pre_settle，涨跌停开启）。手算与引擎逐日 VM、保证金、现金最大差 < 1e-9。2 手多头：VM +34,600，费用 24（开 6、展期 12、平 6），期末 3,034,576，保证金峰值 43,544。输出 output/v2_proto/t_quarter_handcheck_real.txt。注意该脚本用旧规则 roll_days=0（交割月首个交易日 12-02 展期），只为核对记账；正式研究用 bond_roll_rule="earlier_of"。
