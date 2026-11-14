# Architecture Documentation

- [System Architecture](system-architecture.md)
- [Low-Level System Design](low-level-system-design.md)
- [ELT Pipeline Architecture](elt-pipeline-architecture.md)
- [Data Architecture](data-architecture.md)
- [Deployment Architecture](deployment-architecture.md)

## Verification status
The deployed ALB paths were smoke-tested: Streamlit `/` returned HTTP 200; FastAPI `/health` returned `healthy`; `/pipeline/runs` returned a successful response; `/ml/prediction-runs` returned six runs.

The 150-concurrent-user section is a proposed capacity design, not a completed load-test result. The frontend service was verified with desired count 1. Do not claim 150-user capacity until load tests pass and autoscaling/session affinity/database limits are validated.
