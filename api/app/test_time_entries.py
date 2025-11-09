# api/app/test_time_entries.py - Quick diagnostic script
"""
Run this to check if time entries exist in the database.
Usage: docker exec -it vvhs-api python test_time_entries.py
"""
from database import SessionLocal
from models.time_tracking import TimeEntry
from models.volunteer import Volunteer

db = SessionLocal()

print("\n=== TIME ENTRIES DIAGNOSTIC ===\n")

# Check total time entries
total = db.query(TimeEntry).count()
print(f"Total time entries in database: {total}")

# Check by status
pending = db.query(TimeEntry).filter(TimeEntry.status == 'pending').count()
approved = db.query(TimeEntry).filter(TimeEntry.status == 'approved').count()

print(f"  - Pending: {pending}")
print(f"  - Approved: {approved}")

# List all entries with details
print("\nAll Time Entries:")
entries = db.query(TimeEntry).all()
for entry in entries:
    volunteer = db.query(Volunteer).filter(Volunteer.id == entry.volunteer_id).first()
    volunteer_name = f"{volunteer.first_name} {volunteer.last_name}" if volunteer else "Unknown"
    print(f"  • ID {entry.id}: {volunteer_name} - {entry.hours_decimal} hrs - Status: {entry.status}")

print("\n=== END DIAGNOSTIC ===\n")

db.close()
