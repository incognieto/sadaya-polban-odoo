# Sadaya Rutin - E-Purchasing (Standalone)

## Ringkas Modul
Sadaya Rutin adalah modul e-purchasing untuk belanja operasional rutin.
Modul ini berjalan mandiri (standalone) dan belum melakukan integrasi otomatis ke modul Sadaya lain.

Catatan UI:
- Admin memakai backend Odoo untuk membuat dan memproses paket.
- Vendor memakai portal untuk melihat paket yang sudah dipublikasikan, mengonfirmasi stok, dan mengirim penawaran harga.
- Paket dengan status `draft` hanya terlihat di backend admin.

## Akses Portal UI
- Dashboard: /sadaya-rutin atau /sadaya-rutin/dashboard
- Paket: /sadaya-rutin/paket
- Kontrak: /sadaya-rutin/kontrak
- Detail Paket: /sadaya-rutin/paket/<id>

## Model Utama
### Paket (sadaya_rutin.procurement_package)
Field inti:
- code, name, proposing_unit
- procurement_type, amount_total, currency_id
- start_date, end_date

Field alur kerja (tab):
- Data Permintaan: item_name, item_spec, item_qty, estimated_budget, request_notes
- Negosiasi: vendor_name, vendor_stock_confirmed, vendor_offer_notes, negotiation_price, negotiation_notes, negotiation_history, admin_counter_price, admin_review_notes
- SP: sp_number, sp_date, sp_signed_ppk, sp_signed_vendor
- Pengiriman: delivery_date, delivery_notes
- Pemeriksaan: inspection_status, inspection_notes, bast_number, bast_date, bast_signed_pphp, bast_signed_user, bast_signed_vendor
- Selesai: completion_notes

Aturan bisnis:
- delivery_date harus hari kerja (Senin-Jumat).
- requires_ppk aktif jika amount_total > 200000000.

### Kontrak (sadaya_rutin.contract)
Field inti:
- name, package_id, procurement_type
- officer_name, vendor_name
- hps_value, currency_id
- start_date, end_date

## Status Paket dan Tindakan
Status paket (Sadaya Rutin):
1. draft
2. negotiation_vendor
3. negotiation_pp
4. negotiation_done
5. negotiation_minutes
6. spk_preparation
7. spk_process
8. delivery
9. inspection
10. done
11. revision
12. addendum
13. cancelled

Tindakan status tersedia (backend):
- Kirim ke Vendor -> action_to_negotiation_vendor
- Terima Penawaran -> action_to_negotiation_done
- Counter Offer -> action_counter_offer
- Buat BA Negosiasi -> action_to_negotiation_minutes
- Persiapan SPK -> action_to_spk_preparation
- Proses SPK -> action_to_spk_process
- Pengiriman -> action_to_delivery
- Pemeriksaan -> action_to_inspection
- Selesaikan -> action_to_done
- Revisi -> action_set_revision
- Addendum -> action_set_addendum
- Batalkan -> action_cancel
- Kembalikan ke Draft -> action_reset_draft

Validasi minimum saat transisi:
- Draft/Revisi -> Negosiasi (Vendor): item_name, item_qty, estimated_budget, vendor_name wajib.
- Negosiasi (Vendor) -> Negosiasi (PP): vendor harus mengisi harga penawaran dan mengonfirmasi stok.
- Negosiasi (PP) -> Negosiasi (Vendor): admin melakukan counter-offer dan status kembali ke vendor.
- Negosiasi (PP) -> Terima Penawaran: negotiation_price wajib.
- Persiapan SPK -> Proses SPK: sp_number & sp_date wajib.
- Proses SPK -> Pengiriman: sp_signed_ppk & sp_signed_vendor wajib.
- Pengiriman -> Pemeriksaan: delivery_date wajib.
- Pemeriksaan -> Selesai: inspection_status harus "ok".

## Status Kontrak
Status kontrak:
- draft
- spk_preparation
- spk_process
- done
- revision
- addendum
- cancelled

## Integrasi Antar Modul (Rencana)
Modul ini disiapkan untuk integrasi, namun belum otomatis.
Integrasi yang direncanakan:
- Sinkronisasi data paket ke modul lain berdasarkan threshold nilai
- Notifikasi vendor dan TTE dokumen

## Catatan Pengembang
- Semua perubahan flow saat ini bersifat standalone.
- Jika akan integrasi, tambahkan dependensi modul terkait dan mapping field.
