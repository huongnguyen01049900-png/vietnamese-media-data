(() => {
  const D={
    vi:{
      database:"Cơ sở dữ liệu",presentation:"Bản trình bày",live:"Live Monitor",download:"Tải Excel",openExcel:"Mở Excel khác",
      brandTitle:"Truyền thông tiếng Việt ngoài Việt Nam",brandSub:"Báo · đài · tạp chí · tổ chức · cộng đồng — dữ liệu nghiên cứu + live monitor",
      dataSource:"Nguồn dữ liệu:",loading:"Đang tải…",total:"Tổng bản ghi",sources:"Nguồn truyền thông",creators:"Creator / blog",magazines:"Tạp chí bổ sung",countries:"Quốc gia / thị trường",checked:"Ngày kiểm tra",
      overview:"Phân bố dữ liệu",countryChart:"Theo quốc gia / thị trường",statusChart:"Theo trạng thái hoạt động",datasetChart:"Theo nhóm dữ liệu",
      explorer:"Tra cứu và kiểm chứng",search:"Tìm kiếm toàn bảng",country:"Quốc gia / thị trường",status:"Trạng thái",type:"Loại / nền tảng",all:"Tất cả",reset:"Xóa lọc",csv:"Xuất CSV",
      shown:"bản ghi hiển thị",rowHint:"Chọn một dòng để xem toàn bộ trường dữ liệu và URL nguồn.",
      method:"Đọc dữ liệu có trách nhiệm",unknownT:"UNKNOWN không phải “không có”",unknownP:"UNKNOWN nghĩa là chưa xác minh được từ nguồn công khai trong vòng nghiên cứu, không phải khẳng định thông tin đó không tồn tại.",
      creatorT:"Creator ≠ newsroom",creatorP:"Kênh cá nhân, blog, NGO và advocacy được phân loại riêng. Không mặc định chúng có quy trình biên tập như báo chí chuyên nghiệp.",
      primaryT:"Ưu tiên nguồn gốc",primaryP:"Các cột nguồn chính, nguồn bổ sung và mức bằng chứng giúp phân biệt dữ liệu trực tiếp với nguồn thứ ba.",
      timeT:"Dữ liệu có thời điểm",timeP:"Số follower, lịch phát, tổng biên tập và trạng thái hoạt động có thể thay đổi. Luôn xem ngày kiểm tra trước khi sử dụng.",
      presentationTeaser:"Nội dung trình bày cho giáo sư",presentationText:"Bản trình bày song ngữ Việt–Hàn tập trung vào các nguồn tổ chức và tạp chí; creator/blog/YouTube chỉ dùng như số liệu nền.",openPresentation:"Mở bản trình bày song ngữ →",
      liveTitle:"Luồng tin trực tiếp",liveSub:"RSS · Atom · YouTube · website · links — cập nhật tự động bằng GitHub Actions",liveData:"Dữ liệu live:",liveSources:"Tổng nguồn có link",liveOk:"Kết nối lấy bài",liveLinks:"Link-only",liveItems:"Mục đã thu",liveErrors:"Nguồn lỗi crawl",
      feedTitle:"Bài viết & video gần nhất",feedNote:"Nguồn lấy được bài sẽ hiển thị metadata; nguồn không lấy được bài vẫn được giữ thành liên kết trực tiếp bên dưới.",sourceHealth:"Source Health",
      directory:"Nguồn chỉ liên kết / chưa lấy được bài",directoryNote:"Các link này vẫn được duy trì để bạn mở trực tiếp sang nguồn gốc. Không có nguồn nào bị loại chỉ vì crawler không lấy được bài.",
      openSource:"Mở nguồn ↗",noRows:"Không có bản ghi phù hợp bộ lọc.",sourcesTab:"Nguồn truyền thông",creatorsTab:"Creator / blog",magazinesTab:"Tạp chí"
    },
    ko:{
      database:"데이터베이스",presentation:"발표 자료",live:"라이브 모니터",download:"Excel 다운로드",openExcel:"다른 Excel 열기",
      brandTitle:"베트남 밖의 베트남어 미디어",brandSub:"신문 · 방송 · 잡지 · 단체 · 커뮤니티 — 연구 데이터 + 라이브 모니터",
      dataSource:"데이터 출처:",loading:"불러오는 중…",total:"전체 레코드",sources:"미디어 소스",creators:"크리에이터 / 블로그",magazines:"추가 잡지",countries:"국가 / 시장",checked:"검토일",
      overview:"데이터 분포",countryChart:"국가 / 시장별",statusChart:"활동 상태별",datasetChart:"데이터 그룹별",
      explorer:"검색 및 검증",search:"전체 표 검색",country:"국가 / 시장",status:"상태",type:"유형 / 플랫폼",all:"전체",reset:"필터 초기화",csv:"CSV 내보내기",
      shown:"개 레코드 표시",rowHint:"행을 선택하면 전체 필드와 원문 URL을 볼 수 있습니다.",
      method:"데이터를 책임 있게 읽는 방법",unknownT:"UNKNOWN은 “없음”이 아닙니다",unknownP:"UNKNOWN은 공개 자료에서 확인하지 못했다는 뜻이며 해당 정보가 존재하지 않는다는 뜻이 아닙니다.",
      creatorT:"크리에이터 ≠ 뉴스룸",creatorP:"개인 채널, 블로그, NGO, advocacy는 별도로 분류하며 전문 뉴스룸과 동일한 편집 절차를 전제하지 않습니다.",
      primaryT:"1차 출처 우선",primaryP:"공식 출처, 추가 출처, 증거 수준 필드를 통해 직접 자료와 제3자 자료를 구분합니다.",
      timeT:"데이터에는 시점이 있습니다",timeP:"팔로워 수, 방송 편성, 편집 책임자, 활동 상태는 바뀔 수 있으므로 검토일을 확인해야 합니다.",
      presentationTeaser:"교수 발표용 연구 내용",presentationText:"베트남어–한국어 이중언어 발표 페이지입니다. 기관형 미디어와 잡지에 초점을 맞추고 creator/blog/YouTube는 배경 통계로만 사용합니다.",openPresentation:"이중언어 발표 자료 열기 →",
      liveTitle:"실시간 미디어 피드",liveSub:"RSS · Atom · YouTube · website · links — GitHub Actions로 자동 갱신",liveData:"라이브 데이터:",liveSources:"링크 보유 소스",liveOk:"수집 연결 성공",liveLinks:"링크 전용",liveItems:"수집 항목",liveErrors:"수집 오류 소스",
      feedTitle:"최신 기사 & 영상",feedNote:"수집 가능한 소스는 메타데이터를 표시하고, 수집이 어려운 소스도 원문 링크는 유지합니다.",sourceHealth:"Source Health",
      directory:"링크 전용 / 수집 미지원 소스",directoryNote:"크롤러가 항목을 가져오지 못해도 원문 링크를 유지합니다.",
      openSource:"원문 열기 ↗",noRows:"조건에 맞는 레코드가 없습니다.",sourcesTab:"미디어 소스",creatorsTab:"크리에이터 / 블로그",magazinesTab:"잡지"
    }
  };
  const api={lang:localStorage.getItem("vm-lang")||"vi",t(k){return (D[this.lang]&&D[this.lang][k])||D.vi[k]||k},setLang(l){if(!D[l])return;this.lang=l;localStorage.setItem("vm-lang",l);document.documentElement.lang=l;this.apply();window.dispatchEvent(new CustomEvent("vm:langchange",{detail:{lang:l}}))},apply(){document.querySelectorAll("[data-t]").forEach(el=>el.textContent=this.t(el.dataset.t));document.querySelectorAll("[data-ph]").forEach(el=>el.placeholder=this.t(el.dataset.ph));document.querySelectorAll("[data-lang]").forEach(el=>el.classList.toggle("active",el.dataset.lang===this.lang));document.documentElement.lang=this.lang}};
  window.VM_I18N=api;
  document.addEventListener("DOMContentLoaded",()=>{document.querySelectorAll("[data-lang]").forEach(b=>b.addEventListener("click",()=>api.setLang(b.dataset.lang)));api.apply()});
})();