# Bộ Công Cụ Theo Dõi Thứ Hạng Từ Khóa

Dự án này cung cấp một bộ công cụ tự chứa để:

- Thu thập (crawl) thứ hạng từ khóa và số liệu SEO với giới hạn tốc độ có thể cấu hình cùng khả năng tạm dừng/tiếp tục.
- Lên lịch và theo dõi kế hoạch xuất bản nội dung.
- Tổng hợp số liệu kiểu Search Console và GA4 thành các báo cáo lưu lượng.
- Minh họa toàn bộ quy trình thông qua một script demo có thể chạy.

Tất cả tích hợp được hiện thực bằng mock nhẹ, có tính xác định, cho phép kiểm thử cục bộ mà không cần thông tin xác thực bên ngoài. Lớp lưu trữ dựa trên SQLite dùng để theo dõi thứ hạng, lịch nội dung và các báo cáo được tạo.

## Bắt Đầu

1. Cài đặt phụ thuộc (chỉ sử dụng thư viện chuẩn của Python).
2. Chạy bộ kiểm thử tự động:

   ```bash
   pytest
   ```

3. Chạy quy trình demo để quan sát đầu ra của crawler, bộ lập lịch và báo cáo cùng nhau:

   ```bash
   python demo.py
   ```

4. Tích hợp vào dự án của bạn bằng cách import các gói liên quan:

   - `crawler.KeywordCrawler` để thu thập từ khóa; dùng `CrawlerController` để điều chỉnh tốc độ hoặc tạm dừng/tiếp tục.
   - `scheduler.ContentScheduler` để đăng ký và thực thi các bài viết đã lên kế hoạch.
   - `reporting.ReportingPipeline` để tạo các báo cáo tổng hợp.

Giá trị cấu hình mặc định được lưu tại `config/settings.py`. Bạn có thể cung cấp tệp JSON ghi đè ở `config/settings.json` hoặc đặt biến môi trường `CKT_CONFIG` trỏ tới tệp tùy chỉnh.

## Cấu Trúc Kho Mã

```
config/           # Bộ tải cấu hình và giá trị mặc định
crawler/          # Triển khai crawler từ khóa
scheduler/        # Dịch vụ lập lịch nội dung
reporting/        # Pipeline báo cáo lưu lượng
integrations/     # Tích hợp giả lập cho các API của Google
storage/          # Lớp lưu trữ SQLite
tests/            # Bộ kiểm thử tự động
```

## Chạy Bộ Công Cụ

Các mô-đun có thể được kết hợp với nhau để tạo thành một quy trình đầu-cuối:

1. Nạp cấu hình và khởi tạo các tích hợp.
2. Dùng crawler để thu thập số liệu từ khóa và lưu trữ chúng.
3. Lên lịch nội dung sắp xuất bản bằng bộ lập lịch.
4. Tạo báo cáo bằng pipeline báo cáo.

Bộ kiểm thử tự động cũng minh họa quy trình này.
## Tích hợp mới: Requests + BeautifulSoup + APScheduler + JSON

- Crawler có pause/resume linh hoạt qua `crawler.bot.CrawlerController`.
- Bổ sung mô-đun fetch HTML an toàn `crawler/fetcher.py` dùng Requests + BeautifulSoup (retry + backoff, try/except + logging).
- Thêm `scheduler/job_scheduler.py` dựa trên APScheduler để chạy job crawl định kỳ, với `pause()` và `resume()` runtime.
- Xuất dữ liệu JSON ở `reporting/export.py`:
  - `export_keyword_rankings(db, "reporting/output/keyword_rankings.json")`
  - `export_reports(db, "reporting/output/reports.json")`
  Có thể chọn mảng JSON hoặc NDJSON (JSON theo dòng) phù hợp Looker Studio.

### Cài đặt phụ thuộc

```bash
pip install requests beautifulsoup4 apscheduler
```

### Gợi ý vận hành

- Dùng `JobScheduler` để lên lịch crawl theo phút/giây; khi cần bảo trì, gọi `pause()` rồi `resume()` để tiếp tục.
- Bao các tác vụ mạng trong try/except và log lỗi để tránh crash.
- JSON xuất sẵn trong `reporting/output/` để team SEO import Looker Studio.
