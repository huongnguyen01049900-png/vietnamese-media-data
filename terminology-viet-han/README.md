# Nghiên cứu thuật ngữ chính trị và ngoại giao Việt–Hàn

**Bản bàn giao ngày 29/10/2026 (giờ Hàn Quốc).** Bộ dữ liệu gồm 266 dòng: 167 mục ban đầu và 99 mục bổ sung. Mỗi mã được giữ riêng; tổng số dòng không phải số khái niệm độc nhất.

## Mở kết quả

- [File Excel đầy đủ](Ra_soat_266_muc_thuat_ngu_Viet_Han.xlsx)
- [Trang chỉnh sửa trực tuyến](https://thuat-ngu-viet-han-nghien-cuu.h160824h.chatgpt.site/)
- [Mã nguồn và dữ liệu của trang](editor-source.zip)
- [Thống kê dạng JSON](research-summary.json)

Trang chỉnh sửa là trang riêng tư, yêu cầu đăng nhập bằng tài khoản ChatGPT được cấp quyền. Có tìm kiếm Việt/Hàn/Anh/mã, lọc, sửa từng mục, lưu trực tuyến, khôi phục và xuất CSV/JSON. Thay đổi trên trang được lưu theo tài khoản. File Excel và bộ kết quả trên GitHub là bản tại thời điểm bàn giao, không tự cập nhật sau mỗi lần sửa trên trang.

## Nội dung Excel

1. **Thuật ngữ**: số thứ tự, mã, dạng Việt/Hàn, ý nghĩa, nhóm và trạng thái.
2. **Rà soát**: định nghĩa, tư cách thuật ngữ, phạm vi tương ứng và các điểm cần kiểm tra.
3. **Khung và cách đọc**: năm nhóm, định nghĩa, tiểu loại, quy tắc áp dụng và cách đọc chứng cứ.
4. **Nguồn kiểm tra**: 1.185 dòng bằng chứng, gồm 315 nguồn bổ sung cho nguồn gốc từ.
5. **Đối chiếu Anh**: kiểm tra hai nhánh Việt–Anh và Hàn–Anh cùng nghĩa được chọn.
6. **Nguồn gốc từ**: cấu tạo Việt/Hàn, tách thành tố, chữ Hán/Hanja, HVDic và mức A/B/C.

## Chứng cứ nguồn gốc từ

| Mức | Việt | Hàn | Cách hiểu |
| --- | ---: | ---: | --- |
| A | 161 | 64 | Nguồn hỗ trợ các thành tố quyết định nhãn cấu tạo. |
| B | 78 | 202 | Có phân tích nhưng chưa đủ chứng cứ cho từng thành tố hoặc nghĩa mở rộng. |
| C | 27 | 0 | Còn điểm từ nguyên hoặc nghĩa chưa thể chốt. |
| Tổng | 266 | 266 | Các dòng giữ theo mã đầu vào. |

Có **48 dòng A/A**; 15 dòng trong số đó đồng thời đã xác nhận cùng biểu thức Anh trong nghĩa được chọn. Chữ Hán/Hanja có dấu `*` là dạng đối chiếu đề xuất chưa được xác minh đầy đủ.

### Nguồn Hán Nôm

Dùng [Từ điển Hán Nôm Thi Viện](https://hvdic.thivien.net/) theo yêu cầu nghiên cứu. Ghi tên người biên soạn ở những mục đã đọc có thông tin nguồn:

- 12 dòng có chứng cứ mục từ cho cả dạng biểu thức.
- 241 dòng có chứng cứ cho thành tố.
- 13 dòng chưa có chứng cứ HVDic cụ thể trong lượt tra này.

**Chưa có chứng cứ trong lượt tra không có nghĩa từ điển không có mục từ.** Có chữ Hán để ghi âm hoặc có mục từ cùng dạng cũng không tự xác nhận nguồn gốc, nghĩa chuyên ngành hay tương ứng Việt–Hàn. Nhãn cấu tạo toàn biểu thức là kết quả phân tích có dẫn nguồn, không tự chứng minh cả thuật ngữ được vay nguyên khối.

## Khung nội dung

N1 Cá nhân / 인물; N2 Cơ quan, tổ chức / 기관·조직; N3 Thể chế, tư tưởng / 제도·이념; N4 Quan hệ, hoạt động / 관계·활동; N5 Văn bản / 문서.

Mỗi bản ghi chỉ nhận một nhóm chính theo nghĩa đã chọn. Trạng thái **Cần xem xét** được giữ riêng khi chưa khóa nghĩa hoặc khung chưa bao phủ; đây không phải nhóm nội dung thứ sáu. Khung không ép toàn bộ thuật ngữ chính trị–ngoại giao vào năm nhóm khi chưa đủ căn cứ.

## Kiểm tra bàn giao

Excel đã kiểm tra 266 mã, thống kê, công thức, bộ lọc và bảo toàn 22.424 ô cũ. Mã trang đã vượt qua kiểm tra TypeScript, build và kiểm tra lưu/khôi phục, cách ly tài khoản, chống ghi đè phiên bản. Triển khai riêng tư đã thành công. Kiểm tra thao tác trên trình duyệt chưa hoàn tất: dịch vụ xem trước không khả dụng và trang đã triển khai có cửa đăng nhập.
