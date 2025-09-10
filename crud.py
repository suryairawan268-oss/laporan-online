from typing import Any, Dict, Type, Optional
from sqlalchemy.orm import Session
import models
import os
import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import models

# ================== USER AUTHENTICATION ==================
def create_user(db: Session, username: str, password: str, email: str = None, role: str = "user"):
    """Create new user with hashed password"""
    # Check if username already exists
    existing_user = db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        return None
    
    user = models.User(
        username=username,
        email=email,
        role=role
    )
    user.set_password(password)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, username: str, password: str):
    """Verify username and password"""
    user = db.query(models.User).filter(
        models.User.username == username,
        models.User.is_active == True
    ).first()
    
    if not user:
        return None
    
    if not user.check_password(password):
        return None
    
    # Update last login
    user.last_login = datetime.now()
    db.commit()
    
    return user

def get_user_by_username(db: Session, username: str):
    """Get user by username"""
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_id(db: Session, user_id: int):
    """Get user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()

# ================== SESSION MANAGEMENT ==================
def create_session(db: Session, user_id: int, expires_hours: int = 24):
    """Create new session for user"""
    # Generate secure session token
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=expires_hours)
    
    # Remove old sessions for this user
    db.query(models.UserSession).filter(models.UserSession.user_id == user_id).delete()
    
    # Create new session
    session = models.UserSession(
        user_id=user_id,
        session_token=session_token,
        expires_at=expires_at
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session

def get_session(db: Session, session_token: str):
    """Get active session by token"""
    session = db.query(models.UserSession).filter(
        models.UserSession.session_token == session_token,
        models.UserSession.expires_at > datetime.now()
    ).first()
    
    return session

def delete_session(db: Session, session_token: str):
    """Delete session (logout)"""
    db.query(models.UserSession).filter(
        models.UserSession.session_token == session_token
    ).delete()
    db.commit()

def cleanup_expired_sessions(db: Session):
    """Remove expired sessions"""
    db.query(models.UserSession).filter(
        models.UserSession.expires_at < datetime.now()
    ).delete()
    db.commit()

# ================== USER MANAGEMENT ==================
def get_all_users(db: Session):
    """Get all users (admin only)"""
    return db.query(models.User).all()

def update_user_role(db: Session, user_id: int, role: str):
    """Update user role"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.role = role
        db.commit()
        db.refresh(user)
    return user

def deactivate_user(db: Session, user_id: int):
    """Deactivate user account"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        user.is_active = False
        db.commit()
        
        # Remove all sessions for this user
        db.query(models.UserSession).filter(models.UserSession.user_id == user_id).delete()
        db.commit()
    return user
# ================== HELPER GENERIC ==================
def get_all(db: Session, model: Type, filters: Optional[Dict[str, Any]] = None) -> list:
    query = db.query(model)
    if filters:
        for k, v in filters.items():
            query = query.filter(getattr(model, k) == v)
    return query.order_by(model.id.desc()).all()

def get_by_id(db: Session, model: Type, id: int):
    return db.query(model).filter(model.id == id).first()

def _create(db: Session, model: Type, payload: Dict[str, Any]):
    obj = model(**payload)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def update(db: Session, model: Type, id: int, payload: Dict[str, Any]):
    obj = db.query(model).filter(model.id == id).first()
    if obj:
        for k, v in payload.items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
    return obj

def delete(db: Session, model: Type, id: int):
    obj = db.query(model).filter(model.id == id).first()
    if obj:
        db.delete(obj)
        db.commit()
    return obj

# ================== SKID MERAK DEPOT ==================
def create_skid_masuk_depot(db: Session, d: dict):    
    return _create(db, models.SkidMasukDepot, d)

def create_skid_keluar_depot(db: Session, d: dict):    
    return _create(db, models.SkidKeluarDepot, d)

def get_skid_masuk_depot(db: Session):  
    return get_all(db, models.SkidMasukDepot)

def get_skid_keluar_depot(db: Session): 
    return get_all(db, models.SkidKeluarDepot)

# ================== SKID MERAK LAUT ==================
def create_skid_masuk_laut(db: Session, d: dict):      
    return _create(db, models.SkidMasukLaut, d)

def create_skid_keluar_laut(db: Session, d: dict):   
    return _create(db, models.SkidKeluarLaut, d)

def get_skid_masuk_laut(db: Session):    
    return get_all(db, models.SkidMasukLaut)

def get_skid_keluar_laut(db: Session):  
    return get_all(db, models.SkidKeluarLaut)

# ================== SKID SEMARANG LUMBUNG ==================
def create_skid_masuk_lumbung(db: Session, d: dict):      
    return _create(db, models.SkidMasukLumbung, d)

def create_skid_keluar_lumbung(db: Session, d: dict):    
    return _create(db, models.SkidKeluarLumbung, d)

def get_skid_masuk_lumbung(db: Session):    
    return get_all(db, models.SkidMasukLumbung)

def get_skid_keluar_lumbung(db: Session):  
    return get_all(db, models.SkidKeluarLumbung)

# ================== LOADING ==================
def create_sebelum_loading(db: Session, d: dict):      
    return _create(db, models.SebelumLoading, d)

def create_sesudah_loading(db: Session, d: dict):      
    return _create(db, models.SesudahLoading, d)

def get_sebelum_loading(db: Session):    
    return get_all(db, models.SebelumLoading)

def get_sesudah_loading(db: Session):    
    return get_all(db, models.SesudahLoading)

# ================== PRODUKSI ==================
def create_produksi_mulai(db: Session, d: dict):      
    return _create(db, models.ProduksiMulai, d)

def create_produksi_selesai(db: Session, d: dict):    
    return _create(db, models.ProduksiSelesai, d)

def get_produksi_mulai(db: Session):    
    return get_all(db, models.ProduksiMulai)

def get_produksi_selesai(db: Session):  
    return get_all(db, models.ProduksiSelesai)

# ================== HELPER FUNCTIONS ==================

def _create(db: Session, model_class, d: dict):
    """Fungsi helper generik untuk membuat entri di database."""
    # Menghapus kunci yang tidak valid untuk model
    valid_keys = {column.name for column in model_class.__table__.columns}
    d_filtered = {k: v for k, v in d.items() if k in valid_keys}
    
    db_item = model_class(**d_filtered)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_all(db: Session, model_class, filters: dict = None):
    """Fungsi helper generik untuk mendapatkan semua item."""
    query = db.query(model_class)
    if filters:
        for key, value in filters.items():
            if value is not None:
                query = query.filter(getattr(model_class, key) == value)
    return query.all()

# Helper function untuk format data
def format_laporan_item(item, jenis_name, lokasi_name):
    """
    Fungsi helper yang diperbarui untuk memformat item laporan dari berbagai model.
    Menggunakan getattr untuk memastikan tidak ada error jika atribut tidak ditemukan.
    """
    return {
        "id": getattr(item, 'id', None),
        "jenis": jenis_name,
        "lokasi": lokasi_name,
        "penanggung_jawab": getattr(item, 'penanggung_jawab', '-'),
        "tanggal": getattr(item, 'tanggal', getattr(item, 'created_at', None)),
        "nama_driver": getattr(item, 'nama_driver', '-'),
        "plat_mobil": getattr(item, 'plat_mobil', '-'),
        "rit": getattr(item, 'rit', None),
        "jam_masuk": getattr(item, 'jam_masuk', None),
        "jam_keluar": getattr(item, 'jam_keluar', None),
        "jumlah_spa": getattr(item, 'jumlah_spa', None),
        "petugas_loading": getattr(item, 'petugas_loading', '-'),
        "jam_mulai": getattr(item, 'jam_mulai', None),
        "netto_spa": getattr(item, 'netto_spa', None),
        "rotogen_kanan": getattr(item, 'rotogen_kanan', None),
        "rotogen_kiri": getattr(item, 'rotogen_kiri', None),
        "jam_selesai": getattr(item, 'jam_selesai', None),
        "tabung_kosong": getattr(item, 'tabung_kosong', None),
        "tabung_12": getattr(item, 'tabung_12', None),
        "tabung_50": getattr(item, 'tabung_50', None),
        "keterangan": getattr(item, 'keterangan', getattr(item, 'catatan', '-')),
        "jam_berangkat": getattr(item, 'jam_berangkat', None),
        "kapasitas": getattr(item, 'kapasitas', None),
        "jenis_tabung": getattr(item, 'jenis_tabung', '-'),
        "jumlah_dibawa": getattr(item, 'jumlah_dibawa', None),
        "jumlah_turun": getattr(item, 'jumlah_turun', None),
        "tujuan": getattr(item, 'tujuan', '-'),
        "alamat": getattr(item, 'alamat', '-'),
        "kondisi_tabung": getattr(item, 'kondisi_tabung', '-'),
        "jumlah_terbawa": getattr(item, 'jumlah_terbawa', None),
        "sisa_dibawa": getattr(item, 'sisa_dibawa', None),
        "jumlah_kosong": getattr(item, 'jumlah_kosong', None),
        "nama_pangkalan": getattr(item, 'nama_pangkalan', '-'),
        "alamat_pangkalan": getattr(item, 'alamat_pangkalan', '-'),
        "foto_spa": getattr(item, 'foto_spa', None),
        "video_kiri": getattr(item, 'video_kiri', None),
        "video_kanan": getattr(item, 'video_kanan', None),
        "media": getattr(item, 'media', None),
        "verifikasi_barang": getattr(item, 'verifikasi_barang', None),
        "kepala_produksi": getattr(item, 'kepala_produksi', '-'),
        "jam_bongkar": getattr(item, 'jam_bongkar', None),
    }

# ================== DISTRIBUSI: KIRIM ==================
def create_laporan_kirim(db: Session, d: dict, lokasi: str):
    d["lokasi"] = lokasi
    return _create(db, models.LaporanKirim, d)

def get_laporan_kirim(db: Session, lokasi: str = None):
    filters = {"lokasi": lokasi} if lokasi else None
    return get_all(db, models.LaporanKirim, filters=filters)

# ================== DISTRIBUSI: BONGKAR ==================
def create_laporan_bongkar(db: Session, d: dict, lokasi: str):
    d["lokasi"] = lokasi
    return _create(db, models.LaporanBongkar, d)

def get_laporan_bongkar(db: Session, lokasi: str = None):
    filters = {"lokasi": lokasi} if lokasi else None
    return get_all(db, models.LaporanBongkar, filters=filters)

# ================== DASHBOARD FUNCTIONS ==================

def get_laporan_by_location(db: Session):
    """
    Fungsi untuk mendapatkan data laporan yang dipisah berdasarkan lokasi.
    Returns: tuple (laporan_merak, laporan_semarang)
    """
    laporan_merak = []
    laporan_semarang = []
    
    try:
        # MERAK
        for item in get_all(db, models.SkidMasukDepot):
            laporan_merak.append(format_laporan_item(item, "Skid Masuk Depot", "merak"))
        
        for item in get_all(db, models.SkidKeluarDepot):
            laporan_merak.append(format_laporan_item(item, "Skid Keluar Depot", "merak"))
        
        for item in get_all(db, models.SkidMasukLaut):
            laporan_merak.append(format_laporan_item(item, "Skid Masuk Laut", "merak"))
            
        for item in get_all(db, models.SkidKeluarLaut):
            laporan_merak.append(format_laporan_item(item, "Skid Keluar Laut", "merak"))

        # SEMARANG
        for item in get_all(db, models.SkidMasukLumbung):
            laporan_semarang.append(format_laporan_item(item, "Skid Masuk Lumbung", "semarang"))
            
        for item in get_all(db, models.SkidKeluarLumbung):
            laporan_semarang.append(format_laporan_item(item, "Skid Keluar Lumbung", "semarang"))

        # SHARED DATA
        shared_models = [
            (models.SebelumLoading, "Sebelum Loading"),
            (models.SesudahLoading, "Sesudah Loading"),
            (models.ProduksiMulai, "Produksi Mulai"),
            (models.ProduksiSelesai, "Produksi Selesai"),
        ]
        
        for model_class, jenis_name in shared_models:
            items = get_all(db, model_class)
            for item in items:
                # Asumsi laporan ini bisa dari Merak atau Semarang
                if getattr(item, 'lokasi', 'merak').lower() == 'merak':
                    laporan_merak.append(format_laporan_item(item, jenis_name, "merak"))
                else:
                    laporan_semarang.append(format_laporan_item(item, jenis_name, "semarang"))

        # DISTRIBUSI - filter berdasarkan lokasi field
        for item in get_laporan_kirim(db):
            if getattr(item, 'lokasi', None) and item.lokasi.lower() == "merak":
                laporan_merak.append(format_laporan_item(item, "Laporan Kirim", "merak"))
            elif getattr(item, 'lokasi', None) and item.lokasi.lower() == "semarang":
                laporan_semarang.append(format_laporan_item(item, "Laporan Kirim", "semarang"))
                
        for item in get_laporan_bongkar(db):
            if getattr(item, 'lokasi', None) and item.lokasi.lower() == "merak":
                laporan_merak.append(format_laporan_item(item, "Laporan Bongkar", "merak"))
            elif getattr(item, 'lokasi', None) and item.lokasi.lower() == "semarang":
                laporan_semarang.append(format_laporan_item(item, "Laporan Bongkar", "semarang"))
                
    except Exception as e:
        print(f"Error loading dashboard data: {e}")

    # Sort berdasarkan created_at/tanggal terbaru
    laporan_merak.sort(key=lambda x: x.get("tanggal") or "0000-00-00 00:00:00", reverse=True)
    laporan_semarang.sort(key=lambda x: x.get("tanggal") or "0000-00-00 00:00:00", reverse=True)

    return laporan_merak, laporan_semarang


# ================== DASHBOARD (Gabungan) - BACKUP ==================
def get_all_laporan(db: Session):
    """
    Fungsi backup untuk dashboard gabungan semua laporan
    """
    result = []

    # Helper function
    def add_to_result(items, jenis_name, lokasi_default="-"):
        for item in items:
            result.append({
                "id": item.id,
                "jenis": jenis_name,
                "lokasi": getattr(item, 'lokasi', lokasi_default),
                "nama_driver": getattr(item, 'nama_driver', '-'),
                "plat_mobil": getattr(item, 'plat_mobil', '-'),
                "tujuan": getattr(item, 'tujuan', getattr(item, 'nama_pangkalan', '-')),
                "jumlah": get_jumlah_for_dashboard(item),
                "created_at": item.created_at.strftime("%Y-%m-%d %H:%M:%S") if item.created_at else None
            })

    try:
        # Add all data
        add_to_result(get_all(db, models.LaporanKirim), "Laporan Kirim")
        add_to_result(get_all(db, models.LaporanBongkar), "Laporan Bongkar")
        add_to_result(get_all(db, models.SkidMasukDepot), "Skid Masuk Depot", "Depot")
        add_to_result(get_all(db, models.SkidKeluarDepot), "Skid Keluar Depot", "Depot")
        add_to_result(get_all(db, models.SkidMasukLaut), "Skid Masuk Laut", "Laut")
        add_to_result(get_all(db, models.SkidKeluarLaut), "Skid Keluar Laut", "Laut")
        add_to_result(get_all(db, models.SkidMasukLumbung), "Skid Masuk Lumbung", "Lumbung")
        add_to_result(get_all(db, models.SkidKeluarLumbung), "Skid Keluar Lumbung", "Lumbung")
        add_to_result(get_all(db, models.SebelumLoading), "Sebelum Loading")
        add_to_result(get_all(db, models.SesudahLoading), "Sesudah Loading")
        add_to_result(get_all(db, models.ProduksiMulai), "Produksi Mulai")
        add_to_result(get_all(db, models.ProduksiSelesai), "Produksi Selesai")
    except Exception as e:
        print(f"Error in get_all_laporan: {e}")

    # Sort by created_at terbaru
    result.sort(key=lambda x: x["created_at"] or "0000-00-00 00:00:00", reverse=True)
    return result

# ------- PEMBAYARAN AGEN -------  CRUD

import os
import models
from sqlalchemy.orm import Session

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def create_pembayaran(
    db: Session,
    nama_agen: str,
    harga_pertabung: float,
    jenis_tabung: str,
    nama_driver: str,
    tanggal_pengiriman,
    jumlah_turun: int,
    bukti=None
):
    bukti_path = None
    if bukti:
        filename = f"bukti_{nama_agen}_{bukti.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        with open(filepath, "wb") as f:
            f.write(bukti.file.read())

        bukti_path = f"static/uploads/{filename}"

    db_obj = models.PembayaranAgen(
        nama_agen=nama_agen,
        harga_pertabung=harga_pertabung,
        jenis_tabung=jenis_tabung,
        nama_driver=nama_driver,
        tanggal_pengiriman=tanggal_pengiriman,
        jumlah_turun=jumlah_turun,
        status="Paid" if bukti else "Belum Paid",
        bukti=bukti_path
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj


def get_all_pembayaran(db: Session):
    return db.query(models.PembayaranAgen).all()


def get_pembayaran_by_id(db: Session, id: int):
    return db.query(models.PembayaranAgen).filter(models.PembayaranAgen.id == id).first()


def update_pembayaran(
    db: Session,
    id: int,
    nama_agen: str = None,
    harga_pertabung: float = None,
    jenis_tabung: str = None,
    nama_driver: str = None,
    tanggal_pengiriman=None,
    jumlah_turun: int = None,
    status: str = None,
    bukti=None
):
    pembayaran = db.query(models.PembayaranAgen).filter(models.PembayaranAgen.id == id).first()
    if not pembayaran:
        return None

    if nama_agen is not None:
        pembayaran.nama_agen = nama_agen
    if harga_pertabung is not None:
        pembayaran.harga_pertabung = harga_pertabung
    if jenis_tabung is not None:
        pembayaran.jenis_tabung = jenis_tabung
    if nama_driver is not None:
        pembayaran.nama_driver = nama_driver
    if tanggal_pengiriman is not None:
        pembayaran.tanggal_pengiriman = tanggal_pengiriman
    if jumlah_turun is not None:
        pembayaran.jumlah_turun = jumlah_turun
    if status is not None:
        pembayaran.status = status

    if bukti:
        filename = f"bukti_{id}_{bukti.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)

        with open(filepath, "wb") as f:
            f.write(bukti.file.read())

        pembayaran.bukti = f"static/uploads/{filename}"
        pembayaran.status = "Paid"

    db.commit()
    db.refresh(pembayaran)
    return pembayaran

##-------------------------------------------------------##

def update_user(db: Session, user_id: int, username: str, email: str, role: str):
    """Memperbarui data pengguna di database."""
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db_user.username = username
        db_user.email = email
        db_user.role = role
        # db_user.hashed_password = pwd_context.hash(password) # Jika ingin menambahkan fitur update password
        
        db.commit()
        db.refresh(db_user)
        return db_user
    return None

def delete_user(db: Session, user_id: int):
    """Menghapus pengguna dari database."""
    db_user = get_user_by_id(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False


##-------------------------------------------------------##

def create_karyawan(db: Session, nik: str, nama: str, jabatan: str, kontak: str = None, keterangan: str = None):
    karyawan = models.Karyawan(
        nik=nik,
        nama=nama,
        jabatan=jabatan,
        kontak=kontak,
        keterangan=keterangan
    )
    db.add(karyawan)
    db.commit()
    db.refresh(karyawan)
    return karyawan

# Read all
def get_all_karyawan(db: Session):
    return db.query(models.Karyawan).all()

# Read by ID
def get_karyawan_by_id(db: Session, karyawan_id: int):
    return db.query(models.Karyawan).filter(models.Karyawan.id == karyawan_id).first()

# Update
def update_karyawan(db: Session, karyawan_id: int, nik: str, nama: str, jabatan: str, kontak: str = None, keterangan: str = None):
    karyawan = get_karyawan_by_id(db, karyawan_id)
    if karyawan:
        karyawan.nik = nik
        karyawan.nama = nama
        karyawan.jabatan = jabatan
        karyawan.kontak = kontak
        karyawan.keterangan = keterangan
        db.commit()
        db.refresh(karyawan)
    return karyawan

# Delete
def delete_karyawan(db: Session, karyawan_id: int):
    karyawan = get_karyawan_by_id(db, karyawan_id)
    if karyawan:
        db.delete(karyawan)
        db.commit()
    return karyawan


# ================== RESET LOGS (opsional) ==================
def reset_logs(db: Session):
    for M in [
        models.SkidMasukDepot, models.SkidKeluarDepot, models.SkidMasukLaut,
        models.SkidKeluarLaut, models.SebelumLoading, models.SesudahLoading,
        models.ProduksiMulai, models.ProduksiSelesai, models.LaporanKirim,
        models.LaporanBongkar, models.PembayaranAgen
    ]:
        db.query(M).delete()
    db.commit()
