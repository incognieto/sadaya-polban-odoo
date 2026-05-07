# Troubleshooting Odoo Module (Sadaya Tender)

Dokumen ini merangkum penyebab umum error saat membuat custom module di Odoo, khususnya kasus module tidak muncul, gagal install, atau error saat dijalankan.

---

## Alasan Mengapa Terjadi Error

### 1. Nama XML ID tidak sesuai dengan nama modul

Odoo menggunakan format:

<module_name>.<xml_id>

Contoh benar:
```xml
<record id="sadaya_tender.list" model="ir.ui.view">
```

Jika nama modul:

sadaya_tender

Maka:

sadaya_tender.list   (benar)
si_qut.list          (salah)

Error yang muncul:

The ID "si_qut.list" refers to an uninstalled module

### 2. Tidak ada akses di security (menu tidak tampil)

Jika model tidak memiliki access control, maka menu tidak akan muncul di sidebar.

Contoh file:

id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sadaya_tender_sadaya_tender,sadaya_tender.sadaya_tender,model_sadaya_tender_sadaya_tender,base.group_user,1,1,1,1

Minimal agar menu muncul:

perm_read = 1

Tanpa access:

menu dibuat
action ada
tetapi tidak ditampilkan

### 3. Tidak menyertakan depends

Manifest harus menyertakan dependency:

'depends': ['base'],

Jika tidak, module bisa gagal load.

Contoh tambahan:

'depends': ['base', 'website']

### 4. Tidak menyertakan application=True

Jika ingin module tampil di Apps:

'application': True,

Jika tidak:

module tetap bisa diinstall
tetapi tidak muncul sebagai aplikasi

### 5. File disebut di manifest tapi tidak ada

Contoh:

'demo': [
    'demo/demo.xml',
],

Jika file tidak ada:

FileNotFoundError: demo/demo.xml

### 6. addons_path tidak valid (Docker)

Error:

invalid addons directory '/mnt/extra-addons'

Solusi:

pastikan volume Docker benar
folder benar-benar ada

### 7. Port Docker tidak sesuai

Default Odoo:

8069

Salah:

ports:
  - "8070:8070"

Benar:

ports:
  - "8070:8069"

### 8. Database belum diinisialisasi

Error:

relation "ir_module_module" does not exist

Artinya:

database belum dibuat
base module belum terinstall

### 9. Cache atau assets bermasalah

Error:

ERR_TOO_MANY_REDIRECTS

Solusi:

clear browser cache
restart container
disable test assets

### 10. Model tidak punya _description

Warning:

model has no _description

Tambahkan:

_description = 'Sadaya Tender'

## Insight Penting

Flow Odoo Backend
Menu
 ↓
Action (ir.actions.act_window)
 ↓
Model (res_model)
 ↓
Security (access rules)

Jika security gagal, maka menu tidak ditampilkan.

## Checklist Aman

- Nama module konsisten (sadaya_tender)
- XML ID sesuai (sadaya_tender.xxx)
- security/ir.model.access.csv ada
- depends benar
- application=True
- semua file di manifest ada
- docker port mapping benar
- addons_path valid

## Kesimpulan

Masalah paling sering terjadi bukan pada UI atau controller, melainkan pada konfigurasi security dan struktur module.