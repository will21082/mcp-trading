# 🏛️ Kiến Trúc Hệ Thống MCP Trading (Clean Architecture)

Tài liệu này mô tả chi tiết về cấu trúc mã nguồn của hệ thống **MCP Trading** sau khi đã được hợp nhất và quy hoạch lại theo chuẩn Clean Architecture. Cấu trúc mới giúp hệ thống dễ bảo trì, dễ mở rộng (như gắn thêm Bot Telegram/Email) và loại bỏ hoàn toàn các file rác rườm rà.

---

## 1. 📂 Cây Thư Mục Tổng Quan

```text
mcp-trading/
│
├── frontend/               # 🌐 Giao diện Web (React + Vite)
│   ├── src/                # Code React (Components, Hooks)
│   └── vite.config.js      # Cấu hình proxy tự động trỏ về Backend
│
├── backend/                # ⚙️ Máy chủ và Logic Xử Lý Chuyên Sâu
│   ├── api/                # (Sẽ mở rộng sau) Chứa các Route API phân tách
│   ├── core/               # 🧠 BỘ NÃO CỦA HỆ THỐNG
│   │   ├── scanner.py      # Core: Logic quét coin, BB Squeeze, RSI, EMA...
│   │   └── risk_manager.py # Core: Quản lý rủi ro, Position Size, Stop Loss
│   ├── notifications/      # 📬 NƠI CHỨA CÁC BOT THÔNG BÁO (Mới)
│   │   ├── telegram.py     # (Dự kiến) Bot Telegram
│   │   └── email.py        # (Dự kiến) Bot Email
│   ├── config/             # 🛠 Cấu hình của hệ thống (settings.json)
│   ├── data/               # 📁 Dữ liệu lưu trữ nội bộ (như risk_state.json)
│   ├── main.py             # 🚪 CỬA NGÕ WEB (FastAPI Server)
│   ├── cli.py              # 💻 CỬA NGÕ TERMINAL (Tool gõ lệnh bằng tay)
│   └── requirements.txt    # Danh sách thư viện Python
│
├── tradingview-mcp/        # 📡 Thư viện kết nối TradingView (Module dùng chung)
├── reports/                # 📄 Nơi lưu các báo cáo Scan bằng file Markdown
└── tests/                  # 🧪 Các file kiểm thử tự động (Unit Tests)
```

---

## 2. 🧠 Phân Tích Chức Năng Từng Thành Phần

### A. Tầng Lõi (Core Trading)
* **Vị trí:** `backend/core/`
* **Nhiệm vụ:** Đây là trái tim của hệ thống. Nó không quan tâm nó đang được gọi từ Web, từ Terminal hay từ Bot Telegram. Nhiệm vụ duy nhất của nó là nhận yêu cầu "Hãy quét coin", sau đó tải dữ liệu, chạy các vòng lặp tính toán (Bollinger Band, RSI, Volume) và trả ra danh sách các đồng coin tiềm năng (Signals).
* **Đặc tính:** Độc lập hoàn toàn, dễ dàng mang đi nhúng vào các dự án khác.

### B. Tầng Phục Vụ Web (FastAPI)
* **Vị trí:** `backend/main.py`
* **Nhiệm vụ:** Đóng vai trò là Nhân viên Lễ tân. Nó mở cổng `8000`, nhận lệnh từ trang Web (Frontend), sau đó ra lệnh cho Tầng Lõi (`core/scanner.py`) tính toán. Khi Tầng Lõi tính xong, nó đóng gói kết quả thành JSON và gửi ngược lại cho trang Web hiển thị. Nó cũng quản lý các kết nối thời gian thực (WebSocket).

### C. Tầng Công Cụ (CLI)
* **Vị trí:** `backend/cli.py` (Trước đây là `crypto-trading-system/main.py`)
* **Nhiệm vụ:** Dành riêng cho Lập trình viên. Mở Terminal và gõ `python cli.py --exchanges bybit` để ép hệ thống quét và in kết quả ra màn hình đen mà không cần bật Web.

### D. Tầng Mở Rộng (Notifications)
* **Vị trí:** `backend/notifications/` (Mới)
* **Nhiệm vụ:** Thư mục này được tạo ra dọn đường cho ý tưởng tích hợp **Telegram/Email** của bạn. Sau này, chúng ta chỉ cần viết file `telegram_bot.py` ở đây, import `core/scanner.py` vào là có ngay một con Bot xịn xò hoạt động ngầm.

---

## 3. 🚀 Cách Hoạt Động Của Luồng Dữ Liệu

1. **Người dùng** bấm nút "Start Scan" trên giao diện Web (`frontend`).
2. Web gửi một HTTP POST request đến `http://localhost:8000/api/scan` (Tới `backend/main.py`).
3. `main.py` nhận request, bốc máy gọi `core.scanner.run_scan()`.
4. `scanner.py` sử dụng thư viện `tradingview-mcp` gọi API của TradingView lấy chỉ báo.
5. `scanner.py` chấm điểm các đồng coin và lọc ra những coin ngon nhất, trả về cho `main.py`.
6. `main.py` trả cục dữ liệu JSON đó lại cho `frontend`.
7. `frontend` vẽ lên bảng Dashboard tuyệt đẹp.

> **Khả năng mới (Bot ngầm):** Chúng ta có thể cấu hình để `main.py` tự động kích hoạt `scanner.py` mỗi 15 phút, nếu thấy có coin ngon thì nó gọi tiếp thư mục `notifications/telegram.py` bắn tin nhắn thẳng vào điện thoại của bạn!

---

## 4. 🛠 Cách Chạy Hệ Thống Ở Cấu Trúc Mới

Vì toàn bộ backend đã được đưa về một nơi, việc chạy rất đơn giản:

**Chạy Web Server:**
```bash
cd backend
# Đảm bảo đã kích hoạt môi trường ảo (ví dụ: uv venv)
uvicorn main:app --reload --port 8000
```

**Chạy Tool Gõ Lệnh (CLI):**
```bash
cd backend
python cli.py --exchanges bybit --timeframes 15m
```

**Chạy Frontend:**
```bash
cd frontend
npm run dev
```

---
*Cấu trúc này đảm bảo dự án của bạn có thể phình to thêm gấp 10 lần các tính năng phức tạp mà code vẫn sạch sẽ và dễ hiểu.*
