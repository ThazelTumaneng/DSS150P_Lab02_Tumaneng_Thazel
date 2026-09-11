# DSS150P Lab 02

Rerunnable Python ingestion pipeline designed for file-based sources and paginated REST APIs with automated validation, deduplication, state tracking, and execution logging.

### Project Structure
* ( 'src/ingest_pipeline.py' ): Main orchestration script managing file hasing manifests and incremental API extraction.
* ( 'src/local_api_server.py' ): Mock REST API server providing paginated event streams.
* ( 'src/validate_raw.py' ): Automated quality assurance and data contract validation suite.
* ( 'raw/' ): Staging directory for immutable raw outputs, including file copies, SHA-256 manifests, and JSONL event logs.
* ( 'state/' ): Persistent state storage tracking high-watermark timestamps ('api_watermark.json') and execution run logs ( 'pipeline_run_log_template.csv' )

### Core Features
* **File Ingestion & Manifest Tracking:** Automatically copies CSV, JSON, and Parquet sources while computing SHA-256 content hashes to prevent duplicate ingestion on reruns. 
* **Paginated REST API Extraction:** Handles multi-page extraction loops, enriching payloads with operational metadata (_ingested_at and _source).
* **Code-driven Deduplication:** Resolves repeated event IDs by retaining the single logical record with maximum ('updated_at') timestamp.
* **Atomic Watermarking:** Updates high watermark state files using atomic rename patterns to ensure system resilience and prevent data loss.
* **Execution Run-Logging:** Appends structured operational metrics (run_id, start/end timestamps, status, records read/written, duplicates removed, and watermark state transitions) to CSV logs.

### Quick Start Guide
* Activate the Virtual Environment
    * source .venv/bin/activate
* Start the Mock API Server
    * python src/local_api_server.py
* Run the Ingestion Pipeline
    * python src/ingest_pipeline.py
* Execute Raw Validation Checks:
    * python src/validate_raw.py

### Creator
* Tumaneng, Thazel J.

### AI Use Disclosure
* Code refinement for '.py' files
* Troubleshooting for system errors during code execution
* Paraphrasing explanations on markdown files


