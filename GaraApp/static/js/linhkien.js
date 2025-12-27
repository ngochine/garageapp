let currentLinhKien = null;
function renderSelectedLinhKien(selected_linhkien) {
    const container = document.getElementById("dsLinhKienDaChon")
    if (!container) return
    container.innerHTML = ""

    Object.values(selected_linhkien).forEach(lk => {
        container.innerHTML += `
        <div class="card mb-2" id="LK${lk.maLinhKien}">
            <div class="card-body d-flex justify-content-between p-2">
                <div>
                    <p class="fw-bold mb-1">${lk.tenLinhKien}</p>
                    <p class="mb-0">Mã: ${lk.maLinhKien}</p>
                    <p class="mb-0">Đơn giá: ${lk.donGia} VNĐ</p>
                    <p class="mb-0">Tồn kho: ${lk.soLuongTon}</p>
                </div>
                <div class="d-flex flex-column">
                    <input type="number" class="form-control mb-2 text-center"
                           min="1" max="${lk.soLuongTon}" value="${lk.soLuong}"
                           onblur="updateSoLuongLinhKien(${lk.maLinhKien}, this)">
                    <button class="btn btn-warning" onclick="deleteLinhKien(${lk.maLinhKien})">
                        XOÁ
                    </button>
                </div>
            </div>
        </div>
        `
    })
}

function chonLinhKien(maLinhKien, tenLinhKien, donGia, soLuongTon) {
    currentLinhKien = maLinhKien
    if (soLuongTon > 0) {
        fetch("/api/linhkien", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                maLinhKien,
                tenLinhKien,
                donGia,
                soLuongTon
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.selected_linhkien) {
                renderSelectedLinhKien(data.selected_linhkien)
            }
        })
    }
    else {
        const modal = new bootstrap.Modal(
            document.getElementById("modalBaoThieu")
        )
        modal.show()
    }
}

function deleteLinhKien(maLinhKien) {
    if (!confirm("Bạn có chắc chắn xoá linh kiện này?")) return
    fetch(`/api/linhkien/${maLinhKien}`, { method: "DELETE" })
        .then(res => res.json())
        .then(data => {
            if (data.selected_linhkien) {
                renderSelectedLinhKien(data.selected_linhkien)
            }
        })
}

function updateSoLuongLinhKien(maLinhKien, obj) {
    const soLuong = parseInt(obj.value)
    const soLuongTon = parseInt(obj.getAttribute("max"))
    if (soLuong <= 0 || isNaN(soLuong)) {
        alert("Số lượng không hợp lệ")
        return
    }
    if (soLuong > soLuongTon) {
        currentLinhKien = maLinhKien
        obj.value = soLuongTon
        fetch(`/api/linhkien/${maLinhKien}`, {
            method: "PUT",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "soLuong": soLuongTon
            })
        })
        .then(res => res.json())
        .then(data => {
            renderSelectedLinhKien(data.selected_linhkien)
        })
        const modal = new bootstrap.Modal(
            document.getElementById("modalBaoThieu")
        );
        modal.show()
        return
    }
    fetch(`/api/linhkien/${maLinhKien}`, {
        method: "PUT",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            "soLuong": soLuong
        })
    })
    .then(res => res.json())
    .then(data => {
        renderSelectedLinhKien(data.selected_linhkien)
    });
}

function baothieulinhkien() {
    const ghiChu = document.getElementById("ghiChuBaoThieu").value;
    fetch(`/api/baothieulinhkien/${currentLinhKien}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            loaiYeuCau: "BAO_THIEU_LINH_KIEN",
            ghiChu: ghiChu
        })
    })
    .then(res => res.json())
    .then((data) => {
        if (data.status === 200){
            const btnChon = document.getElementById(`btnChonLK${currentLinhKien}`)
            if (btnChon) {
                btnChon.disabled = true;
                btnChon.innerText = "ĐÃ BÁO THIẾU"
                btnChon.classList.add("btn-secondary")
            }
            const modal = document.getElementById("modalBaoThieu")
            const modall = bootstrap.Modal.getInstance(modal)
            modall.hide();
            alert("Báo thiếu linh kiện thành công");
        } else if(data.status === 400){
            alert("Linh kiện đã được báo thiếu");
        }
        else{
            alert("Có lỗi xảy ra đã được báo thiếu");
        }
    });
}
