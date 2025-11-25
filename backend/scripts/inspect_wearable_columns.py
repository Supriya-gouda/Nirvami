"""Inspect wearable_snapshots table via Supabase admin client and print sample rows and keys."""
import os
import sys
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SERVICE_KEY:
    print("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in environment")
    sys.exit(1)

admin = create_client(SUPABASE_URL, SERVICE_KEY)

print("Fetching sample rows from wearable_snapshots (limit 3)...\n")
try:
    res = admin.table('wearable_snapshots').select('*').limit(3).execute()
    print("Status code / result: ", type(res), "\n")
    data = res.data
    if not data:
        print("No rows found in wearable_snapshots. Table may be empty.")
    else:
        for i, row in enumerate(data):
            print(f"--- Row {i+1} keys ---")
            for k in row.keys():
                print(k)
            print("\nRow sample (truncated):")
            # print JSON but truncate long fields
            import json
            row_json = json.dumps(row, default=str)
            print(row_json[:1000])
            print('\n')
except Exception as e:
    print("Error querying wearable_snapshots:", e)
    import traceback
    traceback.print_exc()
    sys.exit(2)

# Also fetch column info via information_schema if possible
print("\nAttempting to query information_schema.columns for wearable_snapshots...\n")
try:
    info = admin.table('information_schema.columns').select('column_name,data_type,ordinal_position').eq('table_name','wearable_snapshots').order('ordinal_position',{'ascending':True}).execute()
    if info.data:
        print("Columns from information_schema:")
        for col in info.data:
            print(f"{col.get('ordinal_position')}: {col.get('column_name')} ({col.get('data_type')})")
    else:
        print("No information_schema results (may be restricted).")
except Exception as e:
    print("Could not query information_schema.columns via PostgREST: ", e)

print('\nDone.')
