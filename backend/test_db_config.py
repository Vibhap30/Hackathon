#!/usr/bin/env python3
"""
Test script to verify database configuration fix
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.core.database import engine, database
    from app.core.config import settings
    print("✅ Database configuration imported successfully")
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Engine created: {engine}")
    print(f"Database object: {database}")
    
    # Test engine connection
    with engine.connect() as conn:
        print("✅ Database engine connection test successful")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
