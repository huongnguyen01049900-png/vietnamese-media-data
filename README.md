# Vietnamese Media Data Portal

Cổng dữ liệu nghiên cứu **truyền thông tiếng Việt toàn cầu**, sẵn sàng chạy trên GitHub Pages.

## Dữ liệu hiện có

Portal đang trình bày 5 nhóm dữ liệu được sinh từ workbook nghiên cứu ngày **2026-09-05**:

- `Source Detail 56` — 56 nguồn báo/đài/truyền thông
- `Creator Detail 88` — 88 creator, blog và kênh cá nhân
- `Added Magazines` — 11 tạp chí/ấn phẩm bổ sung
- `Coverage Gaps` — các quốc gia/khu vực còn khoảng trống nghiên cứu
- `Taxonomy` — hệ thống phân loại nguồn

Do GitHub connector không nhận upload file Excel nhị phân trực tiếp, dữ liệu mặc định được lưu dưới dạng các snapshot nén trong `data/*.json.gz.b64`. File `assets/data-shim.js` dựng lại workbook `.xlsx` ngay trong trình duyệt, nên:

- giao diện vẫn đọc dữ liệu như workbook;
- nút **Tải Excel** tạo file Excel tải xuống tại chỗ;
- nút **Mở Excel khác** vẫn cho phép chọn một workbook `.xlsx/.xls` từ máy để xem thử mà không upload lên server.

## Tính năng

- KPI tổng quan
- biểu đồ theo quốc gia/thị trường, trạng thái và nhóm dữ liệu
- tìm kiếm toàn văn
- lọc theo quốc gia, trạng thái, loại/nền tảng
- sắp xếp cột
- xem toàn bộ metadata của từng bản ghi
- link nguồn chính thức và nguồn kiểm chứng
- xuất CSV từ dữ liệu đã lọc
- responsive cho desktop/mobile

## Cấu trúc repo

```text
.
├── index.html
├── .nojekyll
├── README.md
├── .github/
│   └── workflows/
│       └── pages.yml
├── assets/
│   ├── app.js
│   ├── data-shim.js
│   └── styles.css
└── data/
    ├── README.md
    ├── source-detail.json.gz.b64
    ├── creator-detail.json.gz.b64
    ├── added-magazines.json.gz.b64
    ├── coverage-gaps.json.gz.b64
    └── taxonomy.json.gz.b64
```

## Bật GitHub Pages lần đầu

GitHub App có quyền push code nhưng **không có quyền tạo Pages site**. Chủ repository cần bật Pages một lần:

1. Vào **Settings → Pages**.
2. Ở **Build and deployment → Source**, chọn **GitHub Actions**.
3. Sau đó chạy lại workflow **Deploy GitHub Pages** hoặc tạo một commit mới.

Workflow `.github/workflows/pages.yml` đã được cấu hình sẵn; các lần cập nhật sau sẽ tự deploy khi `main` thay đổi.

URL dự kiến sau khi Pages được bật:

`https://huongnguyen01049900-png.github.io/vietnamese-media-data/`

## Lưu ý nghiên cứu

- `UNKNOWN` nghĩa là chưa xác minh được trong vòng nghiên cứu, không có nghĩa là thông tin không tồn tại.
- Creator/blog/NGO không mặc định tương đương newsroom.
- Subscriber/follower/view phải được đọc cùng ngày đo.
- Với trường quan trọng, mở URL nguồn trong phần chi tiết để kiểm chứng lại trước khi trích dẫn/công bố.

## Thư viện trình duyệt

- SheetJS `xlsx@0.18.5`
- Chart.js `4.4.7`

Portal không có backend và không cần database server.
