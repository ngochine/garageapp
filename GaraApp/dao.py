import hashlib
from datetime import datetime, date

from flask_login import current_user
from sqlalchemy import func, or_

from GaraApp import app, db
from models import PhieuTiepNhan, HangMuc, LinhKien, PhieuSuaChua, ChiTietHangMucSuaChua, ChiTietLinhKienSuaChua, \
    KhachHang, Xe, ct_quanlyquydinh, TaiKhoan, LoaiXe, CaLam, PhanCongCaLam, UserRole, NhanVien, ct_quanlylinhkien, \
    ct_quanlyhangmuc, QuyDinh, YeuCau, YeuCauStatus, HoaDon, DiaChi

def get_ds_phieu_tiep_nhan(loai_khach, loai_xe, sap_xep):
    query = ((PhieuTiepNhan.query
             .join(KhachHang, PhieuTiepNhan.maKhachHang == KhachHang.id)).join(Xe, PhieuTiepNhan.maXe == Xe.maXe).join(LoaiXe, LoaiXe.maLoaiXe == Xe.maLoaiXe)).filter(PhieuTiepNhan.trangThai=="Đang chờ sửa chữa")

    if loai_khach:
        query = query.filter(KhachHang.loaiKhachHang == loai_khach)

    if loai_xe:
        query = query.filter(LoaiXe.tenLoaiXe == loai_xe)

    if sap_xep:
        if sap_xep == "DESC":
            query = query.order_by(PhieuTiepNhan.ngayLap.desc())
        else:
            query = query.order_by(PhieuTiepNhan.ngayLap.asc())
    return query.all()

def get_chi_tiet_ptn(ptn_id):
    return PhieuTiepNhan.query.get(ptn_id)

def get_ds_hang_muc(page, ten_hang_muc):
    query = HangMuc.query
    if ten_hang_muc:
        query = query.filter(HangMuc.tenHangMuc.contains(ten_hang_muc))
    if page:
        size = app.config["PAGE_SIZE"]
        start = (int(page) - 1) * size
        query = query.slice(start, start + size)
    return query.all()

def get_ds_linh_kien(page, tenLinhKien):
    query = LinhKien.query
    if tenLinhKien:
        query = query.filter(LinhKien.tenLinhKien.contains(tenLinhKien))
    if page:
        size = app.config["PAGE_SIZE"]
        start = (int(page) - 1) * size
        query = query.slice(start, start + size)
    return query.all()

def get_ct_linhkien(lk_id):
    return LinhKien.query.get(lk_id)

def count_hangmuc(tenHangMuc):
    query = HangMuc.query
    if tenHangMuc:
        query = query.filter(HangMuc.tenHangMuc.contains(tenHangMuc))

    return query.count()

def count_linhkien(tenLinhKien):
    query = LinhKien.query
    if tenLinhKien:
        query = query.filter(LinhKien.tenLinhKien.contains(tenLinhKien))

    return query.count()

def create_yeucau(ma, loaiYeuCau, noiDung, ghiChu):
    try:
        yc = YeuCau(
            maBangYeuCau = ma,
            loaiYeuCau=loaiYeuCau,
            noiDung=noiDung,
            maTaiKhoanYeuCau=current_user.maTaiKhoan,
            ghiChu=ghiChu
        )
        db.session.add(yc)
        db.session.commit()
        return True
    except Exception:
        return False

def is_bao_thieu_linh_kien(maLinhKien):
    yc = db.session.query(YeuCau).filter(
        YeuCau.loaiYeuCau == "BAO_THIEU_LINH_KIEN",
        YeuCau.maBangYeuCau == int(maLinhKien)
    ).first()
    if yc is None:
        return False
    return True


def get_ds_loaixe():
    query = LoaiXe.query
    return query.all()

def create_phieu_sua_chua(ctPTN, selected_hangmuc, selected_linhkien):
    # cập nhtk trạng thái ptn
    ptn = get_chi_tiet_ptn(ctPTN.maPTN)
    if(ptn.trangThai.__eq__("Đã xử lý")):
        return False
    ptn.trangThai = "Đã xử lý"
    db.session.commit()

    # lưu psc
    psc = PhieuSuaChua(
        maPTN=ctPTN.maPTN,
        maTaiKhoan=current_user.maTaiKhoan
    )
    db.session.add(psc)
    db.session.commit()

    for hm in selected_hangmuc.values():
        ct_hm = ChiTietHangMucSuaChua(
            maPSC=psc.maPSC,
            maHangMuc=int(hm["maHangMuc"]),
            chiPhiHienHanh=hm["chiPhi"]
        )
        db.session.add(ct_hm)
    db.session.commit()

    #lưu linh kiện sửa chữa
    for lk in selected_linhkien.values():
        ct_lk = ChiTietLinhKienSuaChua(
            maPSC=psc.maPSC,
            maLinhKien=int(lk["maLinhKien"]),
            soLuong= int(lk["soLuong"]),
            donGiaHienHanh=lk["donGia"]
        )

        db.session.add(ct_lk)
    db.session.commit()

    # cập nhật kho linh kiện
    for lk in selected_linhkien.values():
        linhkien = LinhKien.query.get(int(lk["maLinhKien"]))
        linhkien.soLuongTon -= int(lk["soLuong"])
    db.session.commit()
    return True

def get_ct_phieusc(psc_id):
    return PhieuSuaChua.query.get(psc_id)

def update_phieu_sua_chua(psc_id):
    psc = get_ct_phieusc(psc_id)
    if psc:
        psc.trangThai = "Chờ thanh toán"
        db.session.commit()

def get_ds_psc(status=None, page=None, kw=None):
    query = PhieuSuaChua.query
    if kw:
        query = query.filter(PhieuSuaChua.maPSC.__eq__(kw))
    if status:
        query = query.filter(PhieuSuaChua.trangThai.__eq__(status))
    if page:
        size = app.config["PAGE_SIZE"]
        start = (int(page) - 1) * size
        query = query.slice(start, start + size)
    return query.all()

def count_psc(status=None, kw=None):
    query = PhieuSuaChua.query
    if kw:
        query = query.filter(PhieuSuaChua.maPSC.__eq__(kw))
    if status:
        query = query.filter(PhieuSuaChua.trangThai.__eq__(status))
    return query.count()

def update_quydinh(qd, quyDinhChinhSua):
    qd_cu = {
        "giaTri": qd.get("giatri")
    }
    noiDungCapNhat = []
    giaTriMoi = quyDinhChinhSua.get("giatri")

    # so snahs
    if giaTriMoi is not None and giaTriMoi != qd_cu["giaTri"]:
        noiDungCapNhat.append(
            f"Giá trị (cũ: {qd_cu['giaTri']}, mới: {giaTriMoi})"
        )
        qd["giaTri"] = giaTriMoi
    # print(noiDungCapNhat)

    if noiDungCapNhat:
        noiDung = "; ".join(noiDungCapNhat)
        ct = ct_quanlyquydinh(
            noiDungCapNhat=noiDung,
            maQuyDinh=qd.get("maQuyDinh"),
            maTaiKhoan=current_user.maTaiKhoan
        )
        db.session.add(ct)
        return True
    return False

def get_chi_tiet_quydinh(qd_id):
    return QuyDinh.query.get(qd_id)

def update_linhkien(lk, linhkienChinhSua):
    lk_cu = {
        "tenLinhKien": lk.get("tenLinhKien"),
        "donGia": lk.get("donGia"),
        "anhLinhKien": lk.get("anhLinhKien")
    }
    noiDungCapNhat = []

    tenMoi = linhkienChinhSua.get("tenLinhKien")
    donGiaMoi = linhkienChinhSua.get("donGia")
    anhMoi = linhkienChinhSua.get("anhLinhKien")

    # so snahs
    if tenMoi is not None and tenMoi != lk_cu["tenLinhKien"]:
        noiDungCapNhat.append(
            f"Tên (cũ: {lk_cu['tenLinhKien']}, mới: {tenMoi})"
        )
        lk["tenLinhKien"] = tenMoi

    if donGiaMoi is not None and donGiaMoi != lk_cu["donGia"]:
        noiDungCapNhat.append(
            f"Đơn giá (cũ: {lk_cu['donGia']}, mới: {donGiaMoi})"
        )
        lk["donGia"] = donGiaMoi

    if anhMoi is not None and anhMoi != lk_cu["anhLinhKien"]:
        noiDungCapNhat.append(
            f"Ảnh (cũ: {lk_cu['anhLinhKien']}, mới: {anhMoi})"
        )
        lk["anhLinhKien"] = anhMoi

    print(noiDungCapNhat)

    if noiDungCapNhat:
        noiDung = "; ".join(noiDungCapNhat)
        ct = ct_quanlylinhkien(
            noiDungCapNhat=noiDung,
            maLinhKien=lk.get("maLinhKien"),
            maTaiKhoan = current_user.maTaiKhoan
        )
        db.session.add(ct)
        return True

    return False

def get_chi_tiet_linhkien(lk_id):
    return LinhKien.query.get(lk_id)

def update_hangmuc(hm, hangmucChinhSua):
    hm_cu = {
        "tenHangMuc": hm.get("tenHangMuc"),
        "chiPhi": hm.get("chiPhi")
    }
    noiDungCapNhat = []

    tenMoi = hangmucChinhSua.get("tenHangMuc")
    chiPhiMoi = hangmucChinhSua.get("chiPhi")

    # so snahs
    if tenMoi is not None and tenMoi != hm_cu["tenHangMuc"]:
        noiDungCapNhat.append(
            f"Tên (cũ: {hm_cu['tenHangMuc']}, mới: {tenMoi})"
        )
        hm["tenHangMuc"] = tenMoi

    if chiPhiMoi is not None and chiPhiMoi != hm_cu["chiPhi"]:
        noiDungCapNhat.append(
            f"ChiPhi (cũ: {hm_cu['chiPhi']}, mới: {chiPhiMoi})"
        )
        hm["chiPhi"] = chiPhiMoi

    print(noiDungCapNhat)

    if noiDungCapNhat:
        noiDung = "; ".join(noiDungCapNhat)
        ct = ct_quanlyhangmuc(
            noiDungCapNhat=noiDung,
            maHangMuc=hm.get("maHangMuc"),
            maTaiKhoan = current_user.maTaiKhoan
        )
        db.session.add(ct)
        return True
    return False

def get_chi_tiet_hangmuc(hm_id):
    return HangMuc.query.get(hm_id)

def get_ds_calam(thu=None):
    query = CaLam.query
    if thu:
        query = query.filter(CaLam.thu.__eq__(thu))
    return query.all()

def create_phan_cong_calam(maTaiKhoan, maCaLams, ngayApDung, ghiChu):
    if maCaLams:
        for maCaLam in maCaLams:
            pc = PhanCongCaLam(
                maTaiKhoan=maTaiKhoan,
                maCaLam=maCaLam,
                ngayApDung=ngayApDung,
                ghiChu=ghiChu
            )
            db.session.add(pc)
        db.session.commit()
        return True
    return False

def add_taikhoan(tenNguoiDung, matKhau, avatar):
    matKhau = hashlib.md5(matKhau.strip().encode('utf-8')).hexdigest()
    tk = TaiKhoan(tenNguoiDung=tenNguoiDung.strip(),matKhau=matKhau, avatar=avatar)
    db.session.add(tk)
    db.session.commit()

def get_taikhoan_by_id(tk_id):
    return TaiKhoan.query.get(tk_id)

def get_ds_taikhoan(q=None, r=None, page=None):
    query = TaiKhoan.query
    q = q.strip() if q else None
    if q:
        if q.isdigit():
            query = query.filter(TaiKhoan.maNhanVien == int(q))
        else:
            query = query.join(NhanVien, TaiKhoan.maNhanVien == NhanVien.id).filter(or_(NhanVien.ho.contains(q),NhanVien.ten.contains(q)))
    if r:
        query = query.filter(TaiKhoan.vaiTro == UserRole[r])
    if page:
        size = app.config["PAGE_SIZE"]
        start = (int(page) - 1) * size
        query = query.slice(start, start + size)
    return query.all()

def count_ds_taikhoan():
    query = TaiKhoan.query.filter(TaiKhoan.vaiTro != UserRole.QUANLY)

    return query.count()

def get_ds_nhanvien(q=None):
    if q is None:
        query = db.session.query(NhanVien).join(TaiKhoan, isouter=True).filter(TaiKhoan.maTaiKhoan == None)
    return query.all()

def auth_user(tenNguoiDung=None,matKhau=None):
    matKhau = hashlib.md5(matKhau.encode("utf-8")).hexdigest()
    return TaiKhoan.query.filter(TaiKhoan.tenNguoiDung.__eq__(tenNguoiDung), TaiKhoan.matKhau.__eq__(matKhau)).first()

def get_ds_yeucau(loai=None, status = None, page=None):
    query = YeuCau.query
    if loai:
        query = query.filter(YeuCau.loaiYeuCau.__eq__(loai))
    if status:
        query = query.filter(YeuCau.trangThai.__eq__(status))
    if page:
        size = app.config["PAGE_SIZE"]
        start = (int(page) - 1) * size
        query = query.slice(start, start + size)

    return query.all()

def count_yeucau(loai=None, status=None):
    query = YeuCau.query

    if loai:
        query = query.filter(YeuCau.loaiYeuCau == loai)
    if status:
        query = query.filter(YeuCau.trangThai == status)

    return query.count()

def xuly_yeucau(action, yc_id):
    yc = YeuCau.query.get(yc_id)
    if yc:
        yc.trangThai = YeuCauStatus[action]
        yc.thoiGianXuLy = datetime.now()
        yc.maTaiKhoanXuLy = current_user.maTaiKhoan
        db.session.commit()

def auth_user(username, password):
    passwd=hashlib.md5(password.encode('utf-8')).hexdigest()
    return TaiKhoan.query.filter(TaiKhoan.tenNguoiDung.__eq__(username ), TaiKhoan.matKhau.__eq__(passwd)).first()

def get_user_byID(id):
    return TaiKhoan.query.filter_by(maTaiKhoan=id).first()

def kiemtra_matkhau(passwd):
    mk = hashlib.md5(passwd.encode('utf-8')).hexdigest()
    return mk == current_user.matKhau


def capnhat_matkhau(matkhau_hientai, matkhau_moi):
    if kiemtra_matkhau(matkhau_hientai):
        mk_moi = hashlib.md5(matkhau_moi.encode('utf-8')).hexdigest()
        current_user.matKhau = mk_moi
        db.session.commit()
        return True
    else:
        return False

def xoa_avatar():
    try:
        current_user.avatar = "https://res.cloudinary.com/dvfuzolim/image/upload/v1765610534/pngtree-dark-gray-simple-avatar-png-image_3418404_ejyjas.jpg"
        db.session.commit()
        return True
    except:
        return False

def thaydoi_avt(new_avt):
    try:
        current_user.avatar=new_avt
        db.session.commit()
        return True
    except:
        return False

def thaydoi_username(username_moi):
    uname_tontai = db.session.query(TaiKhoan).filter(
        TaiKhoan.tenNguoiDung == username_moi,
        TaiKhoan.maTaiKhoan != current_user.maTaiKhoan
    ).first()

    if uname_tontai:
        return False

    try:
        current_user.tenNguoiDung = username_moi
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False


def thaydoi_sdt(sdt_moi):
    sdt_tontai = db.session.query(NhanVien).filter(
        NhanVien.SDT == sdt_moi,
        NhanVien.id != current_user.maTaiKhoan
    ).first()

    if sdt_tontai:
        return False

    try:
        current_user.nhanvien.SDT = sdt_moi
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False

def thaydoi_email(email_moi):
    email_tontai = db.session.query(NhanVien).filter(
        NhanVien.email == email_moi,
        NhanVien.id != current_user.maTaiKhoan
    ).first()

    if email_tontai:
        return False
    try:
        current_user.nhanvien.email = email_moi
        db.session.commit()
        return True
    except:
        return False


def luu_PTN_nhap(dulieu, session):
    session["PTN_nhap"]=dulieu


def lay_PTN_nhap(session):
    return session.get("PTN_nhap", None)

#Kiểm tra quy dịnh xe nhận
def getSoLuongPTN_TrongNgay():
    ngayHienTai=date.today()
    so_luong=PhieuTiepNhan.query.filter(PhieuTiepNhan.ngayLap==ngayHienTai).count()
    return so_luong

def getSoXeTheoQuyDinh():
    qd=QuyDinh.query.filter_by(maQuyDinh=1).first()
    if qd:
        return qd.giaTri
    else:
        return None


#Lưu dữ liệu địa chỉ:
def TimVaTaoDiachi(dulieu_PTN_nhap):
    dc=DiaChi.query.filter_by(
        tinhThanh=dulieu_PTN_nhap.get("tinhthanh"),
        phuong=dulieu_PTN_nhap.get("phuong"),
        xa=dulieu_PTN_nhap.get("xa"),
        duong=dulieu_PTN_nhap.get("duong"),
    ).first()

    if not dc:
        dc=DiaChi(
            tinhThanh=dulieu_PTN_nhap.get("tinhthanh"),
            phuong=dulieu_PTN_nhap.get("phuong"),
            xa=dulieu_PTN_nhap.get("xa"),
            duong=dulieu_PTN_nhap.get("duong"),
        )
        db.session.add(dc)
        db.session.commit()
    return dc

#Lưu dữ liệu khách hàng
def TimVaTaoKhachHang(dulieu_PTN_nhap):
    dc=TimVaTaoDiachi(dulieu_PTN_nhap)

    ngay_sinh = None
    if dulieu_PTN_nhap.get("ngaysinh"):
        ngay_sinh = datetime.strptime(dulieu_PTN_nhap["ngaysinh"], "%Y-%m-%d").date()

    kh=KhachHang.query.filter_by(CCCD=dulieu_PTN_nhap["cccd"]).first()
    if not kh:
        kh=KhachHang(
            ho=dulieu_PTN_nhap["hoKhachHang"],
            ten=dulieu_PTN_nhap["tenKhachHang"],
            SDT=dulieu_PTN_nhap["SDTKhachHang"],
            gioiTinh=dulieu_PTN_nhap["gioitinh"],
            ngaySinh=ngay_sinh,
            CCCD=dulieu_PTN_nhap["cccd"],
            email=dulieu_PTN_nhap.get("email", None),
            loaiKhachHang=dulieu_PTN_nhap.get("loaikhachhang"),
            maDiaChi=dc.maDiaChi
        )
        db.session.add(kh)
        db.session.commit()
    else:
        kh.maDiaChi=dc.maDiaChi
        db.session.commit()

    return kh


# Lưu dữ liệu xe
def TimVaTaoXe(dulieu_PTN_nhap, maKH):
    x=Xe.query.filter_by(bienSoXe=dulieu_PTN_nhap["biensoxe"]).first()
    if not x:
        x = Xe(
            hangXe=dulieu_PTN_nhap["hangxe"],
            bienSoXe=dulieu_PTN_nhap["biensoxe"],
            loaiXe= LoaiXe.query.filter(LoaiXe.tenLoaiXe.__eq__(dulieu_PTN_nhap["loaixe"])).first(),
            maKhachHang=maKH
        )
        db.session.add(x)
        db.session.commit()

    return x

#Lưu dữ liệu phiếu tiếp nhận
def TaoVaLuuPTN(dulieu_PTN_nhap):
    kh=TimVaTaoKhachHang(dulieu_PTN_nhap)
    x=TimVaTaoXe(dulieu_PTN_nhap, kh.id)

    ptn=PhieuTiepNhan(
        loiMoTa=dulieu_PTN_nhap.get("loiMoTa"),
        ngayLap=date.today(),
        maXe=x.maXe,
        maKhachHang=kh.id,
        maTaiKhoan = current_user.maTaiKhoan
    )
    db.session.add(ptn)
    db.session.commit()

    return ptn


#Lấy danh sách phiếu sửa chữa
def get_dsPSC():
    dsPSC=PhieuSuaChua.query.all()
    List_PSC=[]
    for p in dsPSC:
        if p.trangThai.__eq__("Chờ thanh toán"):
            List_PSC.append(p)

    return List_PSC


#Lấy thông tin phiếu sửa chữa
def getThongTinPhieuChoThanhToan(maPSC):
    #Tạm thơi lọc cứng phiếu có maPSC là 1 thử, do mới tạo thử 1 psc đó thôi
    psc=PhieuSuaChua.query.filter_by(maPSC=maPSC).first()
    ptn=PhieuTiepNhan.query.filter_by(maPTN=psc.maPTN).first()
    thue=QuyDinh.query.filter_by(maQuyDinh=2).first()
    kh=KhachHang.query.filter_by(id=ptn.maKhachHang).first()


    if not psc:
        return None
    return {
        "maPSC": psc.maPSC,
        "trangThai": psc.trangThai,
        "maPTN": psc.maPTN,
        "maKhachHang": ptn.maKhachHang,
        "giaTriThue": thue.giaTri,
        "hoKhachHang":kh.ho,
        "tenKhachHang": kh.ten,
        "sdtKhachHang": kh.SDT,
    }

#Lấy thông tin chi tiết hạng mục sửa chữa
def getThongTinChiTietHangMuc(maPSC):
    ct_list = ChiTietHangMucSuaChua.query.filter_by(maPSC=maPSC).all()
    if not ct_list:
        return []

    ketqua = []
    for c in ct_list:
        h = HangMuc.query.filter_by(maHangMuc=c.maHangMuc).first()
        ketqua.append({
            "maHangMuc": c.maHangMuc,
            "tenHangMuc": h.tenHangMuc,
            "chiPhiHienHanh": c.chiPhiHienHanh,
        })

    return ketqua

#Lấy thông tin chi tiết linh kiện sửa chữa
def getThongTinChiTietLinhKien(maPSC):
    ct_list=ChiTietLinhKienSuaChua.query.filter_by(maPSC=maPSC).all()
    if not ct_list:
        return []

    ketqua = []
    for c in ct_list:
        lk=LinhKien.query.filter_by(maLinhKien=c.maLinhKien).first()
        ketqua.append({
            "maLinhKien": c.maLinhKien,
            "tenLinhKien": lk.tenLinhKien,
            "donGiaHienHanh": c.donGiaHienHanh,
            "soLuong": c.soLuong,
        })

    return ketqua

#Lấy danh sách hóa đơn
def getDanhSachHoaDon():
    return HoaDon.query.all()

#Lưu dữ liệu hóa đơn
def TaoVaLuuHoaDon(dulieu):
    hd=HoaDon(
        ngayTaoHoaDon=dulieu.get("ngayTaoHoaDon"),
        tongTien=dulieu.get("tongTien"),
        trangThai=dulieu.get("trangThai"),
        hinhThucThanhToan=dulieu.get("hinhThucThanhToan"),
        maTaiKhoan=dulieu.get("maTaiKhoan"),
        maPSC=dulieu.get("maPSC"),
    )

    #Thay đổi trạng thái phiếu sửa chữa
    psc = PhieuSuaChua.query.filter_by(maPSC=dulieu.get("maPSC")).first()
    psc.trangThai="Đã thanh toán"

    db.session.add(hd)
    db.session.commit()
    return hd.maHoaDon


def TimKiem_DsPSC(tu_khoa, loai_tim_kiem):
    tu_khoa=tu_khoa.strip()

    query=db.session.query(PhieuSuaChua).filter(
        PhieuSuaChua.trangThai=="Chờ thanh toán"
    )

    if loai_tim_kiem=="maPTN":
        query=query.filter(PhieuSuaChua.maPTN==tu_khoa)
    elif loai_tim_kiem=="maPSC":
        query=query.filter(PhieuSuaChua.maPSC==tu_khoa)
    elif loai_tim_kiem=="tenKH":
        hoTenKhachHang=KhachHang.ho+" "+KhachHang.ten
        tu=tu_khoa.split()
        query=(
            db.session.query(PhieuSuaChua)
            .join(PhieuTiepNhan, PhieuSuaChua.maPTN==PhieuTiepNhan.maPTN)
            .join(KhachHang, PhieuTiepNhan.maKhachHang==KhachHang.id)
        )

        for t in tu:
            query=query.filter(hoTenKhachHang.ilike("%"+t+"%"))

    dsPSC=query.all()
    ketqua=[]

    for p in dsPSC:
        ketqua.append({
            "maPSC": p.maPSC,
            "ngayLap": p.ngayLap,
            "maPTN": p.maPTN,
        })

    return ketqua


def getPhanCongCaLam():
    maTaiKhoan=current_user.maTaiKhoan
    return PhanCongCaLam.query.filter_by(maTaiKhoan=maTaiKhoan).all()

def timKiemHoaDon(tukhoa,kieutim):
    tukhoa=tukhoa.strip()
    query=HoaDon.query.join(PhieuSuaChua,HoaDon.phieusuachua).join(PhieuTiepNhan,PhieuSuaChua.phieuTiepNhan).join(KhachHang,PhieuTiepNhan.khachHang)

    if kieutim=="maHoaDon":
        query=query.filter(HoaDon.maHoaDon==tukhoa)
    elif kieutim=="tenKH":
        query=query.filter((KhachHang.ho+" "+KhachHang.ten).like(f"%{tukhoa}%"))

    return query.all()

def LuuYeuCau(noidung, ghichu, maHoaDon):
    yc=YeuCau(loaiYeuCau="SU_CO_THANH_TOAN",noiDung=noidung, ghiChu=ghichu, trangThai="CHUA_XU_LY", maTaiKhoanYeuCau=current_user.maTaiKhoan, maBangYeuCau=maHoaDon)

    hd=HoaDon.query.filter_by(maHoaDon=maHoaDon).first()
    hd.trangThai="CHUA_XU_LY"

    db.session.add(yc)
    db.session.commit()

    return yc

def count_xe_by_loaixe():
     return db.session.query(LoaiXe.maLoaiXe, LoaiXe.tenLoaiXe, func.count(Xe.maXe))\
         .join(Xe, LoaiXe.maLoaiXe == Xe.maLoaiXe, isouter=True).group_by(LoaiXe.maLoaiXe).all()


def thong_ke_theo_thoigian(time=None, month=None, year=None):
    year = str(int(year) + 2000) if year is not None else ""
    if time == "month":
        query = (
            db.session.query(func.extract('month', HoaDon.ngayTaoHoaDon), func.sum(HoaDon.tongTien))
            .filter(func.extract('year', HoaDon.ngayTaoHoaDon) == year)
            .group_by(func.extract('month', HoaDon.ngayTaoHoaDon))
        )
    else:
        query = (
            db.session.query( func.extract('day', HoaDon.ngayTaoHoaDon), func.sum(HoaDon.tongTien))
            .filter(func.extract('month', HoaDon.ngayTaoHoaDon) == month, func.extract('year', HoaDon.ngayTaoHoaDon) == year )
            .group_by(func.extract('day', HoaDon.ngayTaoHoaDon))
        )
    return query.all()


def thong_ke_theo_loi():
    TOP_LOI = {
        "Không nổ máy": "không nổ",
        "Hỏng phanh": "phanh",
        "Hết bình": "bình",
        "Hỏng đèn": "đèn",
        "Lỗi động cơ": "động cơ"
    }
    result = []

    for ten_loi, keyword in TOP_LOI.items():
        count = PhieuTiepNhan.query \
            .filter(PhieuTiepNhan.loiMoTa.ilike(f"%{keyword}%")) \
            .count()

        result.append((ten_loi, count))

    return result


if __name__ == '__main__':
    with app.app_context():
        print(thong_ke_theo_loi())

