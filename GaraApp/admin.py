import math

from flask import redirect, request, session, flash
from flask_admin import Admin, AdminIndexView, expose, BaseView
from flask_admin._types import T_ORM_MODEL
from flask_admin.contrib.sqla import ModelView
from flask_admin.theme import Bootstrap4Theme
from flask_login import current_user, logout_user, login_user
from markupsafe import Markup
from datetime import date, datetime

from unidecode import unidecode
from wtforms import Form, ValidationError, SelectField, TextAreaField
from wtforms.widgets import TextArea

from GaraApp import app, db, dao
from .models import HangMuc, LinhKien, QuyDinh, UserRole, TaiKhoan, PhanCongCaLam, CaLam, NhanVien, YeuCauStatus


class AuthenticatedView(ModelView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.vaiTro==UserRole.QUANLY

class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)

class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()

class LinhKienAdmin(AuthenticatedView):
    column_labels = {
        'tenLinhKien': 'Tên linh kiện',
        'donGia': 'Đơn giá',
        'soLuongTon': 'Số lượng tồn',
        'anhLinhKien': 'Ảnh linh kiện'
    }
    column_list = ['anhLinhKien', 'tenLinhKien', 'donGia', 'soLuongTon']
    column_searchable_list = ['tenLinhKien']
    column_filters = ['donGia', 'soLuongTon']
    column_sortable_list = ('donGia', 'soLuongTon')
    column_default_sort = ('soLuongTon')

    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']
    form_overrides = {
        'anhLinhKien': CKTextAreaField
    }

    def image_thumnail(view, context, model, name):
        if model.anhLinhKien:
            return Markup(
                f'<img src="{model.anhLinhKien}" style="height:80px;border-radius:8px;">'
            )
        return ''

    column_formatters = {
        'anhLinhKien': image_thumnail
    }

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        if request.method == 'GET':
            lk_id = request.args.get('id')
            lk = dao.get_chi_tiet_linhkien(lk_id)

            session['linhkien_cu'] = {
                'maLinhKien': lk.maLinhKien,
                'tenLinhKien': lk.tenLinhKien,
                'donGia': lk.donGia,
                'anhLinhKien': lk.anhLinhKien
            }
        return super().edit_view()

    def on_model_change(self, form: Form, model: T_ORM_MODEL, is_created: bool) -> None:
        linhkien_cu = session.get('linhkien_cu')
        if not is_created:
            return dao.update_linhkien(linhkien_cu, form.data)

class HangMucAdmin(AuthenticatedView):
    column_labels = {
        'tenHangMuc': 'Tên hạng mục',
        'chiPhi': 'Chi phí'
    }
    column_list = ['tenHangMuc', 'chiPhi']
    column_searchable_list = ['tenHangMuc']
    column_filters = ['chiPhi']
    column_sortable_list = ['chiPhi']

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        if request.method == 'GET':
            hm_id = request.args.get('id')
            hm = dao.get_chi_tiet_hangmuc(hm_id)

            session['hangmuc_cu'] = {
                'maHangMuc': hm.maHangMuc,
                'tenHangMuc': hm.tenHangMuc,
                'chiPhi': hm.chiPhi,
            }
        return super().edit_view()
    def on_model_change(self, form: Form, model: T_ORM_MODEL, is_created: bool) -> None:
        hangmuc_cu = session.get('hangmuc_cu')
        if not is_created:
            return dao.update_hangmuc(hangmuc_cu, form.data)

class QuyDinhAdmin(AuthenticatedView):
    column_labels = {
        'tenQuyDinh': 'Tên quy định',
        'giaTri': 'Giá trị',
        'donVi': 'Đơn vị',
        'ngayTao': 'Ngày tạo',
        'ngayChinhSua': 'Ngày chỉnh sửa'
    }
    column_list = ['tenQuyDinh', 'giaTri', 'donVi', 'ngayTao']

    form_columns = ['tenQuyDinh', 'giaTri', 'donVi']
    form_widget_args = {
        'tenQuyDinh': {'readonly': True},
        'donVi': {'readonly': True},
    }

    can_create = False
    can_delete = False

    @expose('/edit/', methods=('GET', 'POST'))
    def edit_view(self):
        if request.method == 'GET':
            qd_id = request.args.get('id')
            qd = dao.get_chi_tiet_quydinh(qd_id)

            session['quydinh_cu'] = {
                'maQuyDinh': qd.maQuyDinh,
                'giaTri': qd.giaTri,
            }
        return super().edit_view()

    def on_model_change(self, form: Form, model: T_ORM_MODEL, is_created: bool) -> None:
        quydinh_cu = session.get('quydinh_cu')
        if not is_created:
            return dao.update_quydinh(quydinh_cu, form.data)


class CaLamAdmin(AuthenticatedView):
    column_labels = {
        'tenCa': 'Tên ca',
        'thu': 'Thứ',
        'gioBatDau': 'Giờ bắt đầu',
        'gioKetThuc': 'Giờ kết thúc'
    }
    column_list = ['tenCa', 'thu', 'gioBatDau', 'gioKetThuc']
    column_filters = ['thu', 'tenCa']
    column_sortable_list = ('thu', 'gioBatDau')
    column_default_sort = ('thu')
    form_columns = ['tenCa', 'thu', 'gioBatDau', 'gioKetThuc']


class PhanCongCaLamAdmin(AuthenticatedView):
    column_labels = {
        'taikhoan': 'Nhân viên',
        'calam': 'Ca làm',
        'ngayApDung': 'Ngày áp dụng',
        'ghiChu': 'Ghi chú'
    }
    column_list = ('taikhoan', 'calam', 'ngayApDung', 'ghiChu')
    form_columns = ('taikhoan', 'calam', 'ngayApDung', 'ghiChu')

    can_create = False

class PhanCongView(BaseView):
    @expose('/')
    def index(self):
        if request.method.__eq__("GET"):
            q = request.args.get('q')
            role = request.args.get('role')
            thu = request.args.get('thu')

        page = request.args.get("page", default=1, type=int)
        pages = math.ceil(dao.count_ds_taikhoan() / app.config["PAGE_SIZE"])
        taiKhoans = dao.get_ds_taikhoan(q, role, page=page)
        calams = dao.get_ds_calam(thu)

        return self.render('admin/phanCongCaLamCreate.html',
            taiKhoans=taiKhoans, calams=calams, role = UserRole, now = date.today(), page=page, pages=pages)

    def is_accessible(self):
        return current_user.is_authenticated and current_user.vaiTro == UserRole.QUANLY

class YeuCauView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self) -> str:
        status = request.args.get('status')
        loai = request.args.get('loai')

        count_tatca = dao.count_yeucau(loai=loai, status=None)
        count_chua_xuly = dao.count_yeucau(loai, YeuCauStatus.CHUA_XU_LY)
        count_da_xuly = dao.count_yeucau(loai, YeuCauStatus.DA_CHAP_NHAN)
        count_da_tuchoi = dao.count_yeucau(loai, YeuCauStatus.DA_TU_CHOI)

        page = request.args.get("page", default=1, type=int)
        pages = math.ceil(dao.count_yeucau(loai, status) / app.config["PAGE_SIZE"])
        yeucaus = dao.get_ds_yeucau(page=page, loai=loai, status=status)

        if request.method == 'POST':
            action = request.form.get('action')
            yc_id = request.form.get('yc_id')
            if action:
                dao.xuly_yeucau(action, yc_id)
                flash("Xử lý yêu cầu thành công", "success")
                return redirect(request.url)
        return self.render("/admin/xuLyYeuCau.html",yeucaus=yeucaus, YeuCauStatus= YeuCauStatus,
                           count_tatca = count_tatca, count_chua_xuly = count_chua_xuly, count_da_xuly= count_da_xuly,
                           count_da_tuchoi=count_da_tuchoi, pages=pages, page=page)

    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.vaiTro == UserRole.QUANLY

class MyLogoutView(BaseView):
    @expose('/')
    def index(self) -> str:
        logout_user()
        return redirect("/admin")

    def is_accessible(self) -> bool:
        return current_user.is_authenticated

class MyLoginView(BaseView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        err_msg = None

        if request.method == 'POST':
            tenNguoiDung = request.form.get('tenNguoiDung')
            matKhau = request.form.get('matKhau')

            tk = dao.auth_user(tenNguoiDung, matKhau)
            if tk:
                login_user(tk)
                return redirect('/admin')

            err_msg = "Tên người dùng hoặc mật khẩu không đúng"

        return self.render('admin/login.html', err_msg=err_msg)

    def is_accessible(self) -> bool:
        return not current_user.is_authenticated

class QuanLyTaiKhoanAdmin(AuthenticatedView):
    column_labels = {
        'maTaiKhoan': 'Mã tài khoản',
        'tenNguoiDung': 'Tên người dùng',
        'vaiTro': 'Vai trò',
        'maNhanVien': 'Mã nhân viên',
        'ngayTaoTaiKhoan' : 'Ngày tạo tài khoản',
        'nhanvien' : 'Nhân viên',
        'matKhau': 'Mật khẩu'
    }
    column_list = ('maTaiKhoan', 'tenNguoiDung', 'vaiTro', 'maNhanVien', 'ngayTaoTaiKhoan')
    column_searchable_list = ['maNhanVien', 'maTaiKhoan']
    column_filters = ['vaiTro']

    column_sortable_list = ['ngayTaoTaiKhoan']
    column_default_sort = ('ngayTaoTaiKhoan', True)

    # trả về câu lênh sql
    def get_query(self):
        return super().get_query().filter(TaiKhoan.vaiTro != UserRole.QUANLY)
    def get_count_query(self):
        return super().get_count_query().filter(TaiKhoan.vaiTro != UserRole.QUANLY)

    form_columns = ('nhanvien', 'vaiTro')

    form_overrides = {'vaiTro': SelectField}

    form_args = {
        'nhanvien': {
            'query_factory': dao.get_ds_nhanvien
        },
        'vaiTro': {
            'choices':[
                (UserRole.KYTHUATVIEN.name, 'Kỹ thuật viên'),
                (UserRole.THUNGAN.name, 'Thu ngân'),
                (UserRole.NHANVIEN.name, 'Nhân viên')
            ]
        }
    }

    # custom tên nguời dùng trong lúc tạo mặc định sẽ là chữ cái đầu họ + tên lót và tên + namsinh
    def on_model_change(self, form, model, is_created):
        if is_created:
            nv = model.nhanvien
            if nv:
                ho = unidecode(nv.ho.strip().lower())
                ten = unidecode(nv.ten.strip().lower())

                cccd = nv.CCCD[-4:] if nv.CCCD else ""
                chu_cai_dau = ''.join([c[0] for c in ho.split()])

                model.tenNguoiDung = f"{chu_cai_dau}{ten}{cccd}"
                import hashlib
                model.matKhau = hashlib.md5(model.tenNguoiDung.encode('utf-8')).hexdigest()

        return super().on_model_change(form, model, is_created)

class QuanLyNhanVienAdmin(AuthenticatedView):
    column_labels = {
        'id' : "Mã nhân viên",
        'ho': 'Họ',
        'ten': 'Tên',
        'CCCD': 'CCCD',
        'luong': 'Lương',
        'gioiTinh' : 'Giới tính',
        'ngayVaoLam' : 'Ngày bắt đầu làm việc'
    }
    column_list = ('id', 'ho', 'ten', 'gioiTinh', 'ngayVaoLam')
    column_searchable_list = ['id', 'ten']
    column_filters = ['luong', 'ngayVaoLam', 'gioiTinh']

    form_columns = ('ho', 'ten', 'gioiTinh', 'luong', 'CCCD')

    form_overrides = {
        'gioiTinh': SelectField
    }
    form_args = {
        'gioiTinh': {
            'choices': [
                ('Nam', 'Nam'),
                ('Nữ', 'Nữ')
            ]
        }
    }
    def on_model_change(self, form, model, is_created):
        cccd = model.CCCD
        if not cccd.isdigit() or len(cccd) != 12:
            raise ValidationError("CCCD phải gồm 12 chữ số")
        luong = model.luong
        if luong < 0:
            raise ValidationError("Số lương không hợp lệ!")


class StatsView(BaseView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.vaiTro==UserRole.QUANLY

class StatsDoanhThuView(StatsView):
    @expose('/')
    def index(self) -> str:
        time = request.args.get('time')
        month_year = request.args.get('month_year')
        month = datetime.strptime(month_year, "%Y-%m").strftime('%m') if month_year else None
        year = (datetime.strptime(month_year, "%Y-%m").strftime('%y') if month_year else None)
        doanhthu_stats = dao.thong_ke_theo_thoigian(time, month=month, year=year)
        print(year, doanhthu_stats)
        return self.render('admin/stats/statsDoanhThu.html', doanhthu_stats = doanhthu_stats)

class StatsTiLeXeView(StatsView):
    @expose('/')
    def index(self) -> str:
        return self.render('admin/stats/statsTiLeXe.html', loaixe_stats = dao.count_xe_by_loaixe())

class StatsBieuDoLoiView(StatsView):
    @expose('/')
    def index(self) -> str:
        return self.render('admin/stats/statsLoi.html', loi_stats = dao.thong_ke_theo_loi())


class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self) -> str:
        return self.render('admin/index.html')


admin = Admin(app=app, name="Hontri GaraApp", theme=Bootstrap4Theme(),  index_view=MyAdminIndexView())
admin.add_view(HangMucAdmin(HangMuc, db.session,name="Quản lý hạng mục",category="Quản lý kho"))
admin.add_view(LinhKienAdmin(LinhKien, db.session,name="Quản lý linh kiện",category="Quản lý kho"))
admin.add_view(YeuCauView(name="Xử lý yêu cầu",category="Quản lý kho"))

admin.add_view(QuyDinhAdmin(QuyDinh, db.session,name="Quản lý quy định"))

admin.add_view(QuanLyTaiKhoanAdmin(TaiKhoan,db.session, name="Quản lý tài khoản",category="Quản lý nhân sự"))
admin.add_view(QuanLyNhanVienAdmin(NhanVien,db.session, name="Quản lý nhân viên",category="Quản lý nhân sự"))

admin.add_view(CaLamAdmin(CaLam,db.session,name="Quản lý ca làm",category="Quản lý ca làm"))
admin.add_view(PhanCongCaLamAdmin(PhanCongCaLam,db.session, name="Danh sách ca làm",category="Quản lý ca làm"))
admin.add_view(PhanCongView(name="Phân công ca làm",category="Quản lý ca làm"))

admin.add_view(StatsDoanhThuView(name="Thống kê doanh thu",category="Thống kê - Báo cáo"))
admin.add_view(StatsTiLeXeView(name="Thống kê tỉ lệ xe",category="Thống kê - Báo cáo"))
admin.add_view(StatsBieuDoLoiView(name="Thống kê lỗi",category="Thống kê - Báo cáo"))

admin.add_view(MyLogoutView(name="Đăng xuất"))
admin.add_view(MyLoginView(name="Đăng nhập"))
