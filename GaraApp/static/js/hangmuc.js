function renderSelectedHangMuc(selected_hangmuc) {
    const bar = document.getElementById("dsHangMucDaChon");
    bar.innerHTML = "";

    Object.values(selected_hangmuc).forEach(obj => {
        const html = `
        <div class="d-flex justify-content-between mb-2">
            <p>Hạng mục: ${obj.tenHangMuc}</p>
            <button class="btn" onclick="deleteHangMuc( ${obj.maHangMuc})"
              style="background:#BF0603;color:#fff;width:100px">XOÁ</button>
        </div>
        <p>Mã hạng mục: ${obj.maHangMuc}</p>
        <p>Chi phí: ${Number(obj.chiPhi).toLocaleString()} VNĐ</p>
        <hr>
        `;
        bar.innerHTML += html;
    });
}

// Thêm hạng mục
function chonLinhKien(maHangMuc, tenHangMuc, chiPhi) {
    fetch("/api/hangmuc", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            maHangMuc,
            tenHangMuc,
            chiPhi
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.selected_hangmuc) {
            renderSelectedHangMuc(data.selected_hangmuc)
        }
        location.reload();
    })
}

function deleteHangMuc(maHangMuc) {
    if (!confirm("Bạn có chắc chắn xoá hạng mục này?")) return
    fetch(`/api/hangmuc/${maHangMuc}`, { method: "DELETE" })
        .then(res => res.json())
        .then(data => {
            if (data.selected_hangmuc) {
                renderSelectedHangMuc(data.selected_hangmuc)
            }
            location.reload();
        })
}