from fastapi import FastAPI, Request, Depends, Form, File, UploadFile, HTTPException, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import date, datetime, time
import os
import shutil
from typing import Optional
from pathlib import Path

import models, crud
from database import get_db, Base, engine
from fastapi.templating import Jinja2Templates

# ================== AUTHENTICATION DEPENDENCIES ==================
def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Get current logged in user from session"""
    session_token = request.cookies.get("session_token")
    
    if not session_token:
        return None
    
    session = crud.get_session(db, session_token)
    if not session:
        return None
    
    user = crud.get_user_by_id(db, session.user_id)
    return user

def require_login(user = Depends(get_current_user)):
    """Require user to be logged in"""
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    return user

def require_login_redirect(request: Request, db: Session = Depends(get_db)):
    """Require user to be logged in with redirect for HTML pages"""
    user = get_current_user(request, db)
    if not user:
        current_path = request.url.path
        return RedirectResponse(url=f"/login?next={current_path}", status_code=302)
    return user

def require_admin(user = Depends(require_login)):
    """Require admin role"""
    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# ======================================
# INIT APP
# ======================================
app = FastAPI()

# Templates
templates = Jinja2Templates(directory="templates")

# Setup upload directory structure
BASE_UPLOAD_DIR = "uploads"
os.makedirs(BASE_UPLOAD_DIR, exist_ok=True)

# Create subdirectories for different types of uploads
UPLOAD_FOLDERS = [
    "skid_depot", "skid_laut", "skid_lumbung", 
    "loading", "distribusi", "pembayaran", "general"
]

for folder in UPLOAD_FOLDERS:
    os.makedirs(os.path.join(BASE_UPLOAD_DIR, folder), exist_ok=True)

# Mount static files SETELAH folder dipastikan ada
app.mount("/uploads", StaticFiles(directory=BASE_UPLOAD_DIR), name="uploads")


# =========================
# ====== FILE UPLOAD (FIXED) ======
# =========================
def save_upload(file: UploadFile, folder: str = "general"):
    """
    Save uploaded file and return URL path for browser access
    
    Args:
        file: UploadFile object from FastAPI
        folder: Subfolder name (skid_depot, skid_laut, etc.)
    
    Returns:
        str: URL path that can be accessed by browser (/uploads/folder/filename)
        None: If file is None or empty
    """
    if not file or not file.filename:
        return None
    
    # Validate folder name (security)
    if folder not in UPLOAD_FOLDERS:
        folder = "general"
    
    # Create upload directory if not exists
    upload_dir = os.path.join(BASE_UPLOAD_DIR, folder)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename to avoid conflicts
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_extension = os.path.splitext(file.filename)[1]
    safe_filename = f"{timestamp}{file_extension}"
    
    # Full file path on disk
    file_path = os.path.join(upload_dir, safe_filename)
    
    # Save file to disk
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        print(f"Error saving file: {e}")
        return None
    
    # ✅ Return URL path sesuai dengan mount /uploads
    return f"/uploads/{folder}/{safe_filename}"
# =========================
# ====== HELPER DATE ======
# =========================
def parse_date(value: str) -> date:
    """Convert string 'YYYY-MM-DD' ke datetime.date"""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None

def parse_time(value: str) -> time:
    """Convert string 'HH:MM' ke datetime.time"""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError:
        return None

def parse_int(value: str) -> int:
    """Convert string ke int, return 0 jika gagal"""
    if not value:
        return 0
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

# ================== HOME ==================
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    total_user = db.query(models.User).count()
    total_karyawan = db.query(models.Karyawan).count()
    
    return templates.TemplateResponse("home.html", {
        "request": request,
        "total_user": total_user,
        "total_karyawan": total_karyawan,
    })

# ================== DASHBOARD ADMIN ==================
@app.get("/dashboard/admin", response_class=HTMLResponse)
async def dashboard_admin(request: Request, db: Session = Depends(get_db)):
    data = {
        "total_users": len(crud.get_users(db)) if hasattr(crud, 'get_users') else 0,
        "total_karyawan": db.query(models.Karyawan).count() if hasattr(models, 'Karyawan') else 0,
        "produksi_bulan_ini": len(crud.get_produksi_selesai(db)),
    }
    return templates.TemplateResponse("home.html", {
        "request": request,
        "data": data
    })

# ================== DASHBOARD MERAK + SEMARANG ==================
@app.get("/dashboard/mrksmg", response_class=HTMLResponse)
async def dashboard_mrksmg(request: Request, db: Session = Depends(get_db)):
    # Get data terpisah untuk Merak dan Semarang sesuai template
    laporan_merak, laporan_semarang = crud.get_laporan_by_location(db)
    
    return templates.TemplateResponse("dashboardmrksmg.html", {
        "request": request,
        "laporan_merak": laporan_merak,
        "laporan_semarang": laporan_semarang
    })

# ================== HELPER FUNCTIONS ==================
from datetime import datetime, date, time
import os
import shutil

def parse_date(date_str: str):
    """Parse date string to date object"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        return None

def parse_time(time_str: str):
    """Parse time string to time object"""
    try:
        return datetime.strptime(time_str, '%H:%M').time()
    except:
        return None

def parse_int(int_str: str):
    """Parse string to integer"""
    try:
        return int(int_str) if int_str else 0
    except:
        return 0

def save_upload(file: UploadFile, folder: str = "general"):  # <-- HAPUS INI
    """Save uploaded file and return relative path"""
    if not file or not file.filename:
        return None
    
    # Create upload directory
    upload_dir = f"uploads/{folder}"  # <-- INI MASALAHNYA!
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_extension = os.path.splitext(file.filename)[1]
    filename = f"{timestamp}{file_extension}"
    
    # Save file
    file_path = os.path.join(upload_dir, filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Return relative path for database
    return f"{folder}/{filename}"  # <-- DAN INI JUGA SALAH!
# =========================
# ====== HALAMAN FORM =====
# =========================
@app.get("/form-laporan", response_class=HTMLResponse)
async def form_laporan(request: Request, user_or_redirect = Depends(require_login_redirect)):
    if isinstance(user_or_redirect, RedirectResponse):
        return user_or_redirect
    
    user = user_or_redirect
    return templates.TemplateResponse("form_laporan.html", {"request": request, "user": user})

@app.get("/laporan-skid", response_class=HTMLResponse)
async def form_laporan(request: Request, user_or_redirect = Depends(require_login_redirect)):
    if isinstance(user_or_redirect, RedirectResponse):
        return user_or_redirect
    
    user = user_or_redirect
    return templates.TemplateResponse("laporan-skid.html", {"request": request, "user": user})

@app.get("/laporan-loading", response_class=HTMLResponse)
async def form_laporan(request: Request, user_or_redirect = Depends(require_login_redirect)):
    if isinstance(user_or_redirect, RedirectResponse):
        return user_or_redirect
    
    user = user_or_redirect
    return templates.TemplateResponse("laporan-loading.html", {"request": request, "user": user})


@app.get("/laporan-produksi", response_class=HTMLResponse)
async def form_laporan(request: Request, user_or_redirect = Depends(require_login_redirect)):
    if isinstance(user_or_redirect, RedirectResponse):
        return user_or_redirect
    
    user = user_or_redirect
    return templates.TemplateResponse("laporan-produksi.html", {"request": request, "user": user})

@app.get("/laporan-supir", response_class=HTMLResponse)
async def form_laporan(request: Request, user_or_redirect = Depends(require_login_redirect)):
    if isinstance(user_or_redirect, RedirectResponse):
        return user_or_redirect
    
    user = user_or_redirect
    return templates.TemplateResponse("laporan-supir.html", {"request": request, "user": user})

# ================== SKID MERAK DEPOT ==================
@app.post("/skid-masuk-depot")
async def create_skid_masuk_depot(
    nama_driver: str = Form(...),
    tanggal: str = Form(...),
    rit: str = Form(...),
    jam_masuk: str = Form(...),
    user = Depends(require_login),
    db: Session = Depends(get_db)
):
    data = {
        "nama_driver": nama_driver,
        "tanggal": parse_date(tanggal),
        "rit": parse_int(rit),
        "jam_masuk": parse_time(jam_masuk)
    }
    result = crud.create_skid_masuk_depot(db, data)
    return {"status": "success", "id": result.id}

@app.post("/skid-keluar-depot")
async def create_skid_keluar_depot(
    nama_driver: str = Form(...),
    tanggal: str = Form(...),
    jam_keluar: str = Form(...),
    jumlah_spa: str = Form(...),
    foto_spa: UploadFile = File(...),  # WAJIB
    user = Depends(require_login),
    db: Session = Depends(get_db)
):
    data = {
        "nama_driver": nama_driver,
        "tanggal": parse_date(tanggal),
        "jam_keluar": parse_time(jam_keluar),
        "jumlah_spa": parse_int(jumlah_spa),
        "foto_spa": save_upload(foto_spa, "skid_depot")
    }
    result = crud.create_skid_keluar_depot(db, data)
    return {"status": "success", "id": result.id}

# ================== SKID MERAK LAUT ==================
@app.post("/skid-masuk-laut")
async def create_skid_masuk_laut(
    nama_driver: str = Form(...),
    tanggal: str = Form(...),
    jam_masuk: str = Form(...),
    petugas_loading: str = Form(...),
    user = Depends(require_login),
    db: Session = Depends(get_db)
):
    data = {
        "nama_driver": nama_driver,
        "tanggal": parse_date(tanggal),
        "jam_masuk": parse_time(jam_masuk),
        "petugas_loading": petugas_loading
    }
    result = crud.create_skid_masuk_laut(db, data)
    return {"status": "success", "id": result.id}

@app.post("/skid-keluar-laut")
async def create_skid_keluar_laut(
    nama_driver: str = Form(...),
    tanggal: str = Form(...),
    jam_keluar: str = Form(...),
    catatan: str = Form(...),  # WAJIB
    media: UploadFile = File(...),  # WAJIB
    user = Depends(require_login),
    db: Session = Depends(get_db)
):
    data = {
        "nama_driver": nama_driver,
        "tanggal": parse_date(tanggal),
        "jam_keluar": parse_time(jam_keluar),
        "catatan": catatan,
        "media": save_upload(media, "skid_laut")
    }
    result = crud.create_skid_keluar_laut(db, data)
    return {"status": "success", "id": result.id}

# ================== SKID SEMARANG LUMBUNG ==================
@app.post("/skid-masuk-lumbung")
async def create_skid_masuk_lumbung(
    nama_driver: str = Form(...),
    tanggal: str = Form(...),
    jam_masuk: str = Form(...),
    petugas_loading: str = Form(...),  # WAJIB
    user = Depends(require_login),
    db: Session = Depends(get_db)
):
    data = {
        "nama_driver": nama_driver,
        "tanggal": parse_date(tanggal),
        "jam_masuk": parse_time(jam_masuk),
        "petugas_loading": petugas_loading
    }
    result = crud.create_skid_masuk_lumbung(db, data)
    return {"status": "success", "id": result.id}

@app.post("/skid-keluar-lumbung")
async def create_skid_keluar_lumbung(
    nama_driver: str = Form(...),
    tanggal: str = Form(...),
    jam_keluar: str = Form(...),
    catatan: str = Form(...),  # WAJIB
    media: UploadFile = File(...),  # WAJIB
    user = Depends(require_login),
    db: Session = Depends(get_db)
):
    data = {
        "nama_driver": nama_driver,
        "tanggal": parse_date(tanggal),
        "jam_keluar": parse_time(jam_keluar),
        "catatan": catatan,
        "media": save_upload(media, "skid_lumbung")
    }
    result = crud.create_skid_keluar_lumbung(db, data)
    return {"status": "success", "id": result.id}

# ================== SEBELUM & SESUDAH LOADING ==================

@app.post("/sebelum-loading")
async def create_sebelum_loading(
    penanggung_jawab: str = Form(...),
    tanggal: str = Form(...),
    nama_driver: str = Form(...),
    jam_mulai: str = Form(...),
    netto_spa: str = Form(...),
    rotogen_kanan: str = Form(...),
    rotogen_kiri: str = Form(...),
    video_kiri: UploadFile = File(...),
    video_kanan: UploadFile = File(...),
    user = Depends(require_login),
    db: Session = Depends(get_db)
):
    data = {
        "penanggung_jawab": penanggung_jawab,
        "tanggal": parse_date(tanggal),
        "nama_driver": nama_driver,
        "jam_mulai": parse_time(jam_mulai),
        "netto_spa": parse_int(netto_spa),
        "rotogen_kanan": parse_int(rotogen_kanan),
        "rotogen_kiri": parse_int(rotogen_kiri),
        "video_kiri": save_upload(video_kiri, "loading"),
        "video_kanan": save_upload(video_kanan, "loading")
    }
    crud.create_sebelum_loading(db, data)
    return RedirectResponse(url="/laporan-loading", status_code=303)


@app.post("/sesudah-loading")
async def create_sesudah_loading(
    penanggung_jawab: str = Form(...),
    tanggal: str = Form(...),
    jam_selesai: str = Form(...),
    video_kiri: UploadFile = File(...),
    video_kanan: UploadFile = File(...),
    user = Depends(require_login),
    db: Session = Depends(get_db)
):
    data = {
        "penanggung_jawab": penanggung_jawab,
        "tanggal": parse_date(tanggal),
        "jam_selesai": parse_time(jam_selesai),
        "video_kiri": save_upload(video_kiri, "loading"),
        "video_kanan": save_upload(video_kanan, "loading")
    }
    crud.create_sesudah_loading(db, data)
    return RedirectResponse(url="/laporan-loading", status_code=303)


# ================== PRODUKSI ==================
from fastapi.responses import JSONResponse

@app.post("/produksi-mulai")
async def create_produksi_mulai(
    kepala_produksi: str = Form(...),
    tanggal: str = Form(...),
    nama_driver: str = Form(...),
    jam_mulai: str = Form(...),
    shift: str = Form(...),
    user = Depends(require_login),
    db: Session = Depends(get_db)
):
    data = {
        "kepala_produksi": kepala_produksi,
        "tanggal": parse_date(tanggal),
        "nama_driver": nama_driver,
        "jam_mulai": parse_time(jam_mulai),
        "shift": shift
    }
    result = crud.create_produksi_mulai(db, data)
    return JSONResponse({
        "success": True,
        "message": "Produksi mulai berhasil disimpan",
        "id": result.id
    })


@app.post("/produksi-selesai")
async def create_produksi_selesai(
    kepala_produksi: str = Form(...),
    tanggal: str = Form(...),
    jam_selesai: str = Form(...),
    tabung_kosong: str = Form(...),
    tabung_12: str = Form(...), 
    tabung_50: str = Form(...),
    keterangan: str = Form(...),
    user = Depends(require_login),
    db: Session = Depends(get_db)
):
    data = {
        "kepala_produksi": kepala_produksi,
        "tanggal": parse_date(tanggal),
        "jam_selesai": parse_time(jam_selesai),
        "tabung_kosong": parse_int(tabung_kosong),
        "tabung_12": parse_int(tabung_12),
        "tabung_50": parse_int(tabung_50),
        "keterangan": keterangan
    }
    # Perbaikan: Memanggil fungsi crud yang benar untuk ProduksiSelesai
    result = crud.create_produksi_selesai(db, data)
    return JSONResponse({
        "success": True,
        "message": "Produksi selesai berhasil disimpan",
        "id": result.id
    })
@app.post("/laporan/kirim-merak")
async def create_laporan_kirim_merak(
    tanggal: str = Form(...),
    nama_driver: str = Form(...),
    plat_mobil: str = Form(...),
    jam_berangkat: str = Form(...),
    kapasitas: str = Form(...),
    jenis_tabung: str = Form(...),
    jumlah_dibawa: str = Form(...),
    jumlah_turun: str = Form(...),
    tujuan: str = Form(...),
    alamat: str = Form(...),
    kondisi_tabung: str = Form(...),
    keterangan: str = Form(...),
    verifikasi_barang: UploadFile = File(...),
    user = Depends(require_login),
    db: Session = Depends(get_db)
):
    data = {
        "tanggal": parse_date(tanggal),
        "nama_driver": nama_driver,
        "plat_mobil": plat_mobil,
        "jam_berangkat": parse_time(jam_berangkat),
        "kapasitas": parse_int(kapasitas),
        "jenis_tabung": jenis_tabung,
        "jumlah_dibawa": parse_int(jumlah_dibawa),
        "jumlah_turun": parse_int(jumlah_turun),
        "tujuan": tujuan,
        "alamat": alamat,
        "kondisi_tabung": kondisi_tabung,
        "keterangan": keterangan,
        "verifikasi_barang": save_upload(verifikasi_barang, "distribusi")
    }
    result = crud.create_laporan_kirim(db, data, "merak")
    return {"status": "success", "id": result.id}


@app.post("/laporan/kirim-semarang")
async def create_laporan_kirim_semarang(
    tanggal: str = Form(...),
    nama_driver: str = Form(...),
    plat_mobil: str = Form(...),
    jam_berangkat: str = Form(...),
    kapasitas: str = Form(...),
    jenis_tabung: str = Form(...),
    jumlah_dibawa: str = Form(...),
    jumlah_turun: str = Form(...),
    tujuan: str = Form(...),
    alamat: str = Form(...),
    kondisi_tabung: str = Form(...),
    keterangan: str = Form(...),
    verifikasi_barang: UploadFile = File(...),
    user = Depends(require_login),
    db: Session = Depends(get_db)
):
    data = {
        "tanggal": parse_date(tanggal),
        "nama_driver": nama_driver,
        "plat_mobil": plat_mobil,
        "jam_berangkat": parse_time(jam_berangkat),
        "kapasitas": parse_int(kapasitas),
        "jenis_tabung": jenis_tabung,
        "jumlah_dibawa": parse_int(jumlah_dibawa),
        "jumlah_turun": parse_int(jumlah_turun),
        "tujuan": tujuan,
        "alamat": alamat,
        "kondisi_tabung": kondisi_tabung,
        "keterangan": keterangan,
        "verifikasi_barang": save_upload(verifikasi_barang, "distribusi")
    }
    result = crud.create_laporan_kirim(db, data, "semarang")
    return {"status": "success", "id": result.id}


# ================== DISTRIBUSI: BONGKAR ==================
@app.post("/laporan/bongkar-merak")
async def create_laporan_bongkar_merak(
    tanggal: str = Form(...),
    nama_driver: str = Form(...),
    jam_bongkar: str = Form(...),
    jenis_tabung: str = Form(...),
    jumlah_terbawa: str = Form(...),
    jumlah_turun: str = Form(...),
    sisa_dibawa: str = Form(...),
    jumlah_kosong: str = Form(...),
    kondisi_tabung: str = Form(...),
    nama_pangkalan: str = Form(...),
    alamat_pangkalan: str = Form(...),
    catatan: str = Form(...),
    media: UploadFile = File(...),
    user = Depends(require_login),
    db: Session = Depends(get_db)
):
    data = {
        "tanggal": parse_date(tanggal),
        "nama_driver": nama_driver,
        "jam_bongkar": parse_time(jam_bongkar),
        "jenis_tabung": jenis_tabung,
        "jumlah_terbawa": parse_int(jumlah_terbawa),
        "jumlah_turun": parse_int(jumlah_turun),
        "sisa_dibawa": parse_int(sisa_dibawa),
        "jumlah_kosong": parse_int(jumlah_kosong),
        "kondisi_tabung": kondisi_tabung,
        "nama_pangkalan": nama_pangkalan,
        "alamat_pangkalan": alamat_pangkalan,
        "catatan": catatan,
        "media": save_upload(media, "distribusi")
    }
    result = crud.create_laporan_bongkar(db, data, "merak")
    return {"status": "success", "id": result.id}


@app.post("/laporan/bongkar-semarang")
async def create_laporan_bongkar_semarang(
    tanggal: str = Form(...),
    nama_driver: str = Form(...),
    jam_bongkar: str = Form(...),
    jenis_tabung: str = Form(...),
    jumlah_terbawa: str = Form(...),
    jumlah_turun: str = Form(...),
    sisa_dibawa: str = Form(...),
    jumlah_kosong: str = Form(...),
    kondisi_tabung: str = Form(...),
    nama_pangkalan: str = Form(...),
    alamat_pangkalan: str = Form(...),
    catatan: str = Form(...),
    media: UploadFile = File(...),
    user = Depends(require_login),
    db: Session = Depends(get_db)
):
    data = {
        "tanggal": parse_date(tanggal),
        "nama_driver": nama_driver,
        "jam_bongkar": parse_time(jam_bongkar),
        "jenis_tabung": jenis_tabung,
        "jumlah_terbawa": parse_int(jumlah_terbawa),
        "jumlah_turun": parse_int(jumlah_turun),
        "sisa_dibawa": parse_int(sisa_dibawa),
        "jumlah_kosong": parse_int(jumlah_kosong),
        "kondisi_tabung": kondisi_tabung,
        "nama_pangkalan": nama_pangkalan,
        "alamat_pangkalan": alamat_pangkalan,
        "catatan": catatan,
        "media": save_upload(media, "distribusi")
    }
    result = crud.create_laporan_bongkar(db, data, "semarang")
    return JSONResponse({"status": "success", "id": result.id})



# ================== DASHBOARD ROUTES ==================
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user_or_redirect = Depends(require_login_redirect), db: Session = Depends(get_db)):
    """Main dashboard - require login with redirect"""
    if isinstance(user_or_redirect, RedirectResponse):
        return user_or_redirect
     
    user = user_or_redirect
    
    if user.role == "admin":
        return RedirectResponse(url="/dashboard/admin", status_code=302)
    else:
        return RedirectResponse(url="/form-laporan", status_code=302)

@app.get("/dashboard/admin", response_class=HTMLResponse)
async def dashboard_admin(request: Request, user = Depends(require_admin)):
    """Admin dashboard - require admin"""
    return templates.TemplateResponse("dashboard_admin.html", {
        "request": request,
        "user": user,
        "active_page": "dashboard"
    })

@app.get("/dashboard/mrksmg", response_class=HTMLResponse)
async def dashboard_mrksmg(request: Request, user = Depends(require_login), db: Session = Depends(get_db)):
    """Dashboard laporan - require login"""
    try:
        laporan_merak, laporan_semarang = crud.get_laporan_by_location(db)
    except Exception as e:
        print(f"Error loading dashboard: {e}")
        laporan_merak, laporan_semarang = [], []
    
    return templates.TemplateResponse("dashboardmrksmg.html", {
        "request": request,
        "user": user,
        "laporan_merak": laporan_merak,
        "laporan_semarang": laporan_semarang,
        "active_page": "produksi-mrksmg"
    })
# ================== USER ROUTES ==================
@app.get("/users/edit/{user_id}", response_class=HTMLResponse)
async def edit_user(request: Request, user_id: int, db: Session = Depends(get_db), user: models.User = Depends(require_admin)):
    """Menampilkan halaman edit user"""
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return templates.TemplateResponse(
        "edit_user.html",
        {
            "request": request,
            "user": db_user
        }
    )

@app.post("/users/edit/{user_id}")
async def update_user(
    request: Request,
    user_id: int,
    username: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    db: Session = Depends(get_db),
    user: models.User = Depends(require_admin)
):
    """Memproses formulir edit user dan memperbarui data"""
    try:
        updated_user = crud.update_user(
            db,
            user_id=user_id,
            username=username,
            email=email,
            role=role
        )
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
            
        return RedirectResponse(url="/data-user", status_code=303)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

@app.get("/users/delete/{user_id}", response_class=HTMLResponse)
async def delete_user(request: Request, user_id: int, db: Session = Depends(get_db), user: models.User = Depends(require_admin)):
    """Menampilkan halaman konfirmasi hapus user"""
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
        
    return templates.TemplateResponse(
        "delete_user_confirmation.html",
        {
            "request": request,
            "user": db_user
        }
    )

@app.post("/users/delete/{user_id}")
async def delete_user_action(user_id: int, db: Session = Depends(get_db), user: models.User = Depends(require_admin)):
    """Memproses penghapusan user"""
    deleted = crud.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found or could not be deleted")
    
    # Baris ini yang benar. Hanya satu yang diperlukan.
    return RedirectResponse(url="/data-user", status_code=303)
    
# --- Tambahkan rute ini untuk menampilkan halaman data user ---
@app.get("/data-user", response_class=HTMLResponse)
async def data_user(request: Request, db: Session = Depends(get_db)):
    """Menampilkan halaman daftar pengguna."""
    users = crud.get_all_users(db)
    return templates.TemplateResponse(
        "users.html",
        {
            "request": request,
            "users": users
        }
    )
# ================== API ROUTES ==================
@app.get("/api/laporan")
def get_all_laporan(db: Session = Depends(get_db)):
    """API endpoint to get all laporan data"""
    return crud.get_all_laporan(db)

# ======================================
# ===== API Pembayaran Agen (Revisi) ===
# ======================================

# List pembayaran agen
@app.get("/api/pembayaran-agen")
def api_list_pembayaran(db: Session = Depends(get_db)):
    rows = crud.get_all_pembayaran(db)
    return [
        {
            "id": r.id,
            "nama_agen": r.nama_agen,
            "harga_pertabung": r.harga_pertabung,
            "jenis_tabung": r.jenis_tabung,
            "nama_driver": r.nama_driver,
            "tanggal_pengiriman": r.tanggal_pengiriman.isoformat() if r.tanggal_pengiriman else None,
            "jumlah_turun": r.jumlah_turun,
            "status": r.status or "Belum Paid",
            "bukti": r.bukti,
        }
        for r in rows
    ]

# Tambah pembayaran agen
@app.post("/api/pembayaran-agen")
def api_create_pembayaran(
    nama_agen: str = Form(...),
    harga_pertabung: int = Form(...),
    jenis_tabung: str = Form(...),
    nama_driver: str = Form(...),
    tanggal_pengiriman: date = Form(...),
    jumlah_turun: int = Form(...),
    bukti: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    obj = crud.create_pembayaran(
        db,
        nama_agen=nama_agen,
        harga_pertabung=harga_pertabung,
        jenis_tabung=jenis_tabung,
        nama_driver=nama_driver,
        tanggal_pengiriman=tanggal_pengiriman,
        jumlah_turun=jumlah_turun,
        bukti=bukti
    )
    return {"ok": True, "id": obj.id}

@app.put("/api/pembayaran-agen/{id}")
def api_update_pembayaran(
    id: int,
    nama_agen: str = Form(None),
    harga_pertabung: int = Form(None),
    jenis_tabung: str = Form(None),
    nama_driver: str = Form(None),
    tanggal_pengiriman: date = Form(None),
    jumlah_turun: int = Form(None),
    status: str = Form(None),
    bukti: UploadFile = File(None),
    role: str = Form("lapangan"),
    db: Session = Depends(get_db)
):
    pembayaran = db.query(models.PembayaranAgen).filter(models.PembayaranAgen.id == id).first()
    if not pembayaran:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")

    if role == "lapangan":
        if bukti:
            # Gunakan fungsi save_upload yang sudah ada
            bukti_url = save_upload(bukti, "pembayaran")
            if bukti_url:
                pembayaran.bukti = bukti_url  # Simpan sebagai /uploads/pembayaran/filename
                pembayaran.status = "Paid"
            else:
                raise HTTPException(status_code=400, detail="Gagal upload bukti")
        else:
            raise HTTPException(status_code=400, detail="Lapangan hanya bisa upload bukti pembayaran")

    elif role == "admin":
        for field, value in {
            "nama_agen": nama_agen,
            "harga_pertabung": harga_pertabung,
            "jenis_tabung": jenis_tabung,
            "nama_driver": nama_driver,
            "tanggal_pengiriman": tanggal_pengiriman,
            "jumlah_turun": jumlah_turun,
            "status": status
        }.items():
            if value is not None:
                setattr(pembayaran, field, value)

        if bukti:
            # Gunakan fungsi save_upload
            bukti_url = save_upload(bukti, "pembayaran")
            if bukti_url:
                pembayaran.bukti = bukti_url

    db.commit()
    db.refresh(pembayaran)
    return {"ok": True, "id": pembayaran.id, "role": role}

# Halaman laporan pembayaran agen
@app.get("/laporan/pembayaran-agen", response_class=HTMLResponse)
async def laporan_pembayaran_agen(
    request: Request,
    user = Depends(require_login), # Tambahkan dependensi ini
    db: Session = Depends(get_db)
):
    pembayaran_list = db.query(models.PembayaranAgen).all()
    return templates.TemplateResponse("laporan_pembayaran_agen.html", {
        "request": request,
        "pembayaran_list": pembayaran_list,
        "user": user, # Tambahkan user ke context
    })

@app.delete("/api/pembayaran-agen/{id}")
def api_delete_pembayaran(
    id: int,
    user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    pembayaran = db.query(models.PembayaranAgen).filter(models.PembayaranAgen.id == id).first()
    if not pembayaran:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")

    if pembayaran.bukti:
        # Konversi URL ke file path
        # /uploads/pembayaran/filename -> uploads/pembayaran/filename
        file_path = pembayaran.bukti.lstrip("/")
        if os.path.exists(file_path):
            os.remove(file_path)

    db.delete(pembayaran)
    db.commit()
    return {"ok": True, "message": "Data berhasil dihapus"}

@app.get("/admin/fix-all-bukti-paths")
def fix_all_bukti_paths(user = Depends(require_admin), db: Session = Depends(get_db)):
    pembayaran_list = db.query(models.PembayaranAgen).filter(
        models.PembayaranAgen.bukti.notlike('/uploads/pembayaran/%')
    ).all()
    
    updated_count = 0
    for pembayaran in pembayaran_list:
        if pembayaran.bukti:
            filename = os.path.basename(pembayaran.bukti)
            new_path = f"/uploads/pembayaran/{filename}"
            pembayaran.bukti = new_path
            updated_count += 1
    
    db.commit()
    return {"message": f"Updated {updated_count} bukti paths", "updated_records": updated_count}


@app.get("/agen/edit/{pembayaran_id}", response_class=HTMLResponse)
async def edit_pembayaran(
    request: Request,
    pembayaran_id: int,
    db: Session = Depends(get_db),
    user: models.User = Depends(require_login)
):
    """Menampilkan halaman edit pembayaran agen"""
    db_pembayaran = crud.get_pembayaran_by_id(db, pembayaran_id)
    if not db_pembayaran:
        raise HTTPException(status_code=404, detail="Data tidak ditemukan")
    return templates.TemplateResponse(
        "edit_pembayaran.html",
        {
            "request": request,
            "pembayaran": db_pembayaran,
            "user": user
        }
    )

@app.post("/agen/edit/{pembayaran_id}")
async def update_pembayaran(
    request: Request,
    pembayaran_id: int,
    nama_agen: str = Form(...),
    harga_pertabung: float = Form(...),
    jenis_tabung: str = Form(...),
    nama_driver: str = Form(...),
    tanggal_pengiriman: date = Form(...),
    jumlah_turun: int = Form(...),
    status: Optional[str] = Form(None),
    bukti: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user: models.User = Depends(require_login)
):
    """Memproses formulir edit pembayaran agen dan memperbarui data"""
    try:
        updated_data = {
            "nama_agen": nama_agen,
            "harga_pertabung": harga_pertabung,
            "jenis_tabung": jenis_tabung,
            "nama_driver": nama_driver,
            "tanggal_pengiriman": tanggal_pengiriman,
            "jumlah_turun": jumlah_turun,
            "status": status,
            "bukti": bukti
        }
        
        updated_pembayaran = crud.update_pembayaran(db, pembayaran_id, **updated_data)
        
        if not updated_pembayaran:
            raise HTTPException(status_code=404, detail="Data tidak ditemukan")
        return RedirectResponse(url="/laporan/pembayaran-agen", status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal memperbarui data: {str(e)}")





# ================== LOGIN ROUTES ==================
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    # Check if already logged in
    try:
        user = get_current_user(request, next(get_db()))
        if user:
            return RedirectResponse(url="/dashboard", status_code=302)
    except:
        pass
    
    next_url = request.query_params.get("next")
    return templates.TemplateResponse("login.html", {
        "request": request,
        "next_url": next_url
    })

@app.post("/login")
async def login(
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    next_url: Optional[str] = Form(None),  # Tambahkan ini
    db: Session = Depends(get_db)
):
    """Process login"""
    # Clean up expired sessions
    crud.cleanup_expired_sessions(db)
    
    # Authenticate user
    user = crud.authenticate_user(db, username, password)
    
    if not user:
        return templates.TemplateResponse("login.html", {
            "request": {"method": "POST"},
            "error": "Username atau password salah",
            "next_url": next_url  # Pass kembali next_url jika login gagal
        })
    
    # Create session
    session = crud.create_session(db, user.id)
    
    # Determine redirect URL
    if next_url and next_url.startswith('/'):  # Security: only internal URLs
        redirect_url = next_url
    elif user.role == "admin":
        redirect_url = "/dashboard/admin"
    else:
        redirect_url = "/dashboard"
    
    # Set session cookie
    response = RedirectResponse(url=redirect_url, status_code=302)
    response.set_cookie(
        key="session_token",
        value=session.session_token,
        max_age=24*60*60,  # 24 hours
        httponly=True,
        secure=False  # Set to True in production with HTTPS
    )
    
    return response

@app.post("/logout")
async def logout(response: Response, request: Request, db: Session = Depends(get_db)):
    """Logout user"""
    session_token = request.cookies.get("session_token")
    
    if session_token:
        crud.delete_session(db, session_token)
    
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session_token")
    return response

# ================== REGISTER ROUTES (ADMIN ONLY) ==================
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, user = Depends(require_admin)):
    """Register page (admin only)"""
    return templates.TemplateResponse("register.html", {"request": request, "user": user})

@app.post("/register")
async def register(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(""),
    role: str = Form("user"),
    user = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create new user (admin only)"""
    new_user = crud.create_user(db, username, password, email, role)
    
    if not new_user:
        return templates.TemplateResponse("register.html", {
            "request": {"method": "POST"},
            "error": "Username sudah digunakan",
            "user": user
        })
    
    return RedirectResponse(url="/users", status_code=302)

# ================== USER MANAGEMENT ROUTES ==================
@app.get("/users", response_class=HTMLResponse)
async def users_page(request: Request, user = Depends(require_admin), db: Session = Depends(get_db)):
    """User management page (admin only)"""
    all_users = crud.get_all_users(db)
    return templates.TemplateResponse("users.html", {
        "request": request, 
        "user": user, 
        "users": all_users
    })

# ================== PROTECTED ROUTES ==================
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user = Depends(require_login), db: Session = Depends(get_db)):
    """Main dashboard - require login"""
    if user.role == "admin":
        return RedirectResponse(url="/dashboard/admin", status_code=302)
    else:
        return RedirectResponse(url="/dashboard/mrksmg", status_code=302)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user = Depends(get_current_user)):
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    # Jika belum login, langsung arahkan ke halaman login
    return RedirectResponse(url="/login", status_code=302)

# -------- Laporan --------
@app.get("/laporan/data-user", response_class=HTMLResponse)
async def data_user(request: Request, user = Depends(require_login), db: Session = Depends(get_db)):
    """Data user page - require login"""
    # Ambil semua data pengguna dari database
    all_users = crud.get_all_users(db)
    
    return templates.TemplateResponse("users.html", {
        "request": request, 
        "user": user,
        # Teruskan data users ke template
        "users": all_users,
        "active_page": "data-user"
    })

@app.get("/laporan/data-karyawan", response_class=HTMLResponse)
async def data_karyawan(
    request: Request, 
    user = Depends(require_login), 
    db: Session = Depends(get_db)
):
    karyawan = crud.get_all_karyawan(db)
    return templates.TemplateResponse("karyawan.html", {
        "request": request,
        "user": user,
        "active_page": "data-karyawan",  # <- harus sama dengan sidebar
        "karyawan": karyawan
    })


@app.get("/dashboard/mrksmg", response_class=HTMLResponse)
async def dashboard_mrksmg(request: Request, user = Depends(require_login), db: Session = Depends(get_db)):
    """Dashboard laporan - require login"""
    try:
        laporan_merak, laporan_semarang = crud.get_laporan_by_location(db)
    except:
        laporan_merak, laporan_semarang = [], []
    
    return templates.TemplateResponse("dashboardmrksmg.html", {
        "request": request,
        "user": user,
        "laporan_merak": laporan_merak,
        "laporan_semarang": laporan_semarang,
        "active_page": "produksi-mrksmg"
    })

@app.get("/agen", response_class=HTMLResponse)
async def agen(request: Request, user_or_redirect = Depends(require_login_redirect)):
    """Pembayaran agen - require login with redirect"""
    if isinstance(user_or_redirect, RedirectResponse):
        return user_or_redirect
    
    user = user_or_redirect
    return templates.TemplateResponse("agen.html", {
        "request": request, 
        "user": user,
        "active_page": "pembayaran-agen"
    })

@app.get("/form-laporan", response_class=HTMLResponse)
async def form_laporan(request: Request, user_or_redirect = Depends(require_login_redirect)):
    """Form laporan - require login with redirect"""
    if isinstance(user_or_redirect, RedirectResponse):
        return user_or_redirect
    
    user = user_or_redirect
    return templates.TemplateResponse("form_laporan.html", {"request": request, "user": user})

@app.get("/laporan/pembayaran-agen", response_class=HTMLResponse)
async def pembayaran_agen(request: Request, user = Depends(require_login)):
    """Laporan pembayaran agen - require login"""
    return templates.TemplateResponse("laporan_pembayaran_agen.html", {
        "request": request, 
        "user": user, 
        "active_page": "pembayaran-agen"
    })

@app.get("/laporan/about", response_class=HTMLResponse)
async def about(request: Request, user = Depends(require_login)):
    """About page - require login"""
    return templates.TemplateResponse("about.html", {
        "request": request, 
        "user": user, 
        "active_page": "about"
    })

# ================== KARYAWAN ==================

@app.get("/karyawan", response_class=HTMLResponse)
def list_karyawan(request: Request, db: Session = Depends(get_db)):
    karyawan = crud.get_all_karyawan(db)
    return templates.TemplateResponse("karyawan.html", {"request": request, "karyawan": karyawan})


@app.get("/karyawan/hapus/{id}")
def hapus_karyawan(id: int, db: Session = Depends(get_db)):
    crud.delete_karyawan(db, id)
    return RedirectResponse(url="/karyawan", status_code=303)


@app.post("/karyawan/simpan")
def simpan_karyawan(
    nik: str = Form(...),
    nama: str = Form(...),
    jabatan: str = Form(...),
    kontak: str = Form(None),
    keterangan: str = Form(None),
    edit_id: str = Form(None),   # <-- aman kalau kosong
    db: Session = Depends(get_db),
):
    if edit_id and edit_id.strip():
        crud.update_karyawan(db, int(edit_id), nik, nama, jabatan, kontak, keterangan)
    else:        # CREATE
        crud.create_karyawan(db, nik, nama, jabatan, kontak, keterangan)
    return RedirectResponse(url="/karyawan", status_code=303)


# ================== API ROUTES PROTECTION ==================
@app.post("/api/pembayaran-agen")
async def api_create_pembayaran(
    nama_agen: str = Form(...),
    harga_pertabung: str = Form(...),
    jenis_tabung: str = Form(...),
    nama_driver: str = Form(...),
    tanggal_pengiriman: date = Form(...),
    jumlah_turun: int = Form(...),
    bukti: UploadFile = File(None),
    user = Depends(require_login),
    db: Session = Depends(get_db)
):
    """Create pembayaran agen - require login"""
    try:
        # Process file upload if provided
        bukti_filename = None
        if bukti and bukti.filename:
            # Save uploaded file
            upload_dir = "uploads/pembayaran"
            os.makedirs(upload_dir, exist_ok=True)
            
            bukti_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{bukti.filename}"
            bukti_path = os.path.join(upload_dir, bukti_filename)
            
            with open(bukti_path, "wb") as buffer:
                shutil.copyfileobj(bukti.file, buffer)
        
        # Create pembayaran record
        pembayaran_data = {
            "nama_agen": nama_agen,
            "harga_pertabung": harga_pertabung,
            "jenis_tabung": jenis_tabung,
            "nama_driver": nama_driver,
            "tanggal_pengiriman": tanggal_pengiriman,
            "jumlah_turun": jumlah_turun,
            "bukti": bukti_filename,
            "user_id": user.id
        }
        
        # Save to database (implement this in your crud module)
        new_pembayaran = crud.create_pembayaran_agen(db, pembayaran_data)
        
        if new_pembayaran:
            return {"status": "success", "message": "Pembayaran agen berhasil disimpan"}
        else:
            raise HTTPException(status_code=400, detail="Gagal menyimpan data")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

# ================== ADDITIONAL API ROUTES ==================
@app.get("/api/pembayaran-agen")
async def api_get_pembayaran(
    user = Depends(require_login),
    db: Session = Depends(get_db)
):
    """Get all pembayaran agen data"""
    try:
        pembayaran_list = crud.get_all_pembayaran_agen(db)
        return {"status": "success", "data": pembayaran_list}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@app.delete("/api/pembayaran-agen/{pembayaran_id}")
async def api_delete_pembayaran(
    pembayaran_id: int,
    user = Depends(require_admin),  # Only admin can delete
    db: Session = Depends(get_db)
):
    """Delete pembayaran agen data"""
    try:
        deleted = crud.delete_pembayaran_agen(db, pembayaran_id)
        if deleted:
            return {"status": "success", "message": "Data berhasil dihapus"}
        else:
            raise HTTPException(status_code=404, detail="Data tidak ditemukan")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

# ================== ERROR HANDLERS ==================
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    return templates.TemplateResponse("404.html", {"request": request}, status_code=404)

@app.exception_handler(403)
async def forbidden_handler(request: Request, exc):
    """Handle 403 errors"""
    return templates.TemplateResponse("403.html", {"request": request}, status_code=403)

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors"""
    return templates.TemplateResponse("500.html", {"request": request}, status_code=500)


