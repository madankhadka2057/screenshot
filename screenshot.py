from flask import Flask, request, send_file, jsonify
from playwright.sync_api import sync_playwright
import io

app = Flask(__name__)

@app.route('/screenshot', methods=['POST'])
def screenshot():
    data = request.json
    print("Received data:", data)
    url = data.get("url")
    width = data.get("width", 1120)
    height = data.get("height", 900)
    full_page = data.get("fullPage", True)

    username = data.get("username")
    password = data.get("password")
    login_url = data.get("loginUrl", "https://itcpms.com/login")

    if not url:
        return jsonify({"success": False, "error": "Missing URL"}), 400

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": width, "height": height})

            # If login credentials provided, perform login first
            if username and password:
                page.goto(login_url, wait_until="networkidle")

                # 🔹 change selectors to match your login form
                page.fill("#email", username)
                page.fill("#password", password)

                with page.expect_navigation(wait_until="networkidle"):
                    page.click("#submit-login")

            # Now go to target page after login
            page.goto(url, wait_until="networkidle")

            screenshot_bytes = page.screenshot(full_page=full_page,clip={"x": 0, "y": 0, "width": width, "height": height}
    )
            browser.close()

        screenshot_io = io.BytesIO(screenshot_bytes)
        screenshot_io.seek(0)

        return send_file(
            screenshot_io,
            mimetype='image/png',
            as_attachment=True,
            download_name='screenshot.png'
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)
