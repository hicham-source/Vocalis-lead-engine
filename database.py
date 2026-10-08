import sqlite3

DB_PATH = 'leads.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            place_id TEXT PRIMARY KEY,
            name TEXT,
            address TEXT,
            rating REAL,
            review_count INTEGER,
            phone TEXT,
            website TEXT,
            maps_url TEXT,
            niche TEXT,
            whatsapp TEXT,
            email TEXT,
            instagram TEXT,
            linkedin TEXT,
            has_booking BOOLEAN,
            has_chatbot BOOLEAN,
            after_hours_issue BOOLEAN,
            revenue_loss_sar REAL,
            primary_pain TEXT,
            whatsapp_draft TEXT,
            email_draft TEXT,
            english_draft TEXT,
            status TEXT DEFAULT 'pending'
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS opt_out (
            identifier TEXT PRIMARY KEY,
            reason TEXT,
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH)
