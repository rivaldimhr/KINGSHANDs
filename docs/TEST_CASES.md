# Test case: King's Hand (versi web)

Semua skenario di bawah dijalankan otomatis oleh `tests/web/test_web.py` (25 test) (Playwright + pytest) di setiap push lewat GitHub Actions. Setiap test memakai browser baru, sehingga data contoh selalu mulai dari kondisi awal. Selain hasil yang diharapkan, setiap test juga gagal bila muncul error JavaScript di halaman.

Akun demo: penanggung jawab (PJ) `demo@kingshand.id` / `demo123`, admin `admin@kingshand.id` / `admin123`.

## Login dan hak akses

| ID | Skenario | Langkah | Hasil yang diharapkan | Test otomatis |
|---|---|---|---|---|
| TC-01 | Kata sandi salah | Isi email PJ dan kata sandi "salah", klik Masuk | Pesan "Email atau kata sandi salah" muncul, aplikasi tidak terbuka | `test_login_gagal_dengan_kata_sandi_salah` |
| TC-02 | Tombol akun demo | Klik kartu "Admin lembaga" | Email dan kata sandi admin terisi | `test_tombol_akun_demo_mengisi_form` |
| TC-03 | Menu sesuai peran | Masuk sebagai PJ, keluar, lalu masuk sebagai admin | PJ melihat menu Proposal dan Profil; admin melihat Evaluasi proposal dan Laporan masuk, tanpa Profil | `test_menu_berbeda_untuk_tiap_peran` |
| TC-04 | Admin membuka halaman PJ lewat URL | Sebagai admin, buka `#proposal` | Dialihkan ke Dashboard | `test_admin_tidak_bisa_membuka_halaman_khusus_pj` |

## Proposal

| ID | Skenario | Langkah | Hasil yang diharapkan | Test otomatis |
|---|---|---|---|---|
| TC-05 | Form tidak lengkap | Isi judul saja, klik Ajukan | Pesan "Lengkapi semua kolom" | `test_proposal_wajib_lengkap` |
| TC-06 | Alur persetujuan | PJ mengajukan proposal → admin menyetujui dengan catatan → PJ masuk lagi | Status proposal di PJ "Menunggu persetujuan". Admin melihat lampirannya. Setelah disetujui, PJ menerima notifikasi, proyek berstatus Aktif, dan form laporan tersedia | `test_proposal_disetujui_admin_menjadi_proyek_aktif` |
| TC-07 | Penolakan | Admin klik Tolak tanpa catatan, lalu dengan catatan | Tanpa catatan: muncul pesan wajib alasan. Dengan catatan: PJ melihat status "Ditolak" beserta alasannya, dan proyek hilang dari daftar | `test_penolakan_wajib_ada_alasan_dan_sampai_ke_pj` |
| TC-08 | Penghitung menu admin | Admin menyetujui satu dari dua proposal | Angka pada menu Evaluasi proposal turun dari 2 ke 1 | `test_penghitung_menu_admin_berkurang` |

## Peringatan otomatis

Aturan: (a) dana terpakai (% anggaran) melebihi progres pekerjaan ≥ 15 poin; (b) laporan perkembangan terakhir lebih dari 30 hari; (c) ada laporan berstatus "Perlu revisi".

| ID | Skenario | Langkah | Hasil yang diharapkan | Test otomatis |
|---|---|---|---|---|
| TC-09 | Peringatan awal | Masuk sebagai PJ | "Perlu perhatian (2)": Klinik Desa Sukamaju (dana 83% vs progres 66%) dan SLB Papua (laporan 45 hari lalu) | `test_peringatan_awal_muncul_di_dashboard` |
| TC-10 | Filter "Perlu perhatian" | Admin klik kartu "Proyek perlu perhatian" | Daftar proyek hanya berisi 2 proyek | `test_filter_perlu_perhatian` |
| TC-11 | Peringatan hilang setelah melapor | PJ mengirim laporan perkembangan SLB Papua dengan progres 60% | Peringatan "terlambat" hilang, progres menjadi 60%, status laporan "Menunggu diperiksa" | `test_kirim_laporan_menghapus_peringatan_terlambat` |
| TC-12 | Laporan keuangan memicu peringatan | PJ melaporkan dana terpakai Rp 450 juta untuk Cafe (anggaran Rp 500 juta, progres 63%) | Muncul "Dana terpakai 90% dari anggaran, progres pekerjaan baru 63%" | `test_laporan_keuangan_bisa_memicu_peringatan_dana` |
| TC-13 | Validasi form laporan | Kirim tanpa file, progres 120%, lalu progres lebih kecil dari sebelumnya | Pesan berturut-turut: pilih file, nilai antara 0 dan 100, progres tidak boleh turun | `test_validasi_form_laporan` |

## Pemeriksaan laporan (admin)

| ID | Skenario | Langkah | Hasil yang diharapkan | Test otomatis |
|---|---|---|---|---|
| TC-14 | Menerima laporan | Admin klik Terima pada laporan Bank Sampah | Laporan pindah ke "Sudah diperiksa"; PJ menerima notifikasi | `test_admin_menerima_laporan_dan_pj_diberi_tahu` |
| TC-15 | Meminta revisi | Admin klik Minta revisi tanpa catatan, lalu dengan catatan | Tanpa catatan: muncul pesan wajib. Dengan catatan: PJ melihat peringatan "perlu revisi" beserta catatannya | `test_minta_revisi_wajib_catatan_dan_menjadi_peringatan` |

## Profil, notifikasi, data

| ID | Skenario | Langkah | Hasil yang diharapkan | Test otomatis |
|---|---|---|---|---|
| TC-16 | Ubah profil | Ubah nama menjadi "Rina Sari", simpan | Sapaan di dashboard menjadi "Halo, Rina" | `test_ubah_profil` |
| TC-17 | Email tidak valid | Ubah email menjadi "bukan-email", simpan | Pesan validasi email | `test_profil_menolak_email_tidak_valid` |
| TC-18 | Notifikasi dibaca | Klik ikon lonceng | Panel terbuka, penanda jumlah belum dibaca hilang | `test_membuka_notifikasi_menandai_sudah_dibaca` |
| TC-19 | Data tersimpan dan reset | Ajukan proposal, muat ulang halaman, lalu klik Reset data | Proposal masih ada setelah dimuat ulang, lalu hilang setelah reset | `test_data_tersimpan_setelah_muat_ulang_dan_bisa_direset` |
| TC-20 | Tampilan ponsel | Buka dashboard, proyek, proposal, dan detail di layar 390 px | Tidak ada halaman yang melebar hingga perlu digulir ke samping | `test_tampilan_ponsel_tanpa_gulir_horizontal` |
| TC-21 | Ponsel dengan font lebar | Seperti TC-20, tetapi font dipaksa ke font yang lebih lebar (font tiap perangkat berbeda) | Tidak ada halaman yang melebar. Test ini ditambahkan setelah CI menemukan halaman Proposal melebar 18 px | `test_tampilan_ponsel_dengan_font_lebar` |

## Regresi: bug dari pengujian eksploratif

Ditemukan saat pengujian eksploratif ([laporan bug](https://github.com/rivaldimhr/qa-automation-portfolio/blob/main/docs/bug-reports.md)), diperbaiki, lalu dijaga test ini. Setiap test sudah dicek gagal di versi sebelum perbaikan.

| ID | Bug | Langkah | Hasil yang diharapkan | Test otomatis |
|---|---|---|---|---|
| TC-22 | BUG-01 | PJ melaporkan progres 95%, admin minta revisi, PJ mengirim koreksi 70% | Koreksi diterima dan progres menjadi 70%. Nilai di bawah progres yang sudah diterima (63%) tetap ditolak | `test_progres_bisa_dikoreksi_setelah_diminta_revisi` |
| TC-23 | BUG-02 | Admin minta revisi laporan Bank Sampah, PJ mengirim laporan pengganti | Peringatan "perlu revisi" hilang; laporan lama berstatus "Diganti laporan baru" | `test_peringatan_revisi_hilang_setelah_laporan_diganti` |
| TC-24 | BUG-03 | Bank Sampah (anggaran Rp 120 juta): progres 100%, dana terpakai Rp 130 juta | Peringatan "Dana terpakai melebihi anggaran" (108%) | `test_dana_melebihi_anggaran_memicu_peringatan` |
| TC-25 | BUG-04 | PJ mengajukan proposal dengan rencana mulai 3 bulan lagi, admin menyetujui | Bulan mulai proyek tetap sesuai rencana | `test_persetujuan_mempertahankan_rencana_mulai` |

## Menjalankan sendiri

```bash
pip install pytest playwright
python -m playwright install chromium
python -m pytest tests/web -v
```
