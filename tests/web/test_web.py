"""Test end-to-end versi web King's Hand.

Tiap test memakai browser context baru, jadi data contoh selalu mulai dari awal.
"""
from playwright.sync_api import expect

from helpers import fake_file, login, logout, nav, open_project


# ---------- Login ----------

def test_login_gagal_dengan_kata_sandi_salah(page):
    page.fill("#email", "demo@kingshand.id")
    page.fill("#pw", "salah")
    page.click("#loginBtn")
    expect(page.locator("#loginErr")).to_contain_text("salah")
    expect(page.locator("#app")).to_be_hidden()


def test_tombol_akun_demo_mengisi_form(page):
    page.click("[data-acct=admin]")
    expect(page.locator("#email")).to_have_value("admin@kingshand.id")
    expect(page.locator("#pw")).to_have_value("admin123")


def test_menu_berbeda_untuk_tiap_peran(page):
    login(page, "pj")
    expect(page.locator("#mainNav")).to_contain_text("Proposal")
    expect(page.locator("#mainNav")).not_to_contain_text("Evaluasi proposal")
    expect(page.locator("#profileBtn")).to_be_visible()
    logout(page)
    login(page, "admin")
    expect(page.locator("#mainNav")).to_contain_text("Evaluasi proposal")
    expect(page.locator("#mainNav")).to_contain_text("Laporan masuk")
    expect(page.locator("#profileBtn")).to_be_hidden()


def test_admin_tidak_bisa_membuka_halaman_khusus_pj(page):
    login(page, "admin")
    page.evaluate("location.hash='proposal'")
    expect(page.locator("#p-dashboard")).to_be_visible()
    expect(page.locator("#p-proposal")).to_be_hidden()


# ---------- Proposal: alur dua peran ----------

def _ajukan(page, judul="Taman Baca Ujungberung", dana="150"):
    nav(page, "Proposal")
    page.fill("#fJudul", judul)
    page.fill("#fLokasi", "Ujungberung, Bandung")
    page.fill("#fTarget", "Anak SD")
    page.fill("#fDana", dana)
    page.fill("#fMulai", "2026-12")
    page.fill("#fDesk", "Taman baca untuk warga.")
    page.set_input_files("#fFile", fake_file("Proposal-Taman-Baca.pdf"))
    page.click("#propSubmit")


def test_proposal_wajib_lengkap(page):
    login(page, "pj")
    nav(page, "Proposal")
    page.fill("#fJudul", "Hanya judul")
    page.click("#propSubmit")
    expect(page.locator("#propErr")).to_contain_text("Lengkapi")


def test_proposal_disetujui_admin_menjadi_proyek_aktif(page):
    login(page, "pj")
    _ajukan(page)
    expect(page.locator("#propTable")).to_contain_text("Taman Baca Ujungberung")
    expect(page.locator("#propTable tr", has_text="Taman Baca").locator(".badge")).to_have_text("Menunggu persetujuan")
    logout(page)

    login(page, "admin")
    nav(page, "Evaluasi proposal")
    card = page.locator(".review-card", has_text="Taman Baca Ujungberung")
    expect(card).to_contain_text("Proposal-Taman-Baca.pdf")
    card.locator("textarea").fill("Silakan mulai, kirim laporan tiap bulan.")
    card.locator("[data-approve]").click()
    expect(page.locator("#reviewHistory")).to_contain_text("Taman Baca Ujungberung")
    logout(page)

    login(page, "pj")
    expect(page.locator("#dashNotif")).to_contain_text("Taman Baca Ujungberung disetujui")
    open_project(page, "Taman Baca Ujungberung")
    expect(page.locator("#detail .badge").first).to_have_text("Aktif")
    expect(page.locator("#up-dev")).to_be_attached()


def test_penolakan_wajib_ada_alasan_dan_sampai_ke_pj(page):
    login(page, "admin")
    nav(page, "Evaluasi proposal")
    card = page.locator(".review-card", has_text="Sumur Bor Desa Cikadu")
    card.locator("[data-reject]").click()
    expect(card.locator(".err")).to_contain_text("alasan")
    card.locator("textarea").fill("Lampirkan hasil survei debit air.")
    card.locator("[data-reject]").click()
    expect(page.locator(".review-card", has_text="Sumur Bor")).to_have_count(0)
    logout(page)

    login(page, "pj")
    nav(page, "Proposal")
    row = page.locator("#propTable tr", has_text="Sumur Bor Desa Cikadu")
    expect(row.locator(".badge")).to_have_text("Ditolak")
    expect(row).to_contain_text("Lampirkan hasil survei debit air.")
    # proyek yang ditolak tidak muncul di daftar proyek
    nav(page, "Proyek")
    expect(page.locator("#projList")).not_to_contain_text("Sumur Bor")


# ---------- Peringatan otomatis ----------

def test_peringatan_awal_muncul_di_dashboard(page):
    login(page, "pj")
    att = page.locator("#attention")
    expect(att).to_contain_text("Perlu perhatian (2)")
    expect(att).to_contain_text("Klinik Desa Sukamaju: Dana terpakai lebih cepat dari progres")
    expect(att).to_contain_text("Sekolah Luar Biasa Papua: Laporan perkembangan terlambat")


def test_filter_perlu_perhatian(page):
    login(page, "admin")
    page.click("#stats [data-filter=attention]")
    items = page.locator("#projList .pitem")
    expect(items).to_have_count(2)


def test_kirim_laporan_menghapus_peringatan_terlambat(page):
    login(page, "pj")
    open_project(page, "Sekolah Luar Biasa Papua")
    expect(page.locator("#detailAlerts")).to_contain_text("terlambat")
    page.set_input_files("#up-dev", fake_file("Progres-Dinding.pdf"))
    page.fill("#val-dev", "60")
    page.click("#send-dev")
    expect(page.locator("#detailAlerts")).not_to_contain_text("terlambat")
    expect(page.locator("#detailProgress")).to_have_text("60%")
    expect(page.locator("#rep-dev")).to_contain_text("Menunggu diperiksa")


def test_laporan_keuangan_bisa_memicu_peringatan_dana(page):
    login(page, "pj")
    open_project(page, "Cafe Le' de Jainero")
    expect(page.locator("#detailAlerts")).to_contain_text("aman")
    page.set_input_files("#up-keu", fake_file("Belanja-Mesin-Kopi.xlsx", "application/vnd.ms-excel"))
    page.fill("#val-keu", "450")   # 90% anggaran, progres 63%
    page.click("#send-keu")
    expect(page.locator("#detailAlerts")).to_contain_text("Dana terpakai 90% dari anggaran, progres pekerjaan baru 63%")


def test_validasi_form_laporan(page):
    login(page, "pj")
    open_project(page, "Bank Sampah Cikutra")
    form = page.locator(".report-form[data-kind=dev]")
    page.click("#send-dev")
    expect(form.locator(".err")).to_contain_text("Pilih file")
    page.set_input_files("#up-dev", fake_file("x.pdf"))
    page.fill("#val-dev", "120")
    page.click("#send-dev")
    expect(form.locator(".err")).to_contain_text("antara 0 dan 100")
    page.fill("#val-dev", "50")    # lebih kecil dari progres sekarang (90%)
    page.click("#send-dev")
    expect(form.locator(".err")).to_contain_text("tidak boleh turun")


# ---------- Pemeriksaan laporan oleh admin ----------

def test_admin_menerima_laporan_dan_pj_diberi_tahu(page):
    login(page, "admin")
    nav(page, "Laporan masuk")
    row = page.locator("#reportQueue tr", has_text="Progres-Unit-Pilah.pdf")
    row.locator("[data-ok]").click()
    expect(page.locator("#reportQueue")).not_to_contain_text("Progres-Unit-Pilah.pdf")
    expect(page.locator("#reportDone")).to_contain_text("Progres-Unit-Pilah.pdf")
    logout(page)
    login(page, "pj")
    expect(page.locator("#dashNotif")).to_contain_text("Laporan perkembangan Bank Sampah Cikutra diterima admin")


def test_minta_revisi_wajib_catatan_dan_menjadi_peringatan(page):
    login(page, "admin")
    nav(page, "Laporan masuk")
    row = page.locator("#reportQueue tr", has_text="Belanja-Bibit-Nutrisi.pdf")
    row.locator("[data-rev]").click()
    expect(row.locator(".err")).to_contain_text("revisi")
    row.locator("input").fill("Lampirkan nota pembelian.")
    row.locator("[data-rev]").click()
    logout(page)
    login(page, "pj")
    expect(page.locator("#attention")).to_contain_text("Kebun Hidroponik Sekolah: Laporan keuangan perlu revisi")
    expect(page.locator("#attention")).to_contain_text("Lampirkan nota pembelian.")


def test_penghitung_menu_admin_berkurang(page):
    login(page, "admin")
    review_btn = page.locator("#mainNav button", has_text="Evaluasi proposal")
    expect(review_btn.locator(".count")).to_have_text("2")
    nav(page, "Evaluasi proposal")
    page.locator(".review-card", has_text="Curug Telu").locator("[data-approve]").click()
    expect(page.locator("#mainNav button", has_text="Evaluasi proposal").locator(".count")).to_have_text("1")


# ---------- Profil, notifikasi, reset ----------

def test_ubah_profil(page):
    login(page, "pj")
    page.click("#profileBtn")
    page.click("#editProfile")
    page.fill("#uName", "Rina Sari")
    page.click("#saveProfile")
    nav(page, "Dashboard")
    expect(page.locator("#hello")).to_have_text("Halo, Rina")


def test_profil_menolak_email_tidak_valid(page):
    login(page, "pj")
    page.click("#profileBtn")
    page.click("#editProfile")
    page.fill("#uEmail", "bukan-email")
    page.click("#saveProfile")
    expect(page.locator("#profileErr")).to_contain_text("email")


def test_membuka_notifikasi_menandai_sudah_dibaca(page):
    login(page, "admin")
    expect(page.locator("#bellDot")).to_be_visible()
    page.click("#bellBtn")
    expect(page.locator("#notifPanel")).to_be_visible()
    expect(page.locator("#bellDot")).to_be_hidden()


def test_data_tersimpan_setelah_muat_ulang_dan_bisa_direset(page):
    login(page, "pj")
    _ajukan(page, judul="Proposal Uji Reset")
    page.reload()
    nav(page, "Proposal")
    expect(page.locator("#propTable")).to_contain_text("Proposal Uji Reset")
    page.click("#resetBtn")
    expect(page.locator("#propTable")).not_to_contain_text("Proposal Uji Reset")


# ---------- Regresi: bug yang ditemukan saat pengujian eksploratif ----------
# Laporan bug lengkap: https://github.com/rivaldimhr/qa-automation-portfolio/blob/main/docs/bug-reports.md

def _kirim(page, kind, value, nama="laporan.pdf"):
    page.set_input_files(f"#up-{kind}", fake_file(nama))
    page.fill(f"#val-{kind}", str(value))
    page.click(f"#send-{kind}")


def _minta_revisi(page, nama_file, catatan):
    nav(page, "Laporan masuk")
    row = page.locator("#reportQueue tr", has_text=nama_file)
    row.locator("input").fill(catatan)
    row.locator("[data-rev]").click()


def test_progres_bisa_dikoreksi_setelah_diminta_revisi(page):
    """BUG-01: progres yang terlanjur terlalu tinggi harus bisa diturunkan setelah admin meminta revisi."""
    login(page, "pj")
    open_project(page, "Cafe Le' de Jainero")
    _kirim(page, "dev", 95, "laporan-salah.pdf")
    logout(page)
    login(page, "admin")
    _minta_revisi(page, "laporan-salah.pdf", "Progres sebenarnya 70%")
    logout(page)
    login(page, "pj")
    open_project(page, "Cafe Le' de Jainero")
    _kirim(page, "dev", 70, "laporan-benar.pdf")
    expect(page.locator(".report-form[data-kind=dev] .err")).to_have_text("")
    expect(page.locator("#detailProgress")).to_have_text("70%")
    _kirim(page, "dev", 60, "lebih-rendah.pdf")   # di bawah progres yang sudah diterima (63%) tetap ditolak
    expect(page.locator(".report-form[data-kind=dev] .err")).to_contain_text("tidak boleh turun")


def test_peringatan_revisi_hilang_setelah_laporan_diganti(page):
    """BUG-02: setelah PJ mengirim laporan pengganti, peringatan "perlu revisi" tidak tampil lagi."""
    login(page, "admin")
    _minta_revisi(page, "Progres-Unit-Pilah.pdf", "Lampirkan foto")
    logout(page)
    login(page, "pj")
    open_project(page, "Bank Sampah Cikutra")
    expect(page.locator("#detailAlerts")).to_contain_text("perlu revisi")
    _kirim(page, "dev", 90, "Progres-Unit-Pilah-revisi.pdf")
    expect(page.locator("#detailAlerts")).not_to_contain_text("perlu revisi")
    expect(page.locator("#rep-dev")).to_contain_text("Diganti laporan baru")


def test_dana_melebihi_anggaran_memicu_peringatan(page):
    """BUG-03: dana terpakai di atas 100% anggaran tidak boleh dianggap aman."""
    login(page, "pj")
    open_project(page, "Bank Sampah Cikutra")
    _kirim(page, "dev", 100, "progres-akhir.pdf")
    _kirim(page, "keu", 130, "keuangan-akhir.pdf")      # anggaran Rp 120 juta
    expect(page.locator("#detailAlerts")).to_contain_text("Dana terpakai melebihi anggaran")
    expect(page.locator("#detailAlerts")).to_contain_text("108%")


def test_persetujuan_mempertahankan_rencana_mulai(page):
    """BUG-04: bulan mulai yang direncanakan PJ tidak boleh diganti bulan persetujuan."""
    import datetime
    d = datetime.date.today().replace(day=1) + datetime.timedelta(days=95)
    rencana = d.strftime("%Y-%m")
    login(page, "pj")
    nav(page, "Proposal")
    page.fill("#fJudul", "Taman Baca Anak")
    page.fill("#fLokasi", "Cimahi")
    page.fill("#fTarget", "Anak SD")
    page.fill("#fDana", "50")
    page.fill("#fMulai", rencana)
    page.fill("#fDesk", "Taman baca untuk anak SD.")
    page.click("#propSubmit")
    logout(page)
    login(page, "admin")
    nav(page, "Evaluasi proposal")
    page.locator(".review-card", has_text="Taman Baca Anak").locator("[data-approve]").click()
    open_project(page, "Taman Baca Anak")
    bulan = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"][d.month - 1]
    expect(page.locator("#detail .facts")).to_contain_text(f"{bulan} {d.year}")


# ---------- Tampilan ponsel ----------

def test_tampilan_ponsel_tanpa_gulir_horizontal(mobile_page):
    pg = mobile_page
    login(pg, "pj")
    for target in ["dashboard", "projects", "proposal", "project/2"]:
        pg.evaluate(f"location.hash='{target}'")
        pg.wait_for_timeout(100)
        overflow = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        assert overflow <= 1, f"Halaman {target} melebar {overflow}px di layar 390px"


def test_tampilan_ponsel_dengan_font_lebar(mobile_page):
    """Font di setiap komputer berbeda; paksa font yang lebar agar masalah tata letak ikut terlihat."""
    pg = mobile_page
    pg.add_style_tag(content="*{font-family:'DejaVu Sans',Verdana,sans-serif!important;letter-spacing:.02em}")
    login(pg, "pj")
    for target in ["dashboard", "projects", "proposal", "project/2", "profile"]:
        pg.evaluate(f"location.hash='{target}'")
        pg.wait_for_timeout(100)
        overflow = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        assert overflow <= 1, f"Halaman {target} melebar {overflow}px di layar 390px"
