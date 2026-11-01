import pyarrow.parquet as pq,sys
for f in sys.argv[1:]:
    m=pq.ParquetFile(f).metadata; print(f,m.num_rows,m.num_row_groups); print(pq.read_schema(f))
print([l for l in open('/proc/self/status') if l.startswith('VmHWM')])
