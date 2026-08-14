import sqlite3
import os
import streamlit as st
from datetime import datetime

DB_NAME = "jobs_tracker.db"

def get_connection():
    """Establishes and returns a database connection."""
    try:
        conn = sqlite3.connect(DB_NAME, check_same_thread=False)
        # Enable returning rows as dictionaries
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        st.error(f"⚠️ Database Connection Error: {e}")
        return None

def init_db():
    """Initializes the database schema if it doesn't exist."""
    conn = get_connection()
    if conn is None:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                job_id TEXT PRIMARY KEY,
                job_title TEXT NOT NULL,
                employer_name TEXT NOT NULL,
                job_city TEXT,
                job_apply_link TEXT,
                status TEXT NOT NULL,
                date_added TEXT,
                date_updated TEXT
            )
        """)
        conn.commit()
    except Exception as e:
        st.error(f"⚠️ Database Initialization Error: {e}")
    finally:
        conn.close()

def save_job(job_id, title, employer, city, link, status="Saved"):
    """Saves a new job or updates an existing one if the status is different."""
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        # Check if job already exists
        cursor.execute("SELECT status FROM applications WHERE job_id = ?", (job_id,))
        row = cursor.fetchone()
        
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if row:
            # Update only if status or details changed
            cursor.execute("""
                UPDATE applications 
                SET job_title = ?, employer_name = ?, job_city = ?, job_apply_link = ?, date_updated = ?
                WHERE job_id = ?
            """, (title, employer, city, link, now_str, job_id))
        else:
            # Insert new
            cursor.execute("""
                INSERT INTO applications (job_id, job_title, employer_name, job_city, job_apply_link, status, date_added, date_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (job_id, title, employer, city, link, status, now_str, now_str))
            
        conn.commit()
        return True
    except Exception as e:
        st.error(f"⚠️ Failed to save job: {e}")
        return False
    finally:
        conn.close()

def get_all_applications():
    """Retrieves all tracked job applications ordered by last update date."""
    conn = get_connection()
    if conn is None:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM applications ORDER BY date_updated DESC")
        rows = cursor.fetchall()
        # Convert sqlite3.Row list to a list of dicts
        applications = [dict(row) for row in rows]
        return applications
    except Exception as e:
        st.error(f"⚠️ Failed to retrieve applications: {e}")
        return []
    finally:
        conn.close()

def update_application_status(job_id, new_status):
    """Updates the status and timestamp of a tracked job."""
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            UPDATE applications 
            SET status = ?, date_updated = ? 
            WHERE job_id = ?
        """, (new_status, now_str, job_id))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"⚠️ Failed to update application status: {e}")
        return False
    finally:
        conn.close()

def delete_application(job_id):
    """Deletes a tracked job from the database."""
    conn = get_connection()
    if conn is None:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM applications WHERE job_id = ?", (job_id,))
        conn.commit()
        return True
    except Exception as e:
        st.error(f"⚠️ Failed to delete application: {e}")
        return False
    finally:
        conn.close()

# Initialize on import
init_db()
