ACCOUNTS = {
    "pj": ("demo@kingshand.id", "demo123"),
    "admin": ("admin@kingshand.id", "admin123"),
}


def login(page, role):
    email, pw = ACCOUNTS[role]
    page.fill("#email", email)
    page.fill("#pw", pw)
    page.click("#loginBtn")
    page.wait_for_selector("#app #hello")


def logout(page):
    page.click("#logoutBtn")
    page.wait_for_selector("#loginForm", state="visible")


def nav(page, label):
    page.click(f"#mainNav button:has-text('{label}')")


def open_project(page, name):
    nav(page, "Proyek")
    page.click(f"#projList .pitem:has-text(\"{name}\")")
    page.wait_for_selector("#detail h1")


def fake_file(name, mime="application/pdf"):
    return {"name": name, "mimeType": mime, "buffer": b"%PDF-1.4 contoh"}
