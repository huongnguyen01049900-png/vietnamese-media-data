# Nghiên cứu thuật ngữ chính trị và ngoại giao Việt–Hàn

[**Mở trang nghiên cứu có thể chỉnh sửa**](https://thuat-ngu-viet-han-nghien-cuu.h160824h.chatgpt.site/)

[**Tải Excel nghiên cứu**](Ra_soat_266_muc_thuat_ngu_Viet_Han.xlsx) · [**Mã nguồn trang**](editor-source.zip) · [**Thông tin bản dữ liệu**](research-summary.json)

Trang vẫn riêng tư theo tài khoản chủ sở hữu. Kho GitHub lưu bản bàn giao; các sửa đổi của bạn trên trang được lưu trực tuyến riêng và không tự ghi ngược vào Excel hoặc GitHub. CSV/JSON xuất từ trang phản ánh bản đang được trang tải.


Bảng nghiên cứu thuật ngữ chính trị và ngoại giao, gồm 266 dòng Việt–Hàn: bộ 167 và 99 mục bổ sung. Các dòng trùng khái niệm được giữ riêng theo mã đầu vào.

## Sử dụng

Trang được triển khai riêng tư bằng Sites. Người dùng đăng nhập bằng tài khoản ChatGPT, tìm kiếm hoặc lọc, mở một dòng rồi chọn **Lưu thay đổi**. Bản sửa được lưu trực tuyến theo tài khoản; mở lại cùng tài khoản trên thiết bị khác sẽ đọc cùng dữ liệu. Nhãn A/B/C và nguồn của bản nghiên cứu luôn được bảo toàn.

- **Xuất CSV**: các dòng đang lọc, gồm những thay đổi đã lưu.
- **Xuất JSON**: toàn bộ bản đang được trang tải, gồm các chứng cứ.
- **Tải Excel nghiên cứu**: bản Excel bàn giao, không tự cập nhật theo chỉnh sửa trên trang.
- **Khôi phục**: trả một mục về bản nghiên cứu ban đầu; lịch sử được giữ ở máy chủ.
- Xung đột phiên bản được báo để người dùng tải lại bản mới trước khi ghi tiếp.

GitHub lưu bản kết quả tại thời điểm bàn giao. Thay đổi trên trang không tự tạo commit GitHub hoặc ghi lại file Excel.

## Dữ liệu và phương pháp

`data/research.json` ghép dữ liệu định nghĩa, nhóm nội dung, đối chiếu Việt–Anh/Hàn–Anh và phân tích nguồn gốc từ. Dữ liệu này là bản nghiên cứu có mức chứng cứ, không phải danh mục 266 cặp đã được xác nhận hoàn toàn.

| Chứng cứ nguồn gốc | Việt | Hàn |
| --- | ---: | ---: |
| A — có nguồn cho thành tố quyết định | 161 | 64 |
| B — phân tích còn thiếu chứng cứ đầy đủ | 78 | 202 |
| C — còn điểm chưa chốt | 27 | 0 |

Có 48 dòng A/A. Chữ Hán/Hanja có `*` là dạng đối chiếu đề xuất chưa được chứng thực đầy đủ. Từ nguyên, tư cách thuật ngữ, tương đương nghĩa và nhóm nội dung là những kết luận riêng.

Nguồn Hán Việt ưu tiên: [Từ điển Hán Nôm Thi Viện](https://hvdic.thivien.net/). Có 12 dòng ghi chứng cứ mục từ cho cả dạng biểu thức, 241 dòng có chứng cứ thành tố, 13 dòng chưa có chứng cứ HVDic trong lượt này. Chưa có chứng cứ không có nghĩa từ điển không có mục từ. Các URL và phần hỗ trợ của từng nguồn nằm trong mỗi mục.

## Định nghĩa và đối chiếu tiếng Anh — cập nhật 29/10/2026 (KST)

Bản bổ sung ghi đủ 266 hồ sơ theo mã. Chọn **Định nghĩa Việt–Hàn** hoặc **Đối chiếu tiếng Anh** ở phía trên bảng, rồi mở một mục để xem nguồn. Bộ lọc **Nguồn từ điển** giúp xem các mục có nguồn chuyên ngành, có định nghĩa toàn mục hoặc cần kiểm lại nghĩa.

- **Phía Việt:** tách nghĩa làm việc, trích đoạn nguồn, diễn giải, ngôn ngữ nguồn và phạm vi. Có 18 dòng có trích đoạn Việt, 33 diễn giải từ định nghĩa có nguồn, 85 mô tả chính thức, 122 nghĩa làm việc và 8 chưa xác minh. Có 23 dòng dựa trên định nghĩa khái niệm bằng tiếng Việt; đây không phải 23 mục từ điển Việt.
- **Từ điển quốc ngữ:** phân biệt 한국어기초사전 và 표준국어대사전. 193 dòng có nghĩa nguồn/bản dịch nghiên cứu. 37 dòng được đối chiếu qua chỉ mục nguồn chính thức (21 toàn hình thức); 156 dòng hiện dựa trên bản xuất dữ liệu công khai, mang nhãn cần kiểm lại nguồn gốc. 73 dòng chưa thấy mục toàn hình thức trong các bản xuất đã kiểm. Các số này không phải số cặp Việt–Hàn đã xác nhận.
- **Từ điển thuật ngữ 용어사전:** 21 dòng có mục nguồn bổ sung từ 19 mục nguồn riêng biệt. 12 dòng có định nghĩa toàn mục hoặc biến thể liên quan; 3 chỉ thành tố, 3 chỉ nhãn đối dịch/từ chuẩn và 3 khác phạm vi hoặc cần xem xét. 49 dòng được tìm kiếm chuyên ngành có mục tiêu; không tuyên bố đã mở từng thuật ngữ trong mọi bộ từ điển.
- **Hai nhánh Anh:** 75 dòng được xác nhận theo nghĩa đang chọn, gồm 69 cùng biểu thức và 6 biến thể; 22 có điều kiện, 137 ứng viên, 14 khác phạm vi và 18 chưa đủ chứng cứ. Nguồn và trạng thái từng nhánh luôn hiển thị riêng. Trùng nhãn Anh không tự chứng minh cùng khái niệm.

Cặp “nghị quyết — 결의안” có điều chỉnh trong bản này: mục từ lưu lại ghi **draft resolution**, còn nghĩa Việt được chọn là văn bản đã thông qua. Bản ghi giữ cảnh báo lệch phạm vi và yêu cầu kiểm tra cách dùng trong corpus. Các nghĩa đồng hình như 파리협정, 대리대사 và 정부 간 협정 được ghi giới hạn rõ. Mục trong từ điển pháp luật Hàn có thể chỉ thể chế Hàn Quốc; không áp chi tiết đó cho thiết chế Việt Nam.

Excel có thêm hai trang **Định nghĩa đối chiếu** và **Từ điển Hàn**. Các nguồn bổ sung mang mã DI. Phần trích nguyên văn, bản dịch và diễn giải không gộp chung. Các định nghĩa chuyên ngành đều ghi cơ quan biên soạn; 온용어 là cổng tổng hợp, không tự là tác giả mọi mục.

### Ghi nguồn và giấy phép

Định nghĩa văn bản của 국립국어원 trong 한국어기초사전 và 표준국어대사전 được ghi nguồn theo **CC BY-SA 2.0 KR**. Bản dịch và diễn giải tương ứng do nghiên cứu thực hiện, theo cùng giấy phép. Tham khảo [chính sách 한국어기초사전](https://krdict.korean.go.kr/kor/kboardPolicy/copyRightTermsInfo), [chính sách 표준국어대사전](https://www.korean.go.kr/front/page/pageView.do?page_id=P000508) và [giấy phép](https://creativecommons.org/licenses/by-sa/2.0/kr/).

Bản xuất được lưu bởi spellcheck-ko, không phải máy chủ của 국립국어원: 표준국어대사전 ngày 2026-06-05 và 한국어기초사전 ngày 2026-06-19. Trang ghi cả nơi đã đọc và đường dẫn mục từ gốc để kiểm lại. Dữ liệu trung gian gồm toàn bộ từ đồng âm đã loại không được đưa vào bản bàn giao.

Nguồn chuyên ngành giữ thông tin giấy phép tại từng mục. Trích đoạn ngắn và diễn giải nghiên cứu được phân biệt; không áp giấy phép quốc ngữ cho toàn bộ nguồn khác.

## Cấu trúc mã nguồn

- `app/page.tsx`, `app/globals.css`: giao diện nghiên cứu và trình chỉnh sửa.
- `app/api/terms/`: đọc, cập nhật và khôi phục mục.
- `app/api/history/`: lịch sử thay đổi của một mục thuộc tài khoản hiện tại.
- `lib/server-terms.ts`: kiểm tra dữ liệu, phân quyền và kiểm soát xung đột.
- `data/research.json`: bản dữ liệu nguồn được quản lý phiên bản.
- `db/schema.ts`, `drizzle/`: schema và migration D1.
- `public/downloads/`: file Excel nghiên cứu được phục vụ trên trang.
- `.openai/hosting.json`: cấu hình triển khai; kho mã nguồn bàn giao không kèm credential.

## Chạy và triển khai

Ứng dụng dùng Vinext/React và Cloudflare D1. `pnpm-lock.yaml` khóa phiên bản phụ thuộc. Trong môi trường Sites, dùng quy trình chính thức để cài phụ thuộc, tạo bản build, đồng bộ mã nguồn và triển khai. Các lệnh dự án: `npm run build`, `npm run db:generate`, `npm run dev`.

Migration chỉ tạo schema. Dữ liệu nghiên cứu đọc từ file JSON; chỉ chỉnh sửa và lịch sử được ghi vào D1. API production yêu cầu danh tính do Sites cung cấp. Môi trường phát triển có tài khoản thử riêng; nhánh thử không được đưa vào bản production. Hướng dẫn framework giữ tại `README.framework.md`.

Trước bàn giao đã kiểm tra kiểu TypeScript, build, dữ liệu 266 dòng, quyền truy cập, cách ly tài khoản, lưu/khôi phục và xung đột ghi. Xem trước bằng trình duyệt chưa thực hiện được vì dịch vụ preview của môi trường không khả dụng.
