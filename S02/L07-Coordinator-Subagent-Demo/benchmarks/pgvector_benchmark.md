# pgvector — RAG Benchmark Report

Source URL: https://supabase.com/blog/pgvector-performance-2025
Report date: 2025-01-15
Vendor: Supabase / PostgreSQL community

## Test setup

- Index type: HNSW
- Vector dimensions: 768
- Index size: 10,000,000 vectors
- Hardware: 8 vCPU, 32 GB RAM, NVMe SSD
- Workload: Top-10 nearest-neighbor retrieval

## Latency

- p50 query latency: 14 ms
- p99 query latency: 52 ms

## Quality

- Recall@10: 0.94

## Cost

- Storage cost: $0.020 per GB-month (managed Postgres baseline)

## Notes

pgvector tested as a PostgreSQL extension on standard managed
infrastructure. Strong fit for teams already running Postgres.
