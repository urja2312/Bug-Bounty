import sqlite3
import uuid
import datetime

conn = sqlite3.connect('app.db')
cursor = conn.cursor()

company_id = uuid.uuid4().hex
program_id = uuid.uuid4().hex
now = datetime.datetime.utcnow().isoformat()

# delete any older records that might be malformed
cursor.execute('DELETE FROM "programs"')
cursor.execute('DELETE FROM "users" WHERE email="company@example.com"')

try:
    cursor.execute('''
        INSERT INTO "users" (
            id, email, hashed_password, full_name, role, 
            is_active, is_verified, token_version, reputation_score,
            created_at, updated_at
        ) 
        VALUES (?, 'company@example.com', 'dummy_hash', 'Demo Company', 'company', 
            1, 1, 0, 0, ?, ?)
    ''', (company_id, now, now))
    
    cursor.execute('''
        INSERT INTO "programs" (
            id, name, slug, description, rules, visibility, status, 
            company_id, response_sla_hours, created_at, updated_at
        )
        VALUES (?, 'Demo Program', 'demo-program', 'Test for valid submissions', 
            'Hack ethical', 'public', 'active', ?, 72, ?, ?)
    ''', (program_id, company_id, now, now))
    
    conn.commit()
    print('Database seeded perfectly with hex UUIDs!')
except Exception as e:
    print('Error:', e)

conn.close()
