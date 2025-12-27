from models import *
if __name__ == "__main__":
    with app.app_context():
        with open("data/diachi.json", encoding="utf-8") as f:
            dc_list = json.load(f)
            for dc in dc_list:
                dc_obj = DiaChi(**dc)
                db.session.add(dc_obj)
        db.session.commit()

        with open("data/nhanvien.json", encoding="utf-8") as f:
            nv_list = json.load(f)
            for nv in nv_list:
                nv_obj = NhanVien(**nv)
                db.session.add(nv_obj)
        db.session.commit()

        with open("data/taikhoan.json", encoding="utf-8") as f:
            tk_list = json.load(f)
            for tk in tk_list:
                import hashlib
                tk["matKhau"] = hashlib.md5(tk["matKhau"].strip().encode('utf-8')).hexdigest()
                tk["vaiTro"] = UserRole(tk["vaiTro"])
                tk_obj = TaiKhoan(**tk)
                db.session.add(tk_obj)
        db.session.commit()

        with open("data/calam.json", encoding="utf-8") as f:
            cl_list = json.load(f)
            for cl in cl_list:
                cl_obj = CaLam(**cl)
                db.session.add(cl_obj)
        db.session.commit()

        with open("data/khachhang.json", encoding="utf-8") as f:
            kh_list = json.load(f)
            for kh in kh_list:
                kh_obj = KhachHang(**kh)
                db.session.add(kh_obj)
        db.session.commit()

        with open("data/loaixe.json", encoding="utf-8") as f:
            loaixe_list = json.load(f)
            for loaixe in loaixe_list:
                loaixe_obj = LoaiXe(**loaixe)
                db.session.add(loaixe_obj)
        db.session.commit()

        with open("data/xe.json", encoding="utf-8") as f:
            xe_list = json.load(f)
            for xe in xe_list:
                xe_obj = Xe(**xe)
                db.session.add(xe_obj)
        db.session.commit()

        with open("data/phieuTN.json", encoding="utf-8") as f:
            ptn_list = json.load(f)
            for ptn in ptn_list:
                ptn_obj = PhieuTiepNhan(**ptn)
                db.session.add(ptn_obj)
        db.session.commit()

        with open("data/hangmuc.json", encoding="utf-8") as f:
            hm_list = json.load(f)
            for hm in hm_list:
                hm_obj = HangMuc(**hm)
                db.session.add(hm_obj)
        db.session.commit()

        with open("data/linhkien.json", encoding="utf-8") as f:
            lk_list = json.load(f)
            for lk in lk_list:
                lk_obj = LinhKien(**lk)
                db.session.add(lk_obj)
        db.session.commit()

        with open("data/phieuSC.json", encoding="utf-8") as f:
            psc_list = json.load(f)
            for psc in psc_list:
                psc_obj = PhieuSuaChua(**psc)
                db.session.add(psc_obj)
        db.session.commit()

        # with open("data/chitiethangmuc.json", encoding="utf-8") as f:
        #     cthm_list = json.load(f)
        #     for cthm in cthm_list:
        #         cthm_obj = ChiTietHangMucSuaChua(**cthm)
        #         db.session.add(cthm_obj)
        # db.session.commit()
        #
        # # 12. Load Chi tiết linh kiện sửa chữa
        # print("Loading ChiTietLinhKienSuaChua...")
        # with open("data/chitietlinhkien.json", encoding="utf-8") as f:
        #     ctlk_list = json.load(f)
        #     for ctlk in ctlk_list:
        #         ctlk_obj = ChiTietLinhKienSuaChua(**ctlk)
        #         db.session.add(ctlk_obj)
        # db.session.commit()

        with open("data/quydinh.json", encoding="utf-8") as f:
            qd_list = json.load(f)
            for qd in qd_list:
                qd_obj = QuyDinh(**qd)
                db.session.add(qd_obj)
        db.session.commit()

        with open("data/hoadon.json", encoding="utf-8") as f:
            hd_list = json.load(f)
            for hd in hd_list:
                hd_obj = HoaDon(**hd)
                db.session.add(hd_obj)
        db.session.commit()

        # with open("data/yeucau.json", encoding="utf-8") as f:
        #     yc_list = json.load(f)
        #     for yc in yc_list:
        #         yc["trangThai"] = YeuCauStatus[yc["trangThai"]]
        #         yc_obj = YeuCau(**yc)
        #         db.session.add(yc_obj)
        # db.session.commit()

        print("Đã load xong tất cả dữ liệu")