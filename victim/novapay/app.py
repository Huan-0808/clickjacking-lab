#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NovaPay - Modern E-Wallet Simulation
Standard library implementation compatible with Python 3.5+ (No Flask, No f-strings)
"""

import sys
import os
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import datetime

PORT = 5000
LOG_FILE = "/home/ubuntu/novapay.log"

# In-memory database
DATA = {
    "user": "nan_nhan",
    "password": "123456",
    "name": "Nguyễn Văn Nạn Nhân",
    "wallet_id": "NOVAPAY-8866-9999",
    "balance": 50000000,
    "transactions": [
        {
            "time": "2026-11-19 14:30:00",
            "type": "in",
            "title": "Nhận lương tháng 11",
            "from_to": "Công ty NovaCorp",
            "amount": 35000000,
            "status": "Thành công"
        },
        {
            "time": "2026-11-20 09:15:00",
            "type": "in",
            "title": "Nạp tiền ví điện tử",
            "from_to": "Vietcombank (***1234)",
            "amount": 15000000,
            "status": "Thành công"
        }
    ]
}

def log_event(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_line = "%s - %s\n" % (timestamp, message)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log_line)
            f.flush()
    except Exception as e:
        pass
    sys.stdout.write(log_line)
    sys.stdout.flush()

def format_currency(amount):
    return "{:,} đ".format(amount).replace(",", ".")

COMMON_CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%);
    min-height: 100vh;
    color: #1e293b;
    display: flex;
    flex-direction: column;
}
.navbar {
    background: rgba(15, 23, 42, 0.85);
    backdrop-filter: blur(12px);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding: 16px 32px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: #fff;
}
.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 22px;
    font-weight: 800;
    letter-spacing: -0.5px;
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-decoration: none;
}
.nav-links { display: flex; gap: 20px; align-items: center; }
.nav-links a {
    color: #cbd5e1;
    text-decoration: none;
    font-weight: 500;
    font-size: 14px;
    transition: color 0.2s;
}
.nav-links a:hover { color: #38bdf8; }
.main-content {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 32px 16px;
}
.card {
    background: rgba(255, 255, 255, 0.98);
    border-radius: 20px;
    box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
    padding: 36px;
    width: 100%;
    max-width: 540px;
    backdrop-filter: blur(8px);
}
.card-wide { max-width: 800px; }
.card-header { margin-bottom: 24px; text-align: center; }
.card-title { font-size: 24px; font-weight: 700; color: #0f172a; margin-bottom: 8px; }
.card-subtitle { font-size: 14px; color: #64748b; }
.form-group { margin-bottom: 20px; text-align: left; }
.form-label { display: block; font-size: 13px; font-weight: 600; color: #334155; margin-bottom: 8px; }
.form-control {
    width: 100%;
    padding: 12px 16px;
    border: 1.5px solid #cbd5e1;
    border-radius: 12px;
    font-size: 15px;
    color: #0f172a;
    transition: border-color 0.2s, box-shadow 0.2s;
    background: #f8fafc;
}
.form-control:focus {
    outline: none;
    border-color: #6366f1;
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
    background: #fff;
}
.form-control[readonly] { background: #f1f5f9; cursor: not-allowed; }
.btn-primary {
    width: 100%;
    padding: 14px 20px;
    border: none;
    border-radius: 9999px;
    background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
    color: #ffffff;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 10px 20px -5px rgba(79, 70, 229, 0.4);
    transition: transform 0.15s, box-shadow 0.15s, opacity 0.15s;
}
.btn-primary:hover {
    transform: translateY(-1px);
    box-shadow: 0 14px 24px -5px rgba(79, 70, 229, 0.5);
}
.btn-primary:active { transform: translateY(0); }
.btn-confirm {
    width: 280px;
    height: 50px;
    margin: 0 auto;
    display: block;
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    box-shadow: 0 10px 20px -5px rgba(16, 185, 129, 0.4);
}
.btn-confirm:hover { box-shadow: 0 14px 24px -5px rgba(16, 185, 129, 0.5); }
.balance-card {
    background: linear-gradient(135deg, #312e81 0%, #4338ca 100%);
    border-radius: 16px;
    padding: 24px;
    color: #ffffff;
    margin-bottom: 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.balance-label { font-size: 13px; color: #c7d2fe; text-transform: uppercase; letter-spacing: 0.5px; }
.balance-value { font-size: 32px; font-weight: 800; margin-top: 6px; letter-spacing: -0.5px; }
.quick-action-btn {
    padding: 10px 18px;
    background: rgba(255, 255, 255, 0.2);
    border: 1px solid rgba(255, 255, 255, 0.3);
    border-radius: 9999px;
    color: #ffffff;
    font-weight: 600;
    font-size: 13px;
    text-decoration: none;
    transition: background 0.2s;
}
.quick-action-btn:hover { background: rgba(255, 255, 255, 0.3); }
.table-container { overflow-x: auto; margin-top: 16px; }
table { width: 100%; border-collapse: collapse; text-align: left; }
th { font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase; padding: 12px 14px; border-bottom: 1.5px solid #e2e8f0; }
td { padding: 14px; font-size: 14px; border-bottom: 1px solid #f1f5f9; color: #1e293b; }
.badge { display: inline-block; padding: 4px 10px; border-radius: 9999px; font-size: 12px; font-weight: 600; }
.badge-in { background: #dcfce7; color: #15803d; }
.badge-out { background: #fee2e2; color: #b91c1c; }
.alert-success {
    background: #ecfdf5;
    border: 1px solid #a7f3d0;
    color: #065f46;
    padding: 12px 16px;
    border-radius: 12px;
    margin-bottom: 20px;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 10px;
}
"""

class NovaPayHandler(BaseHTTPRequestHandler):
    def send_standard_headers(self, content_type="text/html; charset=utf-8", status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        
        # === [TASK 6: VÁ LỖ HỔNG CLICKJACKING - BỎ COMMENT 2 DÒNG DƯỚI ĐÂY] ===
        # self.send_header('X-Frame-Options', 'DENY')
        # self.send_header('Content-Security-Policy', "frame-ancestors 'none'")
        # =====================================================================

    def do_HEAD(self):
        """Phục vụ lệnh curl -I kiểm tra response headers đầy đủ"""
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        if path in ["/", "/login", "/dashboard", "/transfer"]:
            self.send_standard_headers()
            self.end_headers()
        else:
            self.send_error(404, "Page Not Found")

    def parse_cookie(self):
        cookies = {}
        cookie_header = self.headers.get("Cookie")
        if cookie_header:
            for item in cookie_header.split(";"):
                item = item.strip()
                if "=" in item:
                    k, v = item.split("=", 1)
                    cookies[k.strip()] = v.strip()
        return cookies

    def is_logged_in(self):
        cookies = self.parse_cookie()
        return cookies.get("session") == "nan_nhan_auth"

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query = urllib.parse.parse_qs(parsed_url.query)

        if path == "/login":
            self.render_login()
        elif path == "/" or path == "/dashboard":
            if not self.is_logged_in():
                self.redirect_to("/login")
                return
            show_success = "success" in query
            self.render_dashboard(show_success=show_success)
        elif path == "/transfer":
            if not self.is_logged_in():
                self.redirect_to("/login")
                return
            # Ghi nhận Referer của trang cha tải iframe (bắt đầu bằng http://attacker:8000)
            req_referer = self.headers.get("Referer", "")
            parent_ref = req_referer if req_referer.startswith("http://attacker:8000") else ""
            self.render_transfer(parent_referer=parent_ref)
        elif path == "/logout":
            self.send_response(303)
            self.send_header("Location", "/login")
            self.send_header("Set-Cookie", "session=; Path=/; Expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=None")
            self.end_headers()
        else:
            self.send_error(404, "Page Not Found")

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        post_data = urllib.parse.parse_qs(body)

        if path == "/login":
            username = post_data.get("username", [""])[0]
            password = post_data.get("password", [""])[0]
            
            # Ghi log bắt buộc cho Task 1
            log_event("POST /login - Attempted login for user: %s" % username)

            if username == DATA["user"]:
                self.send_response(303)
                self.send_header("Location", "/dashboard")
                self.send_header("Set-Cookie", "session=nan_nhan_auth; Path=/; SameSite=None")
                self.end_headers()
            else:
                self.render_login(error="Tên đăng nhập không đúng. Vui lòng dùng tài khoản mẫu 'nan_nhan'.")

        elif path == "/transfer":
            # Kiểm tra Referer của request POST /transfer và nguồn gốc tải form
            post_referer = self.headers.get("Referer", "")
            parent_referer = post_data.get("parent_referer", [""])[0]

            # Chỉ ghi dest=iframe khi Referer của POST hoặc parent Referer bắt đầu bằng http://attacker:8000
            if post_referer.startswith("http://attacker:8000") or parent_referer.startswith("http://attacker:8000"):
                dest = "iframe"
            else:
                dest = "direct"

            # Ghi log bắt buộc cho Task 5
            log_event("POST /transfer dest=%s - Transaction processed" % dest)

            amount_str = post_data.get("amount", ["5000000"])[0].replace(".", "").replace(",", "").replace("đ", "").strip()
            try:
                amount = int(amount_str)
            except Exception:
                amount = 5000000

            recipient = post_data.get("recipient", ["attacker_wallet"])[0]
            note = post_data.get("note", ["Thanh toán hợp đồng"])[0]

            DATA["balance"] -= amount
            DATA["transactions"].insert(0, {
                "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": "out",
                "title": "Chuyển tiền đến " + recipient,
                "from_to": recipient,
                "amount": amount,
                "status": "Thành công"
            })

            self.send_response(303)
            self.send_header("Location", "/dashboard?success=1")
            self.end_headers()
        else:
            self.send_error(404, "Not Found")

    def redirect_to(self, target):
        self.send_response(303)
        self.send_header("Location", target)
        self.end_headers()

    def render_login(self, error=""):
        self.send_standard_headers()
        self.end_headers()

        error_html = ""
        if error:
            error_html = '<div style="background:#fee2e2;border:1px solid #fca5a5;color:#991b1b;padding:12px;border-radius:12px;margin-bottom:20px;font-size:14px;">%s</div>' % error

        html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>NovaPay - Đăng Nhập Ví Điện Tử</title>
    <style>%s</style>
</head>
<body>
    <div class="navbar">
        <a href="/login" class="brand">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="4"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
            NovaPay
        </a>
    </div>
    <div class="main-content">
        <div class="card">
            <div class="card-header">
                <h1 class="card-title">Đăng Nhập Ví NovaPay</h1>
                <p class="card-subtitle">Hệ thống ví điện tử thanh toán an toàn, tiện lợi</p>
            </div>
            %s
            <form method="POST" action="/login">
                <div class="form-group">
                    <label class="form-label">Tên đăng nhập</label>
                    <input type="text" name="username" class="form-control" value="nan_nhan" required autofocus>
                </div>
                <div class="form-group">
                    <label class="form-label">Mật khẩu</label>
                    <input type="password" name="password" class="form-control" value="123456" required>
                </div>
                <button type="submit" class="btn-primary">Đăng Nhập Ngay</button>
            </form>
            <div style="margin-top:20px;font-size:13px;color:#64748b;text-align:center;">
                Tài khoản mẫu: <b>nan_nhan</b> / Mật khẩu: <b>123456</b>
            </div>
        </div>
    </div>
</body>
</html>""" % (COMMON_CSS, error_html)
        self.wfile.write(html.encode("utf-8"))

    def render_dashboard(self, show_success=False):
        self.send_standard_headers()
        self.end_headers()

        success_html = ""
        if show_success:
            success_html = """<div class="alert-success">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                <span>Giao dịch chuyển tiền vừa được thực hiện thành công!</span>
            </div>"""

        rows_html = ""
        for tx in DATA["transactions"]:
            badge_class = "badge-in" if tx["type"] == "in" else "badge-out"
            sign = "+" if tx["type"] == "in" else "-"
            amount_display = "%s %s" % (sign, format_currency(tx["amount"]))
            rows_html += """<tr>
                <td>%s</td>
                <td><b>%s</b><br><span style="color:#64748b;font-size:12px;">%s</span></td>
                <td><span class="badge %s">%s</span></td>
                <td style="font-weight:700;">%s</td>
            </tr>""" % (tx["time"], tx["title"], tx["from_to"], badge_class, tx["status"], amount_display)

        html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>NovaPay - Tổng Quan Tài Khoản</title>
    <style>%s</style>
</head>
<body>
    <div class="navbar">
        <a href="/dashboard" class="brand">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="4"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
            NovaPay
        </a>
        <div class="nav-links">
            <a href="/dashboard">Tổng quan</a>
            <a href="/transfer" style="color:#38bdf8;font-weight:700;">Chuyển tiền</a>
            <a href="/logout">Đăng xuất (%s)</a>
        </div>
    </div>
    <div class="main-content">
        <div class="card card-wide">
            %s
            <div class="balance-card">
                <div>
                    <div class="balance-label">Số dư khả dụng (%s)</div>
                    <div class="balance-value">%s</div>
                    <div style="font-size:13px;color:#e0e7ff;margin-top:4px;">Chủ ví: %s</div>
                </div>
                <div>
                    <a href="/transfer" class="quick-action-btn">Chuyển tiền ngay &rarr;</a>
                </div>
            </div>
            <div class="card-header" style="text-align:left;display:flex;justify-content:space-between;align-items:center;">
                <h2 class="card-title" style="font-size:20px;">Lịch Sử Giao Dịch Gần Đây</h2>
                <span style="font-size:13px;color:#64748b;">Thời gian thực</span>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Thời gian</th>
                            <th>Nội dung</th>
                            <th>Trạng thái</th>
                            <th>Số tiền</th>
                        </tr>
                    </thead>
                    <tbody>
                        %s
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</body>
</html>""" % (COMMON_CSS, DATA["user"], success_html, DATA["wallet_id"], format_currency(DATA["balance"]), DATA["name"], rows_html)
        self.wfile.write(html.encode("utf-8"))

    def render_transfer(self, parent_referer=""):
        self.send_standard_headers()
        self.end_headers()

        html = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <title>NovaPay - Chuyển Tiền</title>
    <style>%s</style>
</head>
<body>
    <div class="navbar">
        <a href="/dashboard" class="brand">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="4"/><line x1="2" y1="10" x2="22" y2="10"/></svg>
            NovaPay
        </a>
        <div class="nav-links">
            <a href="/dashboard">Tổng quan</a>
            <a href="/transfer" style="color:#38bdf8;font-weight:700;">Chuyển tiền</a>
            <a href="/logout">Đăng xuất</a>
        </div>
    </div>
    <div class="main-content">
        <div class="card">
            <div class="card-header">
                <h1 class="card-title">Chuyển Tiền Nhanh 24/7</h1>
                <p class="card-subtitle">Chuyển tiền đến ví điện tử khác không mất phí</p>
            </div>
            <form method="POST" action="/transfer" id="form-transfer">
                <input type="hidden" name="parent_referer" value="%s">
                <div class="form-group">
                    <label class="form-label">Tài khoản nguồn</label>
                    <input type="text" class="form-control" value="%s (Số dư: %s)" readonly>
                </div>
                <div class="form-group">
                    <label class="form-label">Ví người nhận</label>
                    <input type="text" name="recipient" class="form-control" value="attacker_wallet" readonly>
                </div>
                <div class="form-group">
                    <label class="form-label">Số tiền chuyển (VND)</label>
                    <input type="text" name="amount" class="form-control" value="5.000.000" readonly>
                </div>
                <div class="form-group">
                    <label class="form-label">Nội dung chuyển tiền</label>
                    <input type="text" name="note" class="form-control" value="Thanh toán hợp đồng" readonly>
                </div>
                <div style="margin-top:30px;">
                    <button type="submit" id="btn-transfer" class="btn-primary btn-confirm">Xác nhận chuyển tiền</button>
                </div>
            </form>
        </div>
    </div>
</body>
</html>""" % (COMMON_CSS, parent_referer, DATA["name"], format_currency(DATA["balance"]))
        self.wfile.write(html.encode("utf-8"))

def run():
    server_address = ("0.0.0.0", PORT)
    httpd = HTTPServer(server_address, NovaPayHandler)
    log_event("NovaPay server started on http://0.0.0.0:%d" % PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    log_event("NovaPay server stopped.")

if __name__ == "__main__":
    run()
