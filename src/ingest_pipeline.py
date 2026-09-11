"""Week 3 starter: rerunnable ingestion to a raw area.
Students implement file ingestion + paginated REST API ingestion + watermark + duplicate prevention.
"""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, shutil
import requests
import csv
import uuid

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; RAW=ROOT/'raw'; STATE=ROOT/'state'
LOG_PATH = STATE / 'pipeline_run_log.csv'
API_URL='http://127.0.0.1:8000/api/events'

def utc_now(): return datetime.now(timezone.utc).isoformat()

def sha256_file(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def load_watermark():
    p=STATE/'api_watermark.json'
    if not p.exists(): return None
    return json.loads(p.read_text())['updated_at']

def save_watermark(value):
    STATE.mkdir(exist_ok=True)
    (STATE/'api_watermark.json').write_text(json.dumps({'updated_at':value},indent=2))

def log_run(source, status, read_count, written_count, dupes_removed, wm_before, wm_after, start_time, end_time, error=""):
    LOG_PATH.parent.mkdir(exist_ok=True)
    file_exists = LOG_PATH.exists()
    
    headers = [
        "run_id", "start_timestamp", "end_timestamp", "status", "source",
        "records_read", "records_written", "duplicates_removed",
        "watermark_before", "watermark_after", "error_message"
    ]
    
    with open(LOG_PATH, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "run_id": str(uuid.uuid4())[:8],
            "start_timestamp": start_time,
            "end_timestamp": end_time,
            "status": status,
            "source": source,
            "records_read": read_count,
            "records_written": written_count,
            "duplicates_removed": dupes_removed,
            "watermark_before": wm_before if wm_before else "N/A",
            "watermark_after": wm_after if wm_after else "N/A",
            "error_message": error
        })
        
def ingest_files():
    start_time = utc_now()
    files_raw_dir = RAW / 'files'
    files_raw_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = files_raw_dir / 'manifest.json'
    
    manifest = []
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        
    existing_hashes = {item['sha256'] for item in manifest}
    
    target_files = ['customers.csv', 'orders.json', 'products.parquet']
    read_count = len(target_files)
    written_count = 0
    dupes_removed = 0
    
    try:
        for filename in target_files:
            src_path = DATA / filename
            if not src_path.exists():
                continue
                
            file_hash = sha256_file(src_path)
            
            if file_hash in existing_hashes:
                print(f"Skipping {filename}: identical content hash already ingested.")
                dupes_removed += 1
                continue
                
            dest_path = files_raw_dir / filename
            shutil.copy2(src_path, dest_path)
            
            file_info = {
                "source_file": filename,
                "ingested_at": utc_now(),
                "sha256": file_hash,
                "bytes": src_path.stat().st_size
            }
            manifest.append(file_info)
            written_count += 1
            print(f"Successfully ingested {filename} to {dest_path}")
            
        manifest_path.write_text(json.dumps(manifest, indent=2))
        log_run("files", "SUCCESS", read_count, written_count, dupes_removed, "N/A", "N/A", start_time, utc_now())
    except Exception as e:
        log_run("files", "FAILED", read_count, written_count, dupes_removed, "N/A", "N/A", start_time, utc_now(), error=str(e))
        raise

def fetch_api_page(page, per_page=20, updated_after=None):
    params={'page':page,'per_page':per_page}
    if updated_after: params['updated_after']=updated_after
    r=requests.get(API_URL,params=params,timeout=30); r.raise_for_status(); return r.json()

def ingest_api():
    start_time = utc_now()
    raw_api_path = RAW / 'api' / 'events.jsonl'
    raw_api_path.parent.mkdir(parents=True, exist_ok=True)
    
    watermark_before = load_watermark()
    print(f"Starting API ingestion with watermark: {watermark_before}")
    
    page = 1
    per_page = 50
    has_more = True
    fetched_records = []
    
    try:
        while has_more:
            data = fetch_api_page(page, per_page=per_page, updated_after=watermark_before)
            items = data.get('items', [])
            
            ingestion_time = utc_now()
            for item in items:
                item['_ingested_at'] = ingestion_time
                item['_source'] = 'rest_api'
                fetched_records.append(item)
                
            has_more = data.get('has_more', False)
            page += 1

        read_count = len(fetched_records)
        if read_count == 0:
            print("No new records fetched from API.")
            log_run("rest_api", "SUCCESS", 0, 0, 0, watermark_before, watermark_before, start_time, utc_now())
            return

        unique_events = {}
        dupes_removed = 0
        for record in fetched_records:
            event_id = record['event_id']
            if event_id not in unique_events:
                unique_events[event_id] = record
            else:
                dupes_removed += 1
                if record['updated_at'] > unique_events[event_id]['updated_at']:
                    unique_events[event_id] = record

        deduped_records = list(unique_events.values())
        written_count = len(deduped_records)
        max_updated = max(r['updated_at'] for r in deduped_records)

        # Write raw output (JSONL append format)
        with open(raw_api_path, 'a') as f:
            for record in deduped_records:
                f.write(json.dumps(record) + '\n')

        # Update watermark ONLY after successful raw write using an atomic pattern
        save_watermark(max_updated)
        watermark_after = load_watermark()
        print(f"Successfully ingested {len(deduped_records)} unique records. Watermark updated to: {max_updated}")
        
        log_run("rest_api", "SUCCESS", read_count, written_count, dupes_removed, watermark_before, watermark_after, start_time, utc_now())
    except Exception as e:
        log_run("rest_api", "FAILED", 0, 0, 0, watermark_before, load_watermark(), start_time, utc_now(), error=str(e))
        raise

if __name__=='__main__':
    RAW.mkdir(exist_ok=True); STATE.mkdir(exist_ok=True)
    ingest_files(); ingest_api()