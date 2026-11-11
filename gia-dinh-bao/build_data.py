"""Sinh data.js cho trang gia-dinh-bao/index.html từ workbook Excel.

Cách dùng:  python3 gia-dinh-bao/build_data.py <đường-dẫn-file.xlsx>
Mặc định đọc gia-dinh-bao/GDB_1865-1871.xlsx. Cần: pip install openpyxl

Trang HTML cũng đọc trực tiếp được file Excel qua nút "Mở file Excel";
script này chỉ để dữ liệu mặc định có sẵn khi mở trang (kể cả offline).
"""
import json
import sys
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent

# Tên cột trong sheet đơn vị văn bản -> khóa ngắn dùng trong trang (giống UNIT_COLS trong index.html)
UNIT_COLS = {
    "DATE": "d", "N0": "n", "Thời kỳ": "p", "Mục (chuẩn hóa)": "m",
    "Tên bài (nếu có)": "t", "Tên đặt tạm thời": "tt",
    "Hình thức chính": "hf", "Hình thức phụ": "hf2",
    "Nội dung chính": "cd", "Nội dung phụ": "cd2", "Từ khoá": "kw",
    "Tóm tắt nội dung": "sum", "Ghi chú phân loại": "note", "OCR": "ocr",
    "Năm (phụ)": "y", "Khóa ngày (yyyymmdd)": "k",
}
ISSUE_COLS = {
    "Danh sách số báo": "id", "Ngày phát hành": "d", "Năm phát hành": "y",
    "Số báo": "n", "Tình trạng lưu trữ": "st",
    "Chánh tổng tài / người phụ trách": "ed", "nơi bảo tồn": "loc",
}


def read_sheet(ws, cols, header_hint):
    rows = list(ws.iter_rows(values_only=True))
    hi = next(i for i, r in enumerate(rows) if header_hint in [str(c).strip() if c else "" for c in r])
    header = [str(c).strip() if c else "" for c in rows[hi]]
    out = []
    for r in rows[hi + 1:]:
        rec = {}
        for name, key in cols.items():
            if name in header:
                v = r[header.index(name)]
                if v is not None and str(v).strip() != "":
                    rec[key] = v if isinstance(v, (int, float)) else str(v).strip()
        out.append(rec)
    return out


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "GDB_1865-1871.xlsx"
    wb = openpyxl.load_workbook(src, data_only=True)
    units = [u for u in read_sheet(wb["GDB 1866-1871"], UNIT_COLS, "Hình thức chính") if u.get("d")]
    issues = [i for i in read_sheet(wb["danh sách báo 1865-1871"], ISSUE_COLS, "Tình trạng lưu trữ") if i.get("id")]
    payload = {"source": src.name, "units": units, "issues": issues}
    js = "window.GDB_DATA = " + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n"
    (HERE / "data.js").write_text(js, encoding="utf-8")
    print(f"data.js: {len(units)} đơn vị, {len(issues)} số báo")


if __name__ == "__main__":
    main()
