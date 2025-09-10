import os
import sys
from sqlalchemy.orm import Session

# Karena modul berada di folder yang sama,
# impor langsung tanpa awalan 'app'
from models import User, Base
from crud import create_user, get_user_by_username
from database import SessionLocal, engine

# Buat tabel jika belum ada
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_initial_admin_user():
    """Skrip untuk membuat user admin awal."""
    db: Session = next(get_db())
    
    # Ganti dengan username dan password yang Anda inginkan
    username = "admin123"
    password = "admin123"
    email = "admin@example.com"
    role = "admin"
    
    # Cek apakah user admin sudah ada
    if get_user_by_username(db, username):
        print(f"User '{username}' sudah ada. Tidak ada yang perlu dilakukan.")
        return
        
    print(f"Membuat user admin baru: {username}...")
    new_admin = create_user(db, username, password, email, role)
    
    if new_admin:
        print("User admin berhasil dibuat!")
    else:
        print("Gagal membuat user admin. Username mungkin sudah digunakan.")

if __name__ == "__main__":
    create_initial_admin_user()
