import os
import sys
import threading
import time
from pathlib import Path
import sqlite3
import random

# Ensure the app is in the path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services import save_prediction
from app.database import initialize_database

# Configure a test database for this script so we don't mess up the real one
TEST_DB_PATH = str(PROJECT_ROOT / "test_concurrency.db")
os.environ["DATABASE_PATH"] = TEST_DB_PATH

# 1. Initialize the DB
initialize_database()

NUM_THREADS = 50
SUCCESS_COUNT = 0
LOCK_ERRORS = 0
OTHER_ERRORS = 0

def mock_worker(thread_id):
    global SUCCESS_COUNT, LOCK_ERRORS, OTHER_ERRORS
    
    # Simulate a tiny random delay to force overlapping connections
    time.sleep(random.uniform(0.01, 0.1))
    
    mock_values = {
        "service_name": f"Concurrency Test {thread_id}",
        "usage_quantity": 100.0,
        "usage_unit": "Hours",
        "region": "us-central1",
        "cpu": 50.0,
        "memory": 50.0,
        "network_in": 10.0,
        "network_out": 10.0,
        "usage_start": "2024-01-01",
        "usage_end": "2024-01-31",
        "cost_per_quantity": 0.05,
    }
    
    try:
        # SQLite's default timeout in python is 5.0 seconds. 
        # By hitting it simultaneously with 50 threads, we stress test the lock.
        save_prediction(mock_values, 123.45)
        SUCCESS_COUNT += 1
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e).lower():
            LOCK_ERRORS += 1
        else:
            OTHER_ERRORS += 1
    except Exception as e:
        OTHER_ERRORS += 1

def run_test():
    print(f"Starting SQLite Concurrency Test with {NUM_THREADS} threads...")
    threads = []
    
    start_time = time.time()
    
    for i in range(NUM_THREADS):
        t = threading.Thread(target=mock_worker, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    duration = time.time() - start_time
    
    print("\n--- TEST RESULTS ---")
    print(f"Total Time: {duration:.2f} seconds")
    print(f"Successful Writes: {SUCCESS_COUNT}")
    print(f"Database Locked Errors: {LOCK_ERRORS}")
    print(f"Other Errors: {OTHER_ERRORS}")
    
    if LOCK_ERRORS > 0:
        print("\nWARNING: SQLite write locks detected! If this happens in production, consider migrating to PostgreSQL.")
    else:
        print("\nSUCCESS: SQLite handled the concurrent load successfully without locking.")
        
    # Cleanup test DB
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass

if __name__ == "__main__":
    run_test()
