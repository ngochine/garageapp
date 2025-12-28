import math
from collections import defaultdict
from datetime import datetime, date, timedelta
from decimal import Decimal

import cloudinary
import cloudinary.uploader
from flask import Flask, render_template, request, session, jsonify, flash, url_for
from sqlalchemy.sql.functions import user
from werkzeug.utils import redirect
import dao
from GaraApp import app, login, admin
from flask_login import login_user, logout_user, login_required, current_user

from models import PhieuTiepNhan, KhachHang, PhieuSuaChua, HoaDon, YeuCauStatus, UserRole


@app.route("/")
def index():
    if current_user.is_authenticated and current_user.vaiTro == UserRole.QUANLY:
        return redirect("/admin")
    return render_template("trangchu.html")

@app.route("/taoPSC")
def tao_phieu_sua_chua():
    loai_khach = request.args.get("loai_khach", '')
    loai_xe = request.args.get("loai_xe",'')
    sap_xep = request.args.get("sap_xep",'')

    dsPTN = dao.get_ds_phieu_tiep_nhan(loai_khach=loai_khach, loai_xe=loai_xe, sap_xep=sap_xep)
    ptn_id = request.args.get("ptn_id", type=int)
    ctPTN = dao.get_chi_tiet_ptn(ptn_id)
    loaiXe = dao.get_ds_loaixe()
    selected_hangmuc = session.get('selected_hangmuc', {})
    return render_template("taophieusc/taoPSC.html",
                           dsPTN=dsPTN, ctPTN=ctPTN, selected_hangmuc=selected_hangmuc,
                           loaiXe = loaiXe, loai_khach=loai_khach, sap_xep=sap_xep, loai_xe=loai_xe)

@app.route("/api/hangmuc", methods=["POST"])
def them_hang_muc():
    try:
        selected_hangmuc = session.get('selected_hangmuc', {})
        maHangMuc = str(request.json.get('maHangMuc'))
        if maHangMuc not in selected_hangmuc:
            selected_hangmuc[maHangMuc] = {
                "maHangMuc": maHangMuc,
                "tenHangMuc": request.json.get("tenHangMuc"),
                "chiPhi": request.json.get("chiPhi"),
            }
        session['selected_hangmuc'] = selected_hangmuc
        return jsonify({"selected_hangmuc": selected_hangmuc})
    except Exception as ex:
        return jsonify({"err_msg": ex, "status": 500})

@app.route("/api/hangmuc/<int:maHangMuc>", methods=["DELETE"])
def xoa_hang_muc(maHangMuc):
    try:
        selected_hangmuc = session.get('selected_hangmuc', {})
        maHangMuc_str = str(maHangMuc)
        if selected_hangmuc and maHangMuc_str in selected_hangmuc:
            del selected_hangmuc[maHangMuc_str]
            session['selected_hangmuc'] = selected_hangmuc

        return jsonify({"selected_hangmuc": selected_hangmuc, "status": 200})

    except Exception as ex:
        return jsonify({"err_msg": ex, "status": 500})


@app.route("/taoPSC/ptn_id=<int:ptn_id>/chonHangMuc")
def chon_hang_muc(ptn_id=None):
    ten_hang_muc = request.args.get("ten_hang_muc")
    page = request.args.get("page", default=1, type=int)
    pages = math.ceil(dao.count_hangmuc(ten_hang_muc) / app.config["PAGE_SIZE"])
    dsHangMuc = dao.get_ds_hang_muc(page=page, ten_hang_muc=ten_hang_muc)
    if ptn_id:
        ctPTN = dao.get_chi_tiet_ptn(ptn_id)
    else:
        ctPTN = None

    selected_hangmuc = session.get("selected_hangmuc", {})
    return render_template("taophieusc/chonHangMuc.html",
                           ctPTN=ctPTN, dsHangMuc=dsHangMuc, pages=pages, page=page, selected_hangmuc=selected_hangmuc)

@app.route("/api/linhkien", methods=["POST"])
def them_linh_kien():
    try:
        selected_linhkien = session.get('selected_linhkien', {})
        maLinhKien = str(request.json.get("maLinhKien"))
        if maLinhKien not in selected_linhkien:
            selected_linhkien[maLinhKien] = {
                "maLinhKien": int(request.json.get("maLinhKien")),
                "tenLinhKien": request.json.get("tenLinhKien"),
                "donGia": request.json.get("donGia"),
                "soLuong": 1,
                "soLuongTon": int(request.json.get("soLuongTon"))
            }
            session['selected_linhkien'] = selected_linhkien
            return jsonify({ "selected_linhkien": selected_linhkien, "status": 201 })
        else:
            return jsonify({"msg": "Linh kiện đã tồn tại", "status": 200, "selected_linhkien": selected_linhkien})

    except Exception as ex:
        return jsonify({"err_msg": ex, "status": 500})

@app.route("/api/linhkien/<int:maLinhKien>", methods=['PUT'])
def update_linhkien(maLinhKien):
    try:
        selected_linhkien = session.get("selected_linhkien", {})
        maLinhKien_str = str(maLinhKien)
        soLuong = int(request.json.get("soLuong"))
        if soLuong <= 0:
            return jsonify({"err_msg": "Số lượng phải lớn hơn 0", "status": 400})

        if selected_linhkien[maLinhKien_str]["soLuongTon"] < soLuong:
            return jsonify({"err_msg": "Số lượng lớn hơn số lượng tồn", "status": 400})

        selected_linhkien[maLinhKien_str]["soLuong"] = soLuong
        session['selected_linhkien'] = selected_linhkien
        return jsonify({"selected_linhkien": selected_linhkien, "status": 200})
    except Exception as ex:
        return jsonify({"err_msg": ex, "status":500})

@app.route("/api/linhkien/<int:maLinhKien>", methods=['DELETE'])
def xoa_linh_kien(maLinhKien):
    try:
        selected_linhkien = session.get('selected_linhkien', {})
        maLinhKien_str = str(maLinhKien)

        if selected_linhkien and maLinhKien_str in selected_linhkien:
            del selected_linhkien[maLinhKien_str]
            session['selected_linhkien'] = selected_linhkien

        return jsonify({"selected_linhkien": selected_linhkien, "status": 200})

    except Exception as ex:
        return jsonify({"err_msg": ex, "status":500})

@app.route("/api/baothieulinhkien/<int:maLinhKien>", methods=["POST"])
def bao_thieu_linh_kien(maLinhKien):
    try:
        lk = dao.get_ct_linhkien(maLinhKien)
        loaiYeuCau = request.json.get("loaiYeuCau")
        noiDung = f"Thiếu linh kiện {maLinhKien}: {lk.tenLinhKien}"
        ghiChu = request.json.get("ghiChu")
        if dao.is_bao_thieu_linh_kien(maLinhKien):
            return jsonify({"err_msg": "Linh kiện đã được báo thiếu", "status": 400})

        dao.create_yeucau(ma = maLinhKien, loaiYeuCau=loaiYeuCau, noiDung=noiDung, ghiChu = ghiChu)
        return jsonify({"status": 200})

    except Exception as ex:
        return jsonify({"err_msg": str(ex), "status":500})

@app.route("/taoPSC/ptn_id=<int:ptn_id>/chonLinhKien")
def chon_linh_kien(ptn_id=None):
    ten_linh_kien = request.args.get("ten_linh_kien")
    page = request.args.get("page", default=1, type=int)
    pages = math.ceil(dao.count_linhkien(ten_linh_kien) / app.config["PAGE_SIZE"])
    dsLinhKien = dao.get_ds_linh_kien(page, ten_linh_kien)
    if ptn_id:
        ctPTN = dao.get_chi_tiet_ptn(ptn_id)
    else:
        ctPTN = None

    for lk in dsLinhKien:
        lk.da_bao_thieu = dao.is_bao_thieu_linh_kien(lk.maLinhKien)
    selected_hangmuc = session.get("selected_hangmuc", {})
    selected_linhkien = session.get("selected_linhkien", {})

    return render_template("taophieusc/chonLinhKien.html",
                           ctPTN=ctPTN, selected_hangmuc=selected_hangmuc, dsLinhKien=dsLinhKien,
                           selected_linhkien=selected_linhkien, pages=pages, page=page)


@app.route("/taoPSC/ptn_id=<int:ptn_id>/xacNhanTao", methods=["get", "post"])
def xac_nhan_tao(ptn_id=None):
    ctPTN = dao.get_chi_tiet_ptn(ptn_id)
    selected_hangmuc = session.get('selected_hangmuc', {})
    selected_linhkien = session.get("selected_linhkien", {})
    err_msg= None
    if request.method.__eq__("POST"):
        if dao.create_phieu_sua_chua(ctPTN, selected_hangmuc=selected_hangmuc, selected_linhkien=selected_linhkien):
            if "selected_hangmuc" in session:
                del session["selected_hangmuc"]

            if "selected_linhkien" in session:
                del session["selected_linhkien"]

            flash("Đã tạo thành công phiếu sửa chữa", "success")
            return redirect('/taoPSC')
        else:
            err_msg = 'Có lỗi xảy ra khi tạo phiếu'

    return render_template("taophieusc/xacNhanTaoPSC.html",
                           ctPTN=ctPTN, selected_hangmuc=selected_hangmuc, selected_linhkien=selected_linhkien, err_msg=err_msg)

@app.route("/phieusc/capnhattrangthai", methods=["GET"])
def cap_nhat_trang_thai():
    status = request.args.get('status')
    kw = request.args.get('kw')

    count_tatca = dao.count_psc(kw=kw, status=None)
    count_dangsua = dao.count_psc(kw=kw, status="Đang sửa chữa")
    count_hoanthanh = dao.count_psc(kw=kw, status="Chờ thanh toán")

    page = request.args.get("page", default=1, type=int)
    pages = math.ceil(dao.count_psc(kw=kw, status=status) / app.config["PAGE_SIZE"])
    dsPhieu = dao.get_ds_psc(page=page, kw=kw, status=status)

    return render_template("taophieusc/trangThaiPhieuSC.html", dsPhieu = dsPhieu, count_tatca = count_tatca,
                           count_dangsua = count_dangsua, count_hoanthanh= count_hoanthanh,pages=pages, page=page)

@app.route("/phieusc/api/<int:psc_id>", methods=["POST"])
def cap_nhat_hoan_thanh(psc_id):
    try:
        dao.update_phieu_sua_chua(psc_id)
        flash("Cập nhật trạng thái thành công", "success")
        status=request.form.get("status")
        kw = request.form.get("kw")
        page = request.form.get("page")
        return redirect(url_for("cap_nhat_trang_thai",status=status,kw=kw,page=page))

    except Exception as ex:
        flash(f"Có lỗi xảy ra: {ex}", "danger")
        return redirect(url_for("cap_nhat_trang_thai"))

@app.route('/admin-login', methods=['POST'])
def my_admin_login():
    err_msg = None
    tenNguoiDung = request.form.get("tenNguoiDung")
    matKhau = request.form.get("matKhau")

    tk = dao.auth_user(tenNguoiDung, matKhau)

    if tk:
        login_user(tk)
        return redirect("/admin")
    else:
        err_msg = "Tên người dùng hoặc mật khẩu không đúng"
    return err_msg


@login.user_loader
def get_user(tk_id):
    return dao.get_taikhoan_by_id(tk_id=tk_id)


@app.route("/logout")
def logout_my_user():
    logout_user()
    session.clear()
    return redirect("/")


@app.route('/admin/api/phan-cong-ca', methods=['POST'])
@login_required
def phan_cong_ca():
    maTaiKhoan = request.form.get('maTaiKhoan')
    maCaLam = request.form.getlist('maCaLam')
    ngayApDung = request.form.get('ngayApDung')
    ghiChu = request.form.get('ghiChu')

    if maTaiKhoan and maCaLam and dao.create_phan_cong_calam(
        maTaiKhoan, maCaLam, ngayApDung, ghiChu
    ):
        flash("Đã phân công thành công", "success")
    else:
        flash("Phân công không thành công", "danger")

    return redirect('/admin/phancongcalam')

@app.route('/dangnhap', methods=['GET', 'POST'])
def dangnhap():
    if current_user.is_authenticated:
        return redirect("/")

    err_msg=None
    if request.method == 'POST':
        uname = request.form.get('uname')
        password = request.form.get('pswd')

        user= dao.auth_user(uname, password)

        if user:
            login_user(user)
            return redirect('/')
        else:
            err_msg="Tên người dùng hoặc mật khẩu chưa đúng!!!"

    return render_template("user/dangnhap.html", err_msg=err_msg)

@login.user_loader
def load_user(id):
    return dao.get_user_byID(id)

@app.route('/taikhoan', methods=['GET', 'POST'])
def thongtintaikhoan():
    return render_template("user/thongtintaikhoan.html")

@app.route('/capnhatmatkhau', methods=['GET', 'POST'])
def capnhatmatkhau():
    err_msg=None
    success_msg=None

    if request.method == 'POST':
        matkhau_hientai = request.form.get('pswd-current')
        matkhau_moi = request.form.get('pswd-new')
        matkhau_moi_nhaplai = request.form.get('pswd-new-again')

        if matkhau_moi == matkhau_moi_nhaplai:
            if dao.capnhat_matkhau(matkhau_hientai, matkhau_moi):
                success_msg="Đã thay đổi mật khẩu thành công !"
            else:
                err_msg="Mật khẩu hiện tại chưa đúng!!!"

        else:
            err_msg="Mật khẩu mới chưa trùng khớp !!!"

    return render_template("user/capnhatmatkhau.html", err_msg=err_msg, success_msg=success_msg)


#Trang thay đổi hồ sơ người dùng : ảnh hồ sơ, số điện thoại, email
@app.route('/capnhathoso', methods=['GET', 'POST'])
def capnhathoso():
    success_msg = None
    err_msg = None

    success_action=None

    if request.method == 'GET':
        action=request.args.get('action')
        return  render_template("user/capnhathoso.html", action=action, success_msg=success_msg)

    #Nếu post là yêu cầu kiểm tra mật khẩu
    action = request.form.get("action")
    passwd = request.form.get("pswd-current")
    if passwd:
        if dao.kiemtra_matkhau(passwd):
            success_msg = "Mật khẩu hợp lệ!"
            return render_template("user/capnhathoso.html", action=action, success_msg=success_msg)
        else:
            err_msg = "Mật khẩu chưa đúng!"
            return render_template("user/capnhathoso.html", action=action, err_msg=err_msg)

    #Nếu post là yêu cầu xác nhận thực hiện các action

    elif action == "confirm_change_phone":
        sdt_moi=request.form.get("phone-new")
        if dao.thaydoi_sdt(sdt_moi):
            success_action="Đã thay đổi số điện thoại thành công."
            return render_template("user/thongtintaikhoan.html", action=action, success_action=success_action)
        else:
            err_msg="Số điện thoại đã tồn tại."
            return render_template("user/capnhathoso.html", action="change_phone", err_msg=err_msg)

    elif action == "confirm_change_email":
        email_moi=request.form.get("email-new")
        if dao.thaydoi_email(email_moi):
            success_action="Đã thay đổi email thành công."
            return render_template("user/thongtintaikhoan.html", action=action, success_action=success_action)
        else:
            err_msg="Email đã tồn tại."
            return render_template("user/capnhathoso.html",action="change_email",err_msg=err_msg)
    elif action == "confirm_change_username":
        username_moi=request.form.get("uname")
        if dao.thaydoi_username(username_moi):
            success_action="Đã thay đổi username thành công."
            return render_template("user/thongtintaikhoan.html", action=action, success_action=success_action)
        else:
            err_msg="Username đã tồn tại."
            return render_template("user/capnhathoso.html",action="change_username",err_msg=err_msg)

    elif action == "confirm_change_avatar":
        avt_moi=request.files.get("new-avt")

        if avt_moi:
            rs = cloudinary.uploader.upload(avt_moi)
            new_avatar = rs['secure_url']
            if dao.thaydoi_avt(new_avatar):
                success_action="Đã thay đổi ảnh hồ sơ thành công."
                return render_template("user/thongtintaikhoan.html", action=action, success_action=success_action)
            else:
                err_msg="Có lỗi xảy ra!"
                return render_template("user/capnhathoso.html",action="change_avatar",err_msg=err_msg)

    elif action == "confirm_delete_avatar":
        if dao.xoa_avatar():
            success_action = "Đã xóa ảnh hồ sơ thành công."
            return render_template("user/thongtintaikhoan.html", action=action, success_action=success_action)
        else:
            err_msg = "Có lỗi xảy ra!"
            return render_template("user/capnhathoso.html", action="delete_avatar", err_msg=err_msg)

    return render_template("user/thongtintaikhoan.html", success_action=success_action, err_msg=err_msg)


# # Trang chủ đã đăng nhập
# @app.route('/trangchu/dangnhap')
# def trangchu():
#     return render_template("trangchu_daDangNhap.html")

# Phiếu tiếp nhận : Lấy dữ liệu xuống server
@app.route('/lapphieutiepnhan', methods=['GET', 'POST'])
def phieutiepnhan():
    soXeDaNhan=dao.getSoLuongPTN_TrongNgay()
    soXeQuyDinh=dao.getSoXeTheoQuyDinh()

    if request.method == 'POST':
        dulieu={
            "hoKhachHang": request.form.get("hoKhachHang"),
            "tenKhachHang": request.form.get("tenKhachHang"),
            "SDTKhachHang": request.form.get("SDTKhachHang"),
            "tinhthanh": request.form.get("tinhthanh"),
            "phuong": request.form.get("phuong"),
            "xa": request.form.get("xa"),
            "duong": request.form.get("duong"),
            "cccd": request.form.get("cccd"),
            "ngaysinh": request.form.get("ngaysinh"),
            "email": request.form.get("email"),
            "gioitinh" : request.form.get("gioitinh"),
            "loaikhachhang": request.form.get("loaikhachhang"),
            "hangxe": request.form.get("hangxe"),
            "biensoxe": request.form.get("biensoxe"),
            "loaixe": request.form.get("loaixe"),
            "loiMoTa": request.form.get("loiMoTa"),
        }

        dao.luu_PTN_nhap(dulieu,session)
        return redirect("/lapphieutiepnhan/xacnhan")

    return render_template("taophieutiepnhan/phieutiepnhan.html", soXeDaNhan=soXeDaNhan, soXeQuyDinh=soXeQuyDinh)

@app.route('/lapphieutiepnhan/xacnhan', methods=['GET'])
def xacnhan_phieutiepnhan():
    #Hiển thị dữ liệu từ trang lapphieutiepnhan lên xem lại
    dulieu=dao.lay_PTN_nhap(session)
    ngayLap=datetime.now().strftime("%Y-%m-%d")
    return render_template("taophieutiepnhan/xacnhan_phieutiepnhan.html", dulieu=dulieu, ngayLap=ngayLap)

@app.route('/lapphieutiepnhan/thongbao', methods=['POST'])
def thongbao_luu_phieutiepnhan():
    dulieu=dao.lay_PTN_nhap(session)
    if dulieu:
        ptn= dao.TaoVaLuuPTN(dulieu)
        session.pop("PTN_nhap", None)
        maPTN=ptn.maPTN
        ngayLap=ptn.ngayLap.strftime("%Y-%m-%d")
        thongbao="Phiếu tiếp nhận đã được tạo thành công !!!"

        return render_template("taophieutiepnhan/xacnhan_phieutiepnhan.html",
                                dulieu=dulieu,
                                ngayLap=ngayLap,
                                maPTN=maPTN,
                                thongbao=thongbao,
                               )
    return redirect("/lapphieutiepnhan") #Nếu trống thì quay về đây

@app.route('/chothanhtoan', methods=['GET', 'POST'])
def chothanhtoan():
    tu_khoa=request.args.get("tukhoa"," ").strip()
    loai_tim_kiem=request.args.get("kieutim"," ").strip()

    if tu_khoa and loai_tim_kiem:
        dsPSC= dao.TimKiem_DsPSC(tu_khoa, loai_tim_kiem)
    else:
        dsPSC = dao.get_dsPSC()

    # Phân trang
    page=request.args.get("page",1, type=int) #Trang hiện tại mặc định là 1
    soPhieu_1Trang=5
    tongPhieuSuaChua = len(dsPSC)
    pages = math.ceil(tongPhieuSuaChua / soPhieu_1Trang) if tongPhieuSuaChua else 0

    batdau= (page-1)*soPhieu_1Trang
    ketthuc= batdau+soPhieu_1Trang
    dsPSC_page=dsPSC[batdau:ketthuc]


    thongtin=[]
    if dsPSC:
        for p in dsPSC_page:
            if isinstance(p, dict):
                maPSC = p["maPSC"]
                maPTN = p["maPTN"]
                ngayLapPSC = p["ngayLap"]
            else:
                maPSC=p.maPSC
                ngayLapPSC=p.ngayLap
                maPTN=p.maPTN

            ptn=PhieuTiepNhan.query.filter_by(maPTN=maPTN).first()
            kh=KhachHang.query.filter_by(id=ptn.maKhachHang).first()

            thongtin.append({
                "maPSC": maPSC,
                "maPTN": maPTN,
                "hoKhachHang": kh.ho,
                "tenKhachHang": kh.ten,
                "ngayLapPSC": ngayLapPSC,
                "ngayLapPTN": ptn.ngayLap,
            })

    #Xử lý khi chọn
    thongtin_chon=None
    maPSC_chon = request.args.get("maPSC", type=int)
    if maPSC_chon:
        p=PhieuSuaChua.query.filter_by(maPSC=maPSC_chon).first()
        ptn=PhieuTiepNhan.query.filter_by(maPTN=p.maPTN).first()
        kh = KhachHang.query.filter_by(id=ptn.maKhachHang).first()
        thongtin_chon={
            "maPSC": maPSC_chon,
            "maPTN": p.maPTN,
            "maKhachHang": kh.id,
            "hoKhachHang": kh.ho,
            "tenKhachHang": kh.ten,
            "ngayLapPSC": p.ngayLap,
            }




    return render_template("taohoadon/chothanhtoan.html", thongtin=thongtin, thongtin_chon=thongtin_chon
                           , pages=pages, page=page, tukhoa=tu_khoa, kieutim=loai_tim_kiem)

@app.route('/taohoadon')
def taohoadon():
    maPSC=request.args.get("maPSC")

    #Thông tin phiếu sửa chữa
    tt= dao.getThongTinPhieuChoThanhToan(maPSC)

    maPTN=tt.get("maPTN")
    maKhachHang=tt.get("maKhachHang")
    giaTriThue=tt.get("giaTriThue")

    #danh sach thông tin chi tiết hạng mục sửa chữa
    ds_hangmuc= dao.getThongTinChiTietHangMuc(maPSC)
    tongChiPhi=Decimal(0)
    for hm in ds_hangmuc:
        tongChiPhi+=hm.get("chiPhiHienHanh")

    # danh sach thông tin chi tiết linh kien sửa chữa
    ds_linhkien = dao.getThongTinChiTietLinhKien(maPSC)
    tongDonGia=Decimal(0)
    for lk in ds_linhkien:
        tongDonGia+=lk.get("donGiaHienHanh") * lk.get("soLuong")

    tongTruocThue = tongChiPhi + tongDonGia
    tienThue = tongTruocThue * Decimal(giaTriThue) / Decimal(100)
    tongHoaDon = tongTruocThue + tienThue

    return render_template("taohoadon/taohoadon.html", maPSC=maPSC, maPTN=maPTN, maKhachHang=maKhachHang,
                           giaTriThue=giaTriThue, ds_hangmuc=ds_hangmuc, ds_linhkien=ds_linhkien, tongHoaDon=tongHoaDon)

@app.route('/xulythanhtoan', methods=['GET', 'POST'])
def xulythanhtoan():
    ngayThanhToan=date.today().strftime("%Y-%m-%d")
    if request.method == "POST":
        maPSC = request.form.get("maPSC")
        soTien = request.form.get("soTien")
        tongHoaDon=request.form.get("tongHoaDon")
    else:
        maPSC = request.args.get("maPSC")
        soTien = None

    soTien = Decimal(soTien)
    tongHoaDon = Decimal(tongHoaDon)
    tienThua = soTien - tongHoaDon

    tt= dao.getThongTinPhieuChoThanhToan(maPSC)
    hoKhachHang=tt.get("hoKhachHang")
    tenKhachHang=tt.get("tenKhachHang")
    sdtKhachHang=tt.get("sdtKhachHang")
    giaTriThue = tt.get("giaTriThue")

    # danh sach thông tin chi tiết hạng mục sửa chữa
    ds_hangmuc = dao.getThongTinChiTietHangMuc(maPSC)

    # danh sach thông tin chi tiết linh kien sửa chữa
    ds_linhkien = dao.getThongTinChiTietLinhKien(maPSC)


    return render_template("taohoadon/xulythanhtoan.html",
                           ngayThanhToan=ngayThanhToan, maPSC=maPSC, hoKhachHang=hoKhachHang,tenKhachHang=tenKhachHang,
                           sdtKhachHang=sdtKhachHang,giaTriThue=giaTriThue,ds_hangmuc=ds_hangmuc,ds_linhkien=ds_linhkien,
                           soTien=soTien, tongHoaDon=tongHoaDon, tienThua=tienThua)

@app.route('/xulythanhtoan+thongbao', methods=['GET', 'POST'])
def thongbao_luu_hoadon():
    maPSC = request.form.get("maPSC")
    tongHoaDon=request.form.get("tongHoaDon")
    ngayThanhToan=date.today().strftime("%Y-%m-%d")
    giaTriThue = request.form.get("giaTriThue")


    hd={
        "ngayTaoHoaDon": ngayThanhToan,
        "tongTien": tongHoaDon,
        "trangThai": "Đã thanh toán",
        "hinhThucThanhToan": "Tiền mặt",
        "maTaiKhoan" : current_user.maTaiKhoan,
        "maPSC": maPSC,
    }

    #Lấy lại toàn bộ thông tin để hiển thị
    psc = PhieuSuaChua.query.filter_by(maPSC=maPSC).first()
    ptn = PhieuTiepNhan.query.filter_by(maPTN=psc.maPTN).first()
    kh = KhachHang.query.filter_by(id=ptn.maKhachHang).first()

    ds_hangmuc = dao.getThongTinChiTietHangMuc(maPSC)
    ds_linhkien = dao.getThongTinChiTietLinhKien(maPSC)

    maHoaDon= dao.TaoVaLuuHoaDon(hd)
    thongbao= "Đã tạo hóa đơn thành công !!!"

    return render_template("taohoadon/xulythanhtoan.html",thongbao=thongbao, maHoaDon=maHoaDon,maPSC=maPSC,
                           ngayThanhToan=ngayThanhToan, kh=kh, ds_hangmuc=ds_hangmuc,ds_linhkien=ds_linhkien,
                           tongHoaDon=tongHoaDon, giaTriThue=giaTriThue)


@app.route('/lichlamviec', methods=['GET', 'POST'])
def lichlamviec():
    ds_phancong=dao.getPhanCongCaLam()

    #Lấy ngày bắt đầu và kết thúc tuần
    ngay_hien_tai = date.today()
    ngay_bat_dau = ngay_hien_tai - timedelta(days=ngay_hien_tai.weekday())
    ngay_ket_thuc = ngay_bat_dau + timedelta(days=6)

    ngayBD_Tuan = ngay_bat_dau.strftime("%d/%m/%Y")
    ngayKT_Tuan = ngay_ket_thuc.strftime("%d/%m/%Y")

    khung_gio=[
         "08:00 - 11:45",
        "11:45 - 15:30",
        "15:30 - 19:00",
        "19:00 - 22:00"
    ]
    ca=defaultdict(dict)

    for pc in ds_phancong:
        gioBD=pc.calam.gioBatDau.strftime("%H:%M")
        gioKT = pc.calam.gioKetThuc.strftime("%H:%M")
        thoi_gian=f"{gioBD} - {gioKT}"
        ca[thoi_gian][pc.calam.thu]=True

    return render_template("user/lichlamviec.html", ca=ca, khung_gio=khung_gio,
                           ngayBD_Tuan=ngayBD_Tuan, ngayKT_Tuan=ngayKT_Tuan)

#thu ngan được phép yêu cầu hoàn tiền ở trang này
@app.route("/danhsachhoadon",endpoint="danhsachhoadon", methods=['GET', 'POST'])
def yeucauhoantien():
    thanhcong = request.args.get("thanhcong")
    thatbai = request.args.get("thatbai")

    loaihoadon=request.args.get("loaihoadon" , "all")
    page = request.args.get('page', 1, type=int)
    tu_khoa = request.args.get("tukhoa", " ").strip()
    kieutim=request.args.get("kieutim", " ").strip()

    timkiem=bool(tu_khoa)

    if timkiem:
        ds_goc = dao.timKiemHoaDon(tu_khoa, kieutim)
    else:
        ds_goc = dao.getDanhSachHoaDon()

    tongTatCa = len(ds_goc)
    tongDathanhtoan = len([hd for hd in ds_goc if hd.trangThai == "Đã thanh toán"])
    tongDahoantien = len([hd for hd in ds_goc if hd.trangThai.__eq__(YeuCauStatus.DA_CHAP_NHAN.name)])
    tongDaTuChoi=len([hd for hd in ds_goc if hd.trangThai.__eq__(YeuCauStatus.DA_TU_CHOI.name)])
    tongDaYeuCau=len([hd for hd in ds_goc if hd.trangThai.__eq__(YeuCauStatus.CHUA_XU_LY.name)])

    if loaihoadon == "paid":
        ds = [hd for hd in ds_goc if hd.trangThai == "Đã thanh toán"]
    elif loaihoadon == "refund":
        ds = [hd for hd in ds_goc if hd.trangThai.__eq__(YeuCauStatus.DA_CHAP_NHAN.name)]
    elif loaihoadon == "rejected":
        ds = [hd for hd in ds_goc if hd.trangThai.__eq__(YeuCauStatus.DA_TU_CHOI.name)]
    elif loaihoadon == "requested":
        ds = [hd for hd in ds_goc if hd.trangThai.__eq__(YeuCauStatus.CHUA_XU_LY.name)]
    else:
        ds = ds_goc

    soHoaDon_1Trang = 3
    tongSL=len(ds)
    pages= math.ceil(tongSL/soHoaDon_1Trang)
    batdau = (page - 1) * soHoaDon_1Trang
    ketthuc = batdau + soHoaDon_1Trang
    dsHD_page=ds[batdau:ketthuc]

    return render_template("taohoadon/danhsachhoadon.html",
                           tongTatCa=tongTatCa, tongDathanhtoan=tongDathanhtoan, tongDahoantien=tongDahoantien,tongDaTuChoi=tongDaTuChoi,tongDaYeuCau=tongDaYeuCau,
                           dsHD_page=dsHD_page, pages=pages, page=page,thanhcong=thanhcong, thatbai=thatbai,
                           loaihoadon=loaihoadon, tukhoa=tu_khoa, kieutim=kieutim, timkiem=timkiem)

@app.route("/danhsachhoadon/hoantien", methods=['GET', 'POST'])
def hoantien():
    #Lấy thông tin hóa đơn để đẩy lên cho trang nhập thông tin yêu cầu
    if request.method == "GET":
        maHoaDon = request.args.get("maHoaDon")
        hd=HoaDon.query.filter(HoaDon.maHoaDon==maHoaDon).first()
        psc = PhieuSuaChua.query.filter_by(maPSC=hd.maPSC).first()
        ptn = PhieuTiepNhan.query.filter_by(maPTN=psc.maPTN).first()
        kh = KhachHang.query.filter_by(id=ptn.maKhachHang).first()
        ds_hangmuc = dao.getThongTinChiTietHangMuc(hd.maPSC)
        ds_linhkien = dao.getThongTinChiTietLinhKien(hd.maPSC)

        #Tính ngược lại thuế hiện hành của hóa đơn đó
        tong_hangmuc = sum(hm["chiPhiHienHanh"] for hm in ds_hangmuc)
        tong_linhkien = sum(lk["donGiaHienHanh"]* lk["soLuong"] for lk in ds_linhkien)
        tongTruocThue=tong_hangmuc+tong_linhkien
        thue=hd.tongTien-tongTruocThue
        tyLeThue = None
        if tongTruocThue>0:
            tyLeThue=round((thue/tongTruocThue)*100,2)

        return render_template("taohoadon/hoantien.html", hd=hd, kh=kh, ds_hangmuc=ds_hangmuc, ds_linhkien=ds_linhkien,
                               tyLeThue=tyLeThue  )

    #Lưu thông tin yêu cầu, post
    maHoaDon=request.form.get("maHoaDon")
    noidung=request.form.get("noidung")
    ghichu=request.form.get("ghichu")
    hd = HoaDon.query.filter_by(maHoaDon=maHoaDon).first()

    yc=dao.LuuYeuCau(noidung,ghichu, maHoaDon)

    if yc:
        return redirect(url_for("danhsachhoadon", thanhcong=1))
    else:
        return redirect(url_for("danhsachhoadon", thatbai=1))
if __name__ == "__main__":
    app.run(debug=True)
