import pyarrow.parquet as pq, sys
for p in sys.argv[1:]:
    f=pq.ParquetFile(p); print(p, f.metadata.num_rows); print("  ", f.schema_arrow)
