import json
from flask_login import UserMixin
from sqlalchemy import ForeignKey, Enum, Column, Integer, String, DateTime, Float, Date, Time, Numeric, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, date

from GaraApp import db, app
from enum import Enum as MyEnum

class UserRole(MyEnum):
    NHANVIEN=1
    KYTHUATVIEN = 2
    THUNGAN = 3
    QUANLY=4


class YeuCauStatus(MyEnum):
    CHUA_XU_LY = 1
    DA_TU_CHOI = 2
    DA_CHAP_NHAN = 3

class CaLam(db.Model):
    __tablename__ = 'calam'
    maCaLam = Column(Integer, primary_key=True, autoincrement=True)
    thu= Column(Integer, nullable=False)
    gioBatDau=Column(Time, nullable=False)
    gioKetThuc=Column(Time, nullable=False)
    tenCa=Column(String(50), nullable=False)

    PhanCongCaLam=relationship('PhanCongCaLam', backref='calam', lazy=True)
    def __str__(self):
        thu = "Thứ " + str(self.thu)
        if self.thu == 8:
            thu = 'Chủ nhật'
        return f'Ca {self.maCaLam} - {thu} - {self.tenCa}'

class TaiKhoan(db.Model, UserMixin):
    __tablename__ = 'taikhoan'

    maTaiKhoan = Column(Integer, primary_key=True, autoincrement=True)
    tenNguoiDung = Column(String(100), nullable=False, unique=True)
    matKhau = Column(String(200), nullable=False)
    avatar = Column(String(500), default='https://res.cloudinary.com/dvfuzolim/image/upload/v1765610534/pngtree-dark-gray-simple-avatar-png-image_3418404_ejyjas.jpg')
    vaiTro= Column(Enum(UserRole), default=UserRole.NHANVIEN)
    ngayTaoTaiKhoan= Column(DateTime, default=datetime.now)

    phieuTiepNhan = relationship('PhieuTiepNhan', backref='taikhoan')
    phieuSuaChua = relationship('PhieuSuaChua', backref='taikhoan')
    hoaDon = relationship('HoaDon', backref='taikhoan')

    PhanCongCaLam = relationship("PhanCongCaLam", backref='taikhoan', lazy=True)
    maNhanVien = Column(Integer, ForeignKey('nhanvien.id'))

    ct_quanlyquydinh = relationship("ct_quanlyquydinh", backref="taikhoan", lazy=True)
    ct_quanlyhangmuc = relationship("ct_quanlyhangmuc", backref="taikhoan", lazy=True)
    ct_quanlylinhkien = relationship("ct_quanlylinhkien", backref="taikhoan", lazy=True)


    nguoiTaoYeuCau = relationship("YeuCau", foreign_keys="YeuCau.maTaiKhoanYeuCau",backref="taiKhoanYeuCau", lazy=True)
    nguoiXuLyYeuCau = relationship("YeuCau",foreign_keys="YeuCau.maTaiKhoanXuLy",backref="taiKhoanXuLy",lazy=True)

    def get_id(self):
        return str(self.maTaiKhoan)

    def __str__(self):
        return f'{self.tenNguoiDung} - {self.vaiTro.name}'

class PhanCongCaLam(db.Model):
    __tablename__ = 'phancongcalam'
    maPhanCong=Column(Integer, primary_key=True, autoincrement=True)

    maTaiKhoan=Column(Integer, ForeignKey('taikhoan.maTaiKhoan'))
    maCaLam=Column(Integer, ForeignKey('calam.maCaLam'))

    ngayApDung=Column(DateTime, nullable=False, default=datetime.now )
    ghiChu=Column(String(50))

class DiaChi(db.Model):
    __tablename__ = 'diachi'
    maDiaChi = Column(Integer, primary_key=True, autoincrement=True)
    tinhThanh = Column(String(100), nullable=False)
    phuong = Column(String(100))
    xa = Column(String(100))
    duong = Column(String(100))

class Nguoi(db.Model):
    __abstract__= True
    id = Column(Integer, primary_key=True, autoincrement=True)
    ho = Column(String(50), nullable=False)
    ten = Column(String(50), nullable=False)
    SDT = Column(String(10))
    gioiTinh = Column(String(10), nullable=False)
    ngaySinh = Column(Date)
    CCCD = Column(String(12), nullable=False, unique=True)
    email = Column(String(50))
    maDiaChi = Column(Integer, ForeignKey('diachi.maDiaChi'))

    def __str__(self):
        return str(self.id)

class NhanVien(Nguoi):
    __tablename__ = 'nhanvien'
    ngayVaoLam= Column(DateTime, nullable=False, default=datetime.now)
    luong = Column(Numeric(15,2), default=0.0)

    taiKhoan= relationship('TaiKhoan', backref='nhanvien', uselist=False)
    diaChi = relationship('DiaChi', backref='dsnhanvien')

    def __str__(self):
        return f"{self.id} - {self.ho} {self.ten}"

class KhachHang(Nguoi):
    __tablename__ = 'khachhang'
    loaiKhachHang = Column(String(50))

    xe = relationship('Xe', backref='khachhang', lazy = True)
    phieuTiepNhan = relationship('PhieuTiepNhan', backref='khachhang', lazy = True)

class LoaiXe(db.Model):
    __tablename__ = 'loaixe'
    maLoaiXe = Column(Integer, primary_key=True, autoincrement=True)
    tenLoaiXe =  Column(String(50), nullable=False, unique=True)

    def __str__(self):
        return self.tenLoaiXe

class Xe(db.Model):
    __tablename__ = 'xe'
    maXe = Column(Integer, primary_key=True, autoincrement=True)
    bienSoXe = Column(String(50), unique=True)
    hangXe = Column(String(50))

    maLoaiXe = Column(Integer, ForeignKey('loaixe.maLoaiXe'))
    maKhachHang = Column(Integer, ForeignKey('khachhang.id'))
    loaiXe = relationship('LoaiXe', backref='xe', lazy = True)

    def __str__(self):
        return str(self.maXe)

class ChiTietHangMucSuaChua(db.Model):
    __tablename__ = 'chitiethangmucsuachua'
    maPSC = Column(Integer, ForeignKey('phieusuachua.maPSC'), primary_key=True)

    maHangMuc = Column(Integer, ForeignKey('hangmuc.maHangMuc'), primary_key=True)
    chiPhiHienHanh = Column(Numeric(15,2))

class ChiTietLinhKienSuaChua(db.Model):
    __tablename__ = 'chitiethlinhkiensuachua'
    maPSC = Column(Integer, ForeignKey('phieusuachua.maPSC'), primary_key=True)

    maLinhKien = Column(Integer, ForeignKey('linhkien.maLinhKien'), primary_key=True)
    soLuong = Column(Integer, default=1)
    donGiaHienHanh = Column(Numeric(15,2))

class HangMuc(db.Model):
    __tablename__ = "hangmuc"
    maHangMuc = Column(Integer, primary_key=True, autoincrement=True)
    tenHangMuc = Column(String(100), nullable=False)
    chiPhi = Column(Numeric(15,2), nullable=False, default=0.0)

    # dsPhieuSuaChua = relationship("ChiTietHangMucSuaChua", backref='hangMucSuaChua', lazy=True)
    # chitiethangmucsuachua = relationship("ChiTietHangMucSuaChua", backref="hangmuc", lazy=True)
    #
    # ct_quanlyhangmuc = relationship("ct_quanlyhangmuc", backref="hangmuc", lazy=True)

    def __str__(self):
        return self.tenHangMuc

class ct_quanlyhangmuc(db.Model):
    __tablename__ = 'ct_quanlyhangmuc'
    quanLyHM_id=Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    ngayCapNhat=Column(Date, default=datetime.now)
    noiDungCapNhat=Column(String(300))
    maHangMuc=Column(Integer,ForeignKey("hangmuc.maHangMuc"))
    maTaiKhoan=Column(Integer, ForeignKey('taikhoan.maTaiKhoan'))


class LinhKien(db.Model):
    __tablename__ = 'linhkien'
    maLinhKien = Column(Integer, primary_key=True, autoincrement=True)
    tenLinhKien = Column(String(100), nullable=False)
    donGia = Column(Float, nullable=False, default=0.0)
    soLuongTon = Column(Integer, nullable=False)
    anhLinhKien = Column(String(500), default='https://res.cloudinary.com/dvfuzolim/image/upload/v1765610574/pngtree-cogwheel-gear-setting-symbol-repair-optimizing-workflow-concept-3d-render-illustration-png-image_9016823_pen2v6.png')

    # dsPhieuSuaChua = relationship("ChiTietLinhKienSuaChua", backref='linhkien', lazy=True)
    # ct_quanlylinhkien = relationship("ct_quanlylinhkien", backref="linhkien", lazy=True)

    def __str__(self):
        return self.tenLinhKien

class ct_quanlylinhkien(db.Model):
    __tablename__ = 'ct_quanlylinhkien'
    quanLyLK_id=Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    ngayCapNhat = Column(Date, default=date.today)
    noiDungCapNhat = Column(String(50))

    maLinhKien=Column(Integer,ForeignKey("linhkien.maLinhKien"))
    maTaiKhoan=Column(Integer,ForeignKey("taikhoan.maTaiKhoan"))

class PhieuTiepNhan(db.Model):
    __tablename__ = "phieutiepnhan"
    maPTN = db.Column(Integer, primary_key=True, autoincrement=True)
    ngayLap = Column(DateTime, nullable=False, default=datetime.now)
    loiMoTa = Column(db.String(100), nullable=False)
    trangThai = Column(db.String(100), nullable=False, default="Đang chờ sửa chữa")

    # khoa ngoai nhan vien tao phieu
    maTaiKhoan = Column(Integer, ForeignKey('taikhoan.maTaiKhoan'))
    taiKhoan = relationship('TaiKhoan', backref='dsPhieuTiepNhan', lazy=True)

    #Khoa ngoai khach hang
    maKhachHang = Column(Integer, ForeignKey('khachhang.id'))
    khachHang = relationship('KhachHang', backref='dsPhieuTiepNhan', lazy=True)

    #Khoa ngoai Xe
    maXe = Column(Integer, ForeignKey('xe.maXe'))
    xe = relationship('Xe', backref='dsPhieuTiepNhan', lazy=True)
    phieusuachua = relationship('PhieuSuaChua', backref='PhieuTiepNhan', lazy=True)

    def __str__(self):
        return str(self.maPTN)

class PhieuSuaChua(db.Model):
    __tablename__ = 'phieusuachua'

    maPSC = db.Column(Integer, primary_key=True, autoincrement=True)
    ngayLap = Column(DateTime, nullable=False, default=datetime.now)
    trangThai = Column(db.String(100), nullable=False, default="Đang sửa chữa")

    # khoa ngoai nhan vien tao phieu
    maTaiKhoan= Column(Integer, ForeignKey('taikhoan.maTaiKhoan'))
    taiKhoan = relationship('TaiKhoan', backref='dsPhieuSuaChua', lazy=True)

    #khoa ngoai phieu tiep nhan
    maPTN = Column(Integer, ForeignKey('phieutiepnhan.maPTN'))
    phieuTiepNhan = relationship('PhieuTiepNhan', backref='dsPhieuSuaChua')
    hoaDon = relationship('HoaDon', backref='phieusuachua', lazy=True)

    # hang muc
    dsHangMuc = relationship("ChiTietHangMucSuaChua", backref='phieuSuaChua', lazy=True)
    # linh kien
    dsLinhKien = relationship("ChiTietLinhKienSuaChua", backref='phieuSuaChua', lazy=True)

    def __str__(self):
        return str(self.maPSC)

class HoaDon(db.Model):
    __tablename__ = 'hoadon'
    maHoaDon=Column(Integer,primary_key=True, nullable=False, autoincrement=True)
    ngayTaoHoaDon=Column(Date, nullable=False)
    tongTien=Column(Numeric(15,2), nullable=False)
    trangThai=Column(String(50), nullable=False)
    hinhThucThanhToan=Column(String(50))

    maTaiKhoan=Column(Integer, ForeignKey('taikhoan.maTaiKhoan'))
    maPSC=Column(Integer,ForeignKey('phieusuachua.maPSC'))

    def __str__(self):
        return str(self.maHoaDon)

# bảng quy định
class QuyDinh(db.Model):
    __tablename__ = 'quydinh'
    maQuyDinh=Column(Integer,primary_key=True, nullable=False, autoincrement=True)
    tenQuyDinh=Column(String(50), nullable=False)
    giaTri=Column(Float, nullable=False)
    donVi=Column(String(20), nullable=False)
    ngayTao=Column(Date, default=date.today)

    ct_quanlyquydinh = relationship("ct_quanlyquydinh", backref="quydinh", lazy=True)


    def __str__(self):
        return self.tenQuyDinh

class ct_quanlyquydinh(db.Model):
    __tablename__ = 'ct_quanlyquydinh'
    quanLyQD_id=Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    ngayCapNhat=Column(Date, default=date.today)
    noiDungCapNhat=Column(String(50))

    maTaiKhoan=Column(Integer, ForeignKey('taikhoan.maTaiKhoan'))
    maQuyDinh=Column(Integer,ForeignKey('quydinh.maQuyDinh'))

class YeuCau(db.Model):
    __tablename__ = 'yeucau'
    maYeuCau=Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    maBangYeuCau = Column(Integer)
    loaiYeuCau=Column(String(50))
    noiDung=Column(String(100), nullable=False)
    ghiChu=Column(String(100))
    trangThai=Column(Enum(YeuCauStatus), default=YeuCauStatus.CHUA_XU_LY)
    thoiGianTao=Column(DateTime, default=datetime.now)
    thoiGianXuLy=Column(DateTime)

    maTaiKhoanYeuCau=Column(Integer,ForeignKey("taikhoan.maTaiKhoan"))
    maTaiKhoanXuLy=Column(Integer,ForeignKey("taikhoan.maTaiKhoan"), nullable=True)

if __name__ == "__main__":
    with app.app_context():
        db.drop_all()
        db.create_all()
