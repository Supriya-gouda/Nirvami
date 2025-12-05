#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.utils.database import get_supabase

supabase = get_supabase()
result = supabase.table('recommendations').select('*').limit(10).execute()

print(f'Total recommendations: {len(result.data)}')
print('\nSample recommendations:')
for i, rec in enumerate(result.data[:5], 1):
    print(f'{i}. [{rec["category"].upper()}] {rec["title"]} (from {rec["source"]})')
    print(f'   Date: {rec["date"]}, User: {rec["user_id"][:8]}...')
    print()