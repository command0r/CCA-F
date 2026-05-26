# Qdrant — RAG Benchmark Report

Source URL: https://qdrant.tech/benchmarks/2025-rag-report
Report date: 2025-02-08
Vendor: Qdrant Solutions

## Test setup

- Index type: HNSW with quantization
- Vector dimensions: 768
- Index size: 10,000,000 vectors
- Hardware: 8 vCPU, 32 GB RAM, NVMe SSD
- Workload: Top-10 nearest-neighbor retrieval

## Latency

- p50 query latency: 8 ms
- p99 query latency: 29 ms

## Quality

- Recall@10: 0.96

## Cost

- Storage cost: $0.014 per GB-month (Qdrant Cloud, standard tier)

## Notes

Qdrant ships purpose-built for vector workloads. Scalar quantization
reduces memory footprint at modest recall cost. Strong choice for
latency-sensitive RAG.
