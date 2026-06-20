# RBAC Sadaya Rutin — Panduan Implementasi Kontrol Akses

Dokumen ini menjelaskan implementasi **Role-Based Access Control (RBAC)** pada modul `sadaya_rutin`, mencakup siapa saja pemangku kepentingan, hak akses apa yang dimiliki setiap peran, dan bagaimana implementasinya dilakukan secara teknis.

---

## 1. Pemangku Kepentingan (Stakeholders)

Berdasarkan proses bisnis pengadaan rutin (e-purchasing < Rp50 juta), terdapat lima peran internal yang berinteraksi dengan modul ini di sisi *backend* Odoo, serta satu peran eksternal yang mengakses melalui *portal web*.

| Peran | Nama Dummy | Email Dummy | Akses |
|---|---|---|---|
| **PP (Pejabat Pengadaan)** | Bob | bob.pejabatpengadaan@sadaya.example | Backend - Kendali Penuh |
| **PPK (Pejabat Pembuat Komitmen)** | Smith | smith.ppk@sadaya.example | Backend - Review & Write |
| **Tim Teknis PPK** | Arthur | arthur.timteknis@sadaya.example | Backend - Pemeriksaan |
| **PPHP (Penerima Hasil Pekerjaan)** | Dave | dave.pphp@sadaya.example | Backend - Serah Terima |
| **Unit Kerja / Pemohon** | Eve | eve.unitkerja@sadaya.example | Backend - Pantau (Read Only) |
| **Vendor / Penyedia** | Trent, Glory | trent/glory.vendor@sadaya.example | Portal Web (bukan backend) |

> **Catatan:** Akun John (Admin Sistem) dan Jane (Manajemen) memiliki akses Odoo Administrator (`base.group_system`) yang secara otomatis melewati semua batasan RBAC dan bisa mengakses seluruh sistem.

---

## 2. Matriks Hak Akses

### 2A. Hak Akses Model (CRUD)

| Peran | Paket (Create) | Paket (Read) | Paket (Write) | Paket (Delete) | Kontrak (Create) | Kontrak (Read) | Kontrak (Write) | Kontrak (Delete) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **PP** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **PPK** | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ |
| **Tim Teknis** | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **PPHP** | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Unit Kerja** | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Vendor (Portal)** | ❌ | ✅* | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

> *Vendor hanya bisa membaca paket yang secara eksplisit ditujukan kepada mereka (dikontrol oleh *Record Rule*).

### 2B. Siapa yang Bisa Melakukan Apa (Per Tahapan Alur Kerja)

| Aksi / Tahapan | PP | PPK | Tim Teknis | PPHP | Unit Kerja |
|---|:---:|:---:|:---:|:---:|:---:|
| Buat Paket Baru | ✅ | ❌ | ❌ | ❌ | ❌ |
| Edit Data Permintaan | ✅ | ✅ | ❌ | ❌ | ❌ |
| Kirim ke Vendor (Negosiasi) | ✅ | ❌ | ❌ | ❌ | ❌ |
| Terima / Counter Penawaran | ✅ | ✅ | ❌ | ❌ | ❌ |
| Buat BA Negosiasi (PDF) | ✅ | ✅ | ❌ | ❌ | ❌ |
| Input Nomor & Tanggal SPK | ✅ | ✅ | ❌ | ❌ | ❌ |
| Centang TTE PPK/Vendor | ✅ | ✅ | ❌ | ❌ | ❌ |
| Terima Jadwal Pengiriman | ✅ | ❌ | ❌ | ❌ | ❌ |
| Catat Hasil Pemeriksaan | ✅ | ❌ | ✅ | ✅ | ❌ |
| Isi Nomor & Tanggal BAST | ✅ | ❌ | ❌ | ✅ | ❌ |
| Selesaikan / Batalkan Paket | ✅ | ❌ | ❌ | ❌ | ❌ |
| Pantau Status Paket | ✅ | ✅ | ✅ | ✅ | ✅ |

---

## 3. Implementasi Teknis

### 3A. Struktur File yang Dimodifikasi

```
sadaya_rutin/
├── __manifest__.py          ← Ditambahkan: "sadaya_auth" di depends
└── security/
    ├── security.xml         ← Didefinisikan: Grup + Record Rules
    └── ir.model.access.csv  ← Didefinisikan: Hak CRUD per grup
```

### 3B. `__manifest__.py` — Menambahkan Dependensi

Agar baris `ref('sadaya_auth.user_bob_pejabatpengadaan')` dan seterusnya tidak error saat upgrade, modul `sadaya_auth` wajib didefinisikan sebagai dependensi:

```python
"depends": [
    "base",
    "mail",
    "website",
    "sadaya_auth",   # ← WAJIB: agar akun dummy dari sadaya_auth sudah ada duluan
],
```

### 3C. `security/security.xml` — Mendefinisikan Grup & Record Rules

**Pola pembuatan grup dan assignment user:**

```xml
<record id="group_rutin_pp" model="res.groups">
    <field name="name">PP - Pejabat Pengadaan Rutin</field>
    <!-- (4, id) = Tambahkan user ini ke grup (tanpa menghapus yang lain) -->
    <field name="users" eval="[(4, ref('sadaya_auth.user_bob_pejabatpengadaan'))]"/>
</record>
```

**Record Rule untuk Vendor Portal:**

```xml
<record id="rule_rutin_vendor_paket_sendiri" model="ir.rule">
    <field name="name">Rutin: Vendor Hanya Lihat Paket Sendiri</field>
    <field name="model_id" ref="model_sadaya_rutin_procurement_package"/>
    <field name="groups" eval="[(4, ref('base.group_portal'))]"/>
    <!-- Domain: hanya tampilkan paket yang field vendor_id-nya mengandung user yang sedang login -->
    <field name="domain_force">[('vendor_id.user_ids', 'in', [user.id])]</field>
    <field name="perm_read">1</field>
    <field name="perm_write">0</field>
    <field name="perm_create">0</field>
    <field name="perm_unlink">0</field>
</record>
```

### 3D. `security/ir.model.access.csv` — Hak CRUD per Grup

Format setiap baris: `id, nama, model, grup, read, write, create, delete`

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_rutin_pkg_pp,Paket Rutin - PP,model_sadaya_rutin_procurement_package,sadaya_rutin.group_rutin_pp,1,1,1,1
access_rutin_pkg_ppk,Paket Rutin - PPK,model_sadaya_rutin_procurement_package,sadaya_rutin.group_rutin_ppk,1,1,0,0
access_rutin_pkg_timteknis,Paket Rutin - Tim Teknis,model_sadaya_rutin_procurement_package,sadaya_rutin.group_rutin_tim_teknis,1,1,0,0
access_rutin_pkg_pphp,Paket Rutin - PPHP,model_sadaya_rutin_procurement_package,sadaya_rutin.group_rutin_pphp,1,1,0,0
access_rutin_pkg_unitkerja,Paket Rutin - Unit Kerja,model_sadaya_rutin_procurement_package,sadaya_rutin.group_rutin_unit_kerja,1,0,0,0
```

> **Mengapa Tim Teknis dan PPHP mendapat `perm_write=1` di model Paket?**
> Karena mereka perlu mengisi field pemeriksaan (`inspection_status`, `inspection_notes`, `bast_number`, dll.) yang ada di dalam model yang sama (`sadaya_rutin.procurement_package`). Pembatasan pada *field* mana yang bisa mereka edit lebih tepat dilakukan di level view XML (atribut `readonly`), bukan di level model.

---

## 4. Cara Menguji RBAC

Setelah melakukan upgrade modul, uji dengan login menggunakan akun berikut:

### Skenario 1: Uji Unit Kerja (Eve)
1. Login sebagai `eve.unitkerja@sadaya.example` / `unitkerja123`
2. Buka modul Sadaya Rutin di backend.
3. **Yang diharapkan:** Bisa melihat daftar paket, tapi tombol **Buat** (Create) dan **Hapus** (Delete) tidak muncul. Form paket tampil dalam mode *read-only*.

### Skenario 2: Uji Tim Teknis (Arthur)
1. Login sebagai `arthur.timteknis@sadaya.example` / `timteknis123`
2. Buka paket yang sedang di status **Pemeriksaan**.
3. **Yang diharapkan:** Bisa mengisi field `inspection_status` dan `inspection_notes`. Tapi tidak bisa membuat paket baru.

### Skenario 3: Uji Vendor (Trent di Portal)
1. Login sebagai `trent.vendor@sadaya.example` / `vendor123`
2. Buka `http://localhost:8069/sadaya-rutin/paket`
3. **Yang diharapkan:** Hanya paket yang `vendor_id` = Trent yang muncul. Paket milik Glory tidak terlihat sama sekali.

### Skenario 4: Uji PP (Bob)
1. Login sebagai `bob.pejabatpengadaan@sadaya.example` / `pejabatpengadaan123`
2. **Yang diharapkan:** Akses penuh — bisa buat, edit, hapus paket, dan menjalankan semua transisi status.

---

## 5. Catatan Pengembang

- **Kenapa `noupdate="0"`?** Agar saat pengembangan, setiap `docker-compose run ... -u sadaya_rutin` akan selalu me-*refresh* assignment user ke grup. Ubah ke `noupdate="1"` di lingkungan produksi.
- **Vendor tidak butuh backend access.** Semua interaksi vendor sudah dikelola oleh controller portal (`controllers/`) menggunakan `sudo()` dengan pengecekan eksplisit identitas user di Python. Record Rule di atas menambahkan lapisan keamanan tambahan di level *database query*.
- **RBAC di level *field*** (misalnya membatasi Arthur agar hanya bisa edit tab Pemeriksaan) harus dilakukan dengan atribut `groups` atau `readonly` pada elemen `<field>` di view XML (`views/procurement_package_views.xml`), bukan di file security ini.
