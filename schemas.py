from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date, time


# ==================== DRIVER ====================
class DriverBase(BaseModel):
    nama: str
    role: str

class DriverCreate(DriverBase):
    password: str

class DriverOut(DriverBase):
    id: int
    class Config:
        orm_mode = True


# ==================== LAPORAN KIRIM ====================
class LaporanKirimBase(BaseModel):
    lokasi: str
    tanggal: date
    nama_driver: str
    plat_mobil: str
    jam_berangkat: time
    kapasitas: int
    jenis_tabung: str
    jumlah_dibawa: int
    jumlah_turun: Optional[int] = None
    tujuan: str
    alamat: Optional[str] = None
    kondisi_tabung: str
    keterangan: Optional[str] = None
    verifikasi_barang: Optional[str] = None

class LaporanKirimCreate(LaporanKirimBase):
    pass

class LaporanKirimOut(LaporanKirimBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True


# ==================== LAPORAN BONGKAR ====================
class LaporanBongkarBase(BaseModel):
    lokasi: str
    tanggal: date
    nama_driver: str
    jam_bongkar: time
    jenis_tabung: str
    jumlah_terbawa: int
    jumlah_turun: int
    sisa_dibawa: int
    jumlah_kosong: int
    kondisi_tabung: str
    nama_pangkalan: str
    alamat_pangkalan: Optional[str] = None
    catatan: Optional[str] = None
    media: Optional[str] = None

class LaporanBongkarCreate(LaporanBongkarBase):
    pass

class LaporanBongkarOut(LaporanBongkarBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True


# ==================== PRODUKSI MULAI ====================
class ProduksiMulaiBase(BaseModel):
    kepala_produksi: str
    tanggal: date
    nama_driver: str
    jam_mulai: time
    shift: Optional[str] = None

class ProduksiMulaiCreate(ProduksiMulaiBase):
    pass

class ProduksiMulaiOut(ProduksiMulaiBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True


# ==================== PRODUKSI SELESAI ====================
class ProduksiSelesaiBase(BaseModel):
    kepala_produksi: str
    tanggal: date
    jam_selesai: time
    tabung_kosong: int
    tabung_12: int
    tabung_50: int
    keterangan: Optional[str] = None

class ProduksiSelesaiCreate(ProduksiSelesaiBase):
    pass

class ProduksiSelesaiOut(ProduksiSelesaiBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True


# ==================== SEBELUM LOADING ====================
class SebelumLoadingBase(BaseModel):
    penanggung_jawab: str
    tanggal: date
    nama_driver: str
    jam_mulai: time
    netto_spa: int
    rotogen_kanan: Optional[int] = None
    rotogen_kiri: Optional[int] = None
    video_kiri: Optional[str] = None
    video_kanan: Optional[str] = None

class SebelumLoadingCreate(SebelumLoadingBase):
    pass

class SebelumLoadingOut(SebelumLoadingBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True


# ==================== SESUDAH LOADING ====================
class SesudahLoadingBase(BaseModel):
    penanggung_jawab: str
    tanggal: date
    jam_selesai: time
    video_kiri: Optional[str] = None
    video_kanan: Optional[str] = None

class SesudahLoadingCreate(SesudahLoadingBase):
    pass

class SesudahLoadingOut(SesudahLoadingBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True


# ==================== SKID MASUK DEPOT ====================
class SkidMasukDepotBase(BaseModel):
    nama_driver: str
    plat_mobil: Optional[str] = None
    tanggal: date
    rit: int
    jam_masuk: time

class SkidMasukDepotCreate(SkidMasukDepotBase):
    pass

class SkidMasukDepotOut(SkidMasukDepotBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True


# ==================== SKID KELUAR DEPOT ====================
class SkidKeluarDepotBase(BaseModel):
    nama_driver: str
    plat_mobil: Optional[str] = None
    tanggal: date
    jam_keluar: time
    jumlah_spa: int
    foto_spa: Optional[str] = None

class SkidKeluarDepotCreate(SkidKeluarDepotBase):
    pass

class SkidKeluarDepotOut(SkidKeluarDepotBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True


# ==================== SKID MASUK LAUT ====================
class SkidMasukLautBase(BaseModel):
    nama_driver: str
    plat_mobil: Optional[str] = None
    tanggal: date
    jam_masuk: time
    petugas_loading: str

class SkidMasukLautCreate(SkidMasukLautBase):
    pass

class SkidMasukLautOut(SkidMasukLautBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True


# ==================== SKID KELUAR LAUT ====================
class SkidKeluarLautBase(BaseModel):
    nama_driver: str
    plat_mobil: Optional[str] = None
    tanggal: date
    jam_keluar: time
    catatan: Optional[str] = None
    media: Optional[str] = None

class SkidKeluarLautCreate(SkidKeluarLautBase):
    pass

class SkidKeluarLautOut(SkidKeluarLautBase):
    id: int
    created_at: datetime
    class Config:
        orm_mode = True



# ==================== PEMBAYARAN AGEN ====================

class PembayaranAgenBase(BaseModel):
    nama_agen: str
    harga_pertabung: float
    jenis_tabung: str
    nama_driver: str
    tanggal_pengiriman: date | None = None   # bisa kosong
    jumlah_turun: int
    status: str = "Belum Paid"
    bukti: str | None = None                 # bisa kosong


class PembayaranAgenCreate(PembayaranAgenBase):
    """Schema untuk create data baru"""
    pass


class PembayaranAgenUpdate(BaseModel):
    """Schema untuk update data"""
    nama_agen: str | None = None
    harga_pertabung: float | None = None
    jenis_tabung: str | None = None
    nama_driver: str | None = None
    tanggal_pengiriman: date | None = None
    jumlah_turun: int | None = None
    status: str | None = None
    bukti: str | None = None


class PembayaranAgenResponse(PembayaranAgenBase):
    """Schema untuk response"""
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class KaryawanBase(BaseModel):
    nik: str
    nama: str
    jabatan: str
    kontak: Optional[str] = None
    keterangan: Optional[str] = None

class KaryawanCreate(KaryawanBase):
    pass

class KaryawanUpdate(KaryawanBase):
    pass

class KaryawanOut(KaryawanBase):
    id: int

    class Config:
        orm_mode = True