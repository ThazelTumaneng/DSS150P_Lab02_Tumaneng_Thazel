"""Starter validation checks for raw outputs."""
from pathlib import Path
import json
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'raw'
STATE = ROOT / 'state'

def main():
    print("Running raw output validations...")
    
    # Assert expected raw files and manifest exist
    manifest_path = RAW / 'files' / 'manifest.json'
    events_path = RAW / 'api' / 'events.jsonl'
    watermark_path = STATE / 'api_watermark.json'
    
    assert RAW.exists(), "Raw directory missing!"
    assert (RAW / 'files' / 'customers.csv').exists(), "Missing customers.csv in raw area"
    assert (RAW / 'files' / 'orders.json').exists(), "Missing orders.json in raw area"
    assert (RAW / 'files' / 'products.parquet').exists(), "Missing products.parquet in raw area"
    assert manifest_path.exists(), "File ingestion manifest.json missing!"
    assert events_path.exists(), "Raw API events.jsonl missing!"
    assert watermark_path.exists(), "API watermark state file missing!"
    
    # Validate API events file (uniqueness, metadata fields, timestamp parseability)
    event_ids = set()
    max_updated_at = None
    
    with open(events_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            record = json.loads(line.strip())
            
            # Check required metadata enrichment fields
            assert '_ingested_at' in record, f"Missing _ingested_at on line {line_num}"
            assert '_source' in record, f"Missing _source on line {line_num}"
            assert 'event_id' in record, f"Missing event_id on line {line_num}"
            assert 'updated_at' in record, f"Missing updated_at on line {line_num}"
            
            # Check event_id uniqueness (deduplication check)
            eid = record['event_id']
            assert eid not in event_ids, f"Duplicate event_id found: {eid}"
            event_ids.add(eid)
            
            # Verify updated_at is parseable as a timestamp
            try:
                parsed_time = datetime.fromisoformat(record['updated_at'].replace('Z', '+00:00'))
            except ValueError as e:
                raise AssertionError(f"Invalid timestamp format in event {eid}: {e}")
                
            # Track max updated_at for watermark comparison
            if max_updated_at is None or record['updated_at'] > max_updated_at:
                max_updated_at = record['updated_at']

    # Assert watermark equals max updated_at
    watermark_data = json.loads(watermark_path.read_text())
    saved_watermark = watermark_data.get('updated_at')
    
    assert saved_watermark == max_updated_at, (
        f"Watermark mismatch! Saved watermark ({saved_watermark}) "
        f"does not match max raw updated_at ({max_updated_at})"
    )
    
    print("SUCCESS: All raw output validations passed cleanly!")

if __name__ == '__main__':
    main()