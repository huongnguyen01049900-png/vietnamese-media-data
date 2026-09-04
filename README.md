# Vietnamese Media Data Portal

Cổng dữ liệu tĩnh dùng cho **GitHub Pages**, đọc trực tiếp dữ liệu từ workbook Excel.

## Dữ liệu mặc định

- File: `data/database.xlsx`
- Các sheet được hiển thị:
  - `Source Detail 56`
  - `Creator Detail 88`
  - `Added Magazines`
  - `Coverage Gaps`
  - `Taxonomy`

Trang tự đọc workbook bằng SheetJS và dựng:

- KPI tổng quan
- biểu đồ theo quốc gia/thị trường, trạng thái và nhóm dữ liệu
- bảng tìm kiếm/lọc/sắp xếp
- drawer chi tiết toàn bộ trường dữ liệu
- link nguồn chính thức/nguồn kiểm chứng
- xuất CSV từ dữ liệu đã lọc
- mở thử một file Excel khác ngay trong trình duyệt (không upload lên server)

## Cập nhật dữ liệu

Chỉ cần **thay file `data/database.xlsx` bằng workbook mới cùng cấu trúc sheet** rồi commit lên GitHub. Trang có cache-buster nên lần tải sau sẽ đọc file mới.

Nếu đổi tên sheet hoặc tên cột, sửa mapping ở đầu file `assets/app.js` trong biến `DATASETS`.

## Bật GitHub Pages

1. Tạo repository mới, ví dụ: `vietnamese-media-data`.
2. Upload toàn bộ nội dung thư mục này vào **root** của repository.
3. Vào **Settings → Pages**.
4. Ở **Build and deployment**, chọn **Deploy from a branch**.
5. Chọn branch `main`, folder `/ (root)`, rồi Save.
6. Sau khi GitHub build xong, site thường có dạng:
   `https://<username>.github.io/vietnamese-media-data/`

## Cấu trúc repo

```text
.
├── index.html
├── .nojekyll
├── README.md
├── assets/
│   ├── app.js
│   └── styles.css
└── data/
    └── database.xlsx
```

## Lưu ý nghiên cứu

- `UNKNOWN` nghĩa là chưa xác minh được trong vòng nghiên cứu, không có nghĩa là thông tin không tồn tại.
- Creator/blog/NGO không mặc định tương đương newsroom.
- Các số subscriber/follower/view cần đọc cùng ngày đo.
- Khi dùng dữ liệu học thuật hoặc công bố công khai, nên mở URL nguồn trong drawer chi tiết để kiểm tra lại trường quan trọng.

## Thư viện trình duyệt

Trang hiện dùng CDN được pin phiên bản:

- SheetJS `xlsx@0.18.5`
- Chart.js `4.4.7`

Không có backend và không cần database server.
