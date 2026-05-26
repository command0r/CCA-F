# Weaviate — RAG Benchmark Report

Source URL: https://weaviate.io/blog/rag-benchmarks-2025
Report date: 2025-01-29
Vendor: Weaviate

## Test setup

- Index type: HNSW
- Vector dimensions: 768
- Index size: 10,000,000 vectors
- Hardware: 8 vCPU, 32 GB RAM, NVMe SSD
- Workload: Top-10 nearest-neighbor retrieval

## Latency

- p50 query latency: 11 ms
- p99 query latency: 38 ms

## Quality

- Recall@10: 0.95

## Cost

- Storage cost: $0.022 per GB-month (Weaviate Cloud Standard)

## Notes

Weaviate offers hybrid search (vector + keyword) and module-based
integrations for transformer-based reranking. Balanced choice across
latency, recall, and feature breadth.
