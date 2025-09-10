from sqlalchemy import Column, Integer, String, Float, Date, Time, DateTime, Text, func, Boolean
from sqlalchemy.orm import relationship
from database import Base
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
# ============ USER MODEL (DENGAN AUTHENTICATION) ============
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=True, default="user")  # admin, user, lapangan
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def set_password(self, password):
        """Hash dan simpan password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifikasi password"""
        return check_password_hash(self.password_hash, password)

# ============ SESSION TABLE ============
class UserSession(Base):
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    session_token = Column(String(255), nullable=False, unique=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

# ============ DRIVER ============
class Driver(Base):
    __tablename__ = "drivers"
    id = Column(Integer, primary_key=True, index=True)
    nama = Column(String, unique=True, index=True)
    password = Column(String)
    # role bisa: admin / driver / produksi / checker / agen
    role = Column(String, default="agen")  
    created_at = Column(DateTime(timezone=True), server_default=func.now())



# ============ DEPOT (MERAK) ============
class SkidMasukDepot(Base):
    __tablename__ = "skid_masuk_depot"
    id = Column(Integer, primary_key=True, index=True)
    nama_driver = Column(String(100), nullable=False)
    plat_mobil = Column(String(50), nullable=True)
    tanggal = Column(Date, nullable=False)
    rit = Column(Integer, nullable=False)
    jam_masuk = Column(Time, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class SkidKeluarDepot(Base):
    __tablename__ = "skid_keluar_depot"
    id = Column(Integer, primary_key=True, index=True)
    nama_driver = Column(String(100), nullable=False)
    plat_mobil = Column(String(50), nullable=True)
    tanggal = Column(Date, nullable=False)
    jam_keluar = Column(Time, nullable=False)
    jumlah_spa = Column(Integer, nullable=False)
    foto_spa = Column(String(255), nullable=True)  # path foto
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

# ============ LAUT (MERAK) ============
class SkidMasukLaut(Base):
    __tablename__ = "skid_masuk_laut"
    id = Column(Integer, primary_key=True, index=True)
    nama_driver = Column(String(100), nullable=False)
    plat_mobil = Column(String(50), nullable=True)
    tanggal = Column(Date, nullable=False)
    jam_masuk = Column(Time, nullable=False)
    petugas_loading = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class SkidKeluarLaut(Base):
    __tablename__ = "skid_keluar_laut"
    id = Column(Integer, primary_key=True, index=True)
    nama_driver = Column(String(100), nullable=False)
    plat_mobil = Column(String(50), nullable=True)
    tanggal = Column(Date, nullable=False)
    jam_keluar = Column(Time, nullable=False)
    catatan = Column(Text, nullable=True)
    media = Column(String(255), nullable=True)  # foto/video
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

# ============ LUMBUNG (SEMARANG) ============
class SkidMasukLumbung(Base):
    __tablename__ = "skid_masuk_lumbung"
    id = Column(Integer, primary_key=True, index=True)
    nama_driver = Column(String(100), nullable=False)
    plat_mobil = Column(String(50), nullable=True)
    tanggal = Column(Date, nullable=False)
    jam_masuk = Column(Time, nullable=False)
    petugas_loading = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class SkidKeluarLumbung(Base):
    __tablename__ = "skid_keluar_lumbung"
    id = Column(Integer, primary_key=True, index=True)
    nama_driver = Column(String(100), nullable=False)
    plat_mobil = Column(String(50), nullable=True)
    tanggal = Column(Date, nullable=False)
    jam_keluar = Column(Time, nullable=False)
    catatan = Column(Text, nullable=True)
    media = Column(String(255), nullable=True)  # foto/video
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

# ============ LOADING ============
class SebelumLoading(Base):
    __tablename__ = "sebelum_loading"
    id = Column(Integer, primary_key=True, index=True)
    penanggung_jawab = Column(String(100), nullable=False)
    tanggal = Column(Date, nullable=False)
    nama_driver = Column(String(100), nullable=False)
    jam_mulai = Column(Time, nullable=False)
    netto_spa = Column(Integer, nullable=False)
    rotogen_kanan = Column(Integer, nullable=True)
    rotogen_kiri = Column(Integer, nullable=True)
    video_kiri = Column(String(255), nullable=True)
    video_kanan = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class SesudahLoading(Base):
    __tablename__ = "sesudah_loading"
    id = Column(Integer, primary_key=True, index=True)
    penanggung_jawab = Column(String(100), nullable=False)
    tanggal = Column(Date, nullable=False)
    jam_selesai = Column(Time, nullable=False)
    video_kiri = Column(String(255), nullable=True)
    video_kanan = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

# ============ PRODUKSI ============
class ProduksiMulai(Base):
    __tablename__ = "produksi_mulai"
    id = Column(Integer, primary_key=True, index=True)
    kepala_produksi = Column(String(100), nullable=False)
    tanggal = Column(Date, nullable=False)
    nama_driver = Column(String(100), nullable=False)
    jam_mulai = Column(Time, nullable=False)
    shift = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class ProduksiSelesai(Base):
    __tablename__ = "produksi_selesai"
    id = Column(Integer, primary_key=True, index=True)
    kepala_produksi = Column(String(100), nullable=False)
    tanggal = Column(Date, nullable=False)
    jam_selesai = Column(Time, nullable=False)
    tabung_kosong = Column(Integer, nullable=False)
    tabung_12 = Column(Integer, nullable=False)
    tabung_50 = Column(Integer, nullable=False)
    keterangan = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

# ============ DISTRIBUSI ============
class LaporanKirim(Base):
    __tablename__ = "laporan_kirim"
    id = Column(Integer, primary_key=True, index=True)
    lokasi = Column(String(50), nullable=False)  # Merak / Semarang
    tanggal = Column(Date, nullable=False)
    nama_driver = Column(String(100), nullable=False)
    plat_mobil = Column(String(50), nullable=False)
    jam_berangkat = Column(Time, nullable=False)
    kapasitas = Column(Integer, nullable=False)
    jenis_tabung = Column(String(50), nullable=False)
    jumlah_dibawa = Column(Integer, nullable=False)
    jumlah_turun = Column(Integer, nullable=True)
    tujuan = Column(String(100), nullable=False)
    alamat = Column(Text, nullable=True)
    kondisi_tabung = Column(String(100), nullable=False)
    keterangan = Column(Text, nullable=True)
    verifikasi_barang = Column(String(255), nullable=True)  # path foto/video
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

class LaporanBongkar(Base):
    __tablename__ = "laporan_bongkar"
    id = Column(Integer, primary_key=True, index=True)
    lokasi = Column(String(50), nullable=False)  # Merak / Semarang
    tanggal = Column(Date, nullable=False)
    nama_driver = Column(String(100), nullable=False)
    jam_bongkar = Column(Time, nullable=False)
    jenis_tabung = Column(String(50), nullable=False)
    jumlah_terbawa = Column(Integer, nullable=False)
    jumlah_turun = Column(Integer, nullable=False)
    sisa_dibawa = Column(Integer, nullable=False)
    jumlah_kosong = Column(Integer, nullable=False)
    kondisi_tabung = Column(String(100), nullable=False)
    nama_pangkalan = Column(String(100), nullable=False)
    alamat_pangkalan = Column(Text, nullable=True)
    catatan = Column(Text, nullable=True)
    media = Column(String(255), nullable=True)  # path foto/video
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

# ============ PEMBAYARAN AGEN ============
class PembayaranAgen(Base):
    __tablename__ = "pembayaran_agen"
    id = Column(Integer, primary_key=True, index=True)
    nama_agen = Column(String(100), nullable=False)
    harga_pertabung = Column(Float, nullable=False)
    jenis_tabung = Column(String(20), nullable=False)        # contoh: "12KG" / "50KG"
    nama_driver = Column(String(100), nullable=False)
    tanggal_pengiriman = Column(Date, nullable=False)
    jumlah_turun = Column(Integer, nullable=False)
    bukti = Column(String(200), nullable=True)               # simpan path / URL bukti
    status = Column(String(20), default="Belum Paid")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)



class Karyawan(Base):
    __tablename__ = "karyawan"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nik = Column(String(50), unique=True, index=True, nullable=False)
    nama = Column(String(100), nullable=False)
    jabatan = Column(String(100), nullable=False)
    kontak = Column(String(50), nullable=True)
    keterangan = Column(Text, nullable=True)
