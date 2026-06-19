# Modul sadaya_auth

Modul ini bertanggung jawab untuk menyimpan data seeding *users* (pengguna) dan *partners* awal sebagai dasar autentikasi di dalam Odoo untuk aplikasi Sadaya. Modul ini **tidak mengonfigurasi** *Access Control List* (ACL), *Record Rules*, atau *Groups* secara spesifik. Setiap modul lain yang memerlukan hak akses khusus harus mengatur grup dan aturan mereka sendiri dengan merujuk pada XML ID yang disediakan di bawah ini.

## Daftar Pengguna Seeding (Seeded Users)

Semua pengguna awal telah dibuat dalam tag `<data noupdate="1">` sehingga data tersebut tidak akan ter-reset saat modul ini diperbarui.

- **Format Password Default**: `[role]123`
- **Format Email Default**: `[nama].[role]@sadaya.example`

| Nama   | Peran / Role         | Login / Email                        | Password             | XML ID (Users)              | XML ID (Partner)              |
| ------ | -------------------- | ------------------------------------ | -------------------- | --------------------------- | ----------------------------- |
| John   | Admin Sistem         | john.admin@sadaya.example            | admin123             | `user_john_admin`           | `partner_john_admin`          |
| Jane   | Manajemen            | jane.manajemen@sadaya.example        | manajemen123         | `user_jane_manajemen`       | `partner_jane_manajemen`      |
| Smith  | PPK                  | smith.ppk@sadaya.example             | ppk123               | `user_smith_ppk`            | `partner_smith_ppk`           |
| Alice  | POKJA                | alice.pokja@sadaya.example           | pokja123             | `user_alice_pokja`          | `partner_alice_pokja`         |
| Bob    | Pejabat Pengadaan    | bob.pejabatpengadaan@sadaya.example  | pejabatpengadaan123  | `user_bob_pejabatpengadaan` | `partner_bob_pejabatpengadaan`|
| Arthur | Tim Teknis PPK       | arthur.timteknis@sadaya.example      | timteknis123         | `user_arthur_timteknis`     | `partner_arthur_timteknis`    |
| Dave   | Tim PPHP             | dave.pphp@sadaya.example             | pphp123              | `user_dave_pphp`            | `partner_dave_pphp`           |
| Eve    | User / Unit Kerja    | eve.unitkerja@sadaya.example         | unitkerja123         | `user_eve_unitkerja`        | `partner_eve_unitkerja`       |
| Trent  | Penyedia / Vendor    | trent.vendor@sadaya.example          | vendor123            | `user_trent_vendor`         | `partner_trent_vendor`        |
| Glory  | Penyedia / Vendor    | glory.vendor@sadaya.example          | vendor123            | `user_glory_vendor`         |

---

## Cara Merujuk XML ID pada Modul Lain

Jika Anda memegang modul lain dan ingin menambahkan *user* ini ke dalam *Groups* tertentu yang baru Anda buat, Anda bisa menggunakan `eval` atau `<record>` dengan mengaitkan relasi `many2many` grup tersebut ke *user* yang sudah ada. 

Karena XML ID di atas dibuat di modul `sadaya_auth`, Anda **wajib menggunakan prefix `sadaya_auth.`** di depan nama XML ID saat merujuknya dari modul Anda. Selain itu, pastikan modul Anda menambahkan `'sadaya_auth'` di bagian `depends` dalam file `__manifest__.py`.

### Contoh 1: Menambahkan *user* ke dalam *Group* menggunakan XML (`security.xml`)

Misalnya di modul `sadaya_lelang`, Anda membuat grup baru `group_lelang_pokja` dan ingin memasukkan **Alice** ke dalamnya:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <!-- Membuat Group Baru -->
        <record id="group_lelang_pokja" model="res.groups">
            <field name="name">Lelang POKJA</field>
            <field name="category_id" ref="base.module_category_hidden"/>
            
            <!-- Menambahkan user Alice dari modul sadaya_auth ke grup ini -->
            <field name="users" eval="[(4, ref('sadaya_auth.user_alice_pokja'))]"/>
        </record>
    </data>
</odoo>
```

### Contoh 2: Menambahkan banyak *user* sekaligus ke dalam *Group*

Jika Anda ingin menambahkan **Dave** (Tim PPHP) dan **Smith** (PPK) ke dalam grup yang sama, Anda bisa memanggil list `eval` dengan format operator `(4, ID)` secara berurutan:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data>
        <record id="group_viewer" model="res.groups">
            <field name="name">Viewer Mode</field>
            <field name="users" eval="[
                (4, ref('sadaya_auth.user_smith_ppk')),
                (4, ref('sadaya_auth.user_dave_pphp'))
            ]"/>
        </record>
    </data>
</odoo>
```

### Penjelasan Operator Relasi Many2Many `(4, ID)`

Dalam sistem Odoo, ketika Anda memberikan nilai ke field relasi `Many2many` (seperti field `users` pada model `res.groups`), Anda harus menggunakan format tuple operasi khusus. 

- `(4, ID)` berarti: **"Tambahkan *record* dengan ID tersebut ke dalam relasi ini tanpa menghapus relasi yang sudah ada sebelumnya."**

Beberapa pilihan operator relasi `Many2many` yang lain:
- `(3, ID)`: Hapus relasi dengan *record* ID tersebut, tetapi jangan hapus objek *record*-nya secara permanen.
- `(5, 0)`: Hapus semua relasi di dalam field ini (mengosongkan field many2many).
- `(6, 0, [ID1, ID2])`: Gantikan semua relasi yang ada saat ini dengan daftar ID baru yang diberikan di dalam list.

Dengan metode ini, konfigurasi dan hak akses mendalam di Odoo akan terjaga dengan rapi sesuai batasan tanggung jawab modul masing-masing!
