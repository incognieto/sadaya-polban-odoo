# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProcurementPackage(models.Model):
    _name = "sadaya_rutin.procurement_package"
    _description = "Sadaya Rutin Package"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    code = fields.Char(string="Kode Paket", tracking=True)
    name = fields.Char(string="Nama Paket", required=True, tracking=True)

    amount_total = fields.Monetary(
        string="Nilai",
        currency_field="currency_id",
        tracking=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id.id,
    )

    procurement_type = fields.Selection(
        [
            ("goods", "Barang"),
            ("services", "Jasa Lainnya"),
            ("construction", "Konstruksi"),
            ("consulting", "Jasa Konsultansi"),
        ],
        string="Jenis Pengadaan",
        required=True,
        tracking=True,
    )

    proposing_unit = fields.Char(string="Unit Pengusul", tracking=True)

    start_date = fields.Date(string="Tanggal Mulai", tracking=True)
    end_date = fields.Date(string="Tanggal Selesai", tracking=True)

    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("negotiation_vendor", "Negosiasi (Penyedia)"),
            ("negotiation_pp", "Negosiasi (PP)"),
            ("negotiation_done", "Negosiasi Selesai"),
            ("negotiation_minutes", "Proses Berita Acara Negosiasi"),
            ("spk_preparation", "Persiapan SPK"),
            ("spk_process", "Proses SPK"),
            ("delivery", "Pengiriman"),
            ("inspection", "Pemeriksaan"),
            ("done", "Selesai"),
            ("revision", "Revisi"),
            ("addendum", "Addendum SPK"),
            ("cancelled", "Batal"),
        ],
        string="Status Paket",
        default="draft",
        tracking=True,
    )

    # Flags untuk request dari portal vendor
    vendor_revision_requested = fields.Boolean(string="Vendor Request Revisi", default=False)
    vendor_cancellation_requested = fields.Boolean(string="Vendor Request Batal", default=False)

    # Tab 1 - Data Permintaan
    item_name = fields.Char(string="Nama Barang/Jasa")
    item_spec = fields.Text(string="Spesifikasi")
    item_qty = fields.Float(string="Jumlah")
    estimated_budget = fields.Monetary(
        string="Estimasi Anggaran",
        currency_field="currency_id",
    )
    request_notes = fields.Text(string="Catatan Permintaan")

    # Tab 2 - Negosiasi
    vendor_id = fields.Many2one("res.partner", string="Vendor")
    vendor_stock_confirmed = fields.Boolean(string="Stok Tersedia")
    vendor_offer_notes = fields.Text(string="Catatan Penawaran Vendor")
    negotiation_price = fields.Monetary(
        string="Harga Negosiasi",
        currency_field="currency_id",
    )
    negotiation_notes = fields.Text(string="Catatan Negosiasi")
    negotiation_history = fields.Text(string="Riwayat Tawar-Menawar")
    admin_counter_price = fields.Monetary(
        string="Harga Counter Admin",
        currency_field="currency_id",
    )
    admin_review_notes = fields.Text(string="Catatan Review Admin")
    ba_negotiation_file = fields.Binary(string="File BA Negosiasi (TTE)", attachment=True)
    ba_negotiation_filename = fields.Char(string="Nama File BA")

    # Tab 3 - Surat Pesanan (SP)
    sp_number = fields.Char(string="Nomor Surat Pesanan")
    sp_date = fields.Date(string="Tanggal Surat Pesanan")
    sp_signed_ppk = fields.Boolean(string="TTE PPK")
    sp_signed_vendor = fields.Boolean(string="TTE Vendor (SP)")
    sp_signed_file = fields.Binary(string="File SPK/Kontrak (TTE)", attachment=True)
    sp_signed_filename = fields.Char(string="Nama File SPK")

    # Tab 4 - Pengiriman
    delivery_date = fields.Date(string="Tanggal Pengiriman")
    delivery_notes = fields.Text(string="Catatan Pengiriman")

    # Tab 5 - Pemeriksaan & Serah Terima
    inspection_status = fields.Selection(
        [
            ("ok", "Sesuai Spek"),
            ("not_ok", "Tidak Sesuai"),
        ],
        string="Hasil Pemeriksaan",
    )
    inspection_notes = fields.Text(string="Catatan Pemeriksaan")
    bast_number = fields.Char(string="Nomor BAST")
    bast_date = fields.Date(string="Tanggal BAST")
    bast_signed_pphp = fields.Boolean(string="TTE Tim Teknis/PPHP")
    bast_signed_user = fields.Boolean(string="TTE User")
    bast_signed_vendor = fields.Boolean(string="TTE Vendor (BAST)")

    # Tab 6 - Selesai
    completion_notes = fields.Text(string="Catatan Penyelesaian")

    requires_ppk = fields.Boolean(
        string="Butuh PPK (> 200 Juta)",
        compute="_compute_requires_ppk",
    )

    contract_ids = fields.One2many(
        "sadaya_rutin.contract",
        "package_id",
        string="Kontrak",
    )

    contract_count = fields.Integer(compute="_compute_contract_count")

    @api.depends("amount_total")
    def _compute_requires_ppk(self):
        for rec in self:
            rec.requires_ppk = (rec.amount_total or 0.0) > 200000000.0

    @api.constrains("delivery_date")
    def _check_delivery_weekday(self):
        for rec in self:
            if rec.delivery_date and rec.delivery_date.weekday() >= 5:
                raise ValidationError(
                    "Pengiriman hanya dapat dijadwalkan pada hari kerja (Senin-Jumat)."
                )

    @api.depends("contract_ids")
    def _compute_contract_count(self):
        for rec in self:
            rec.contract_count = len(rec.contract_ids)

    def _ensure_status(self, allowed):
        for rec in self:
            if rec.status not in allowed:
                raise ValidationError("Status paket tidak sesuai untuk tindakan ini.")

    def _ensure_required(self, fields_map):
        for rec in self:
            missing = [label for label, value in fields_map.items() if not value]
            if missing:
                raise ValidationError(
                    "Field wajib belum lengkap: %s" % ", ".join(missing)
                )

    def action_to_negotiation_vendor(self):
        self._ensure_status(["draft", "revision"])
        for rec in self:
            rec._ensure_required(
                {
                    "Nama Barang/Jasa": rec.item_name,
                    "Jumlah": rec.item_qty,
                    "Estimasi Anggaran": rec.estimated_budget,
                    "Vendor": rec.vendor_id,
                }
            )
            rec.status = "negotiation_vendor"

    def action_vendor_submit_offer(self):
        self._ensure_status(["negotiation_vendor"])
        for rec in self:
            rec._ensure_required(
                {
                    "Vendor": rec.vendor_id,
                    "Harga Negosiasi": rec.negotiation_price,
                }
            )
            if not rec.vendor_stock_confirmed:
                raise ValidationError("Vendor harus mengonfirmasi stok tersedia sebelum mengirim penawaran.")
            history_line = "Vendor menawar Rp %s dan stok tersedia." % rec.negotiation_price
            rec.negotiation_history = "\n".join(
                [line for line in [rec.negotiation_history, history_line] if line]
            )
            rec.status = "negotiation_pp"

    def _clear_progress_fields(self, keep_inspection=False):
        """Reset progres field saat status berubah ke Revisi atau Draft.

        Args:
            keep_inspection (bool): Jika True, field hasil pemeriksaan
                (inspection_status & inspection_notes) TIDAK dihapus.
                Gunakan True saat Revisi karena catatan ketidaksesuaian
                harus tetap tersimpan sebagai referensi vendor.
        """
        for rec in self:
            rec.vendor_stock_confirmed = False
            rec.sp_signed_ppk = False
            rec.sp_signed_vendor = False
            rec.ba_negotiation_file = False
            rec.ba_negotiation_filename = False
            rec.sp_signed_file = False
            rec.sp_signed_filename = False
            rec.delivery_date = False
            rec.delivery_notes = False
            rec.vendor_cancellation_requested = False
            rec.vendor_revision_requested = False
            if not keep_inspection:
                rec.inspection_status = False
                rec.inspection_notes = False

    def action_vendor_reject_offer(self):
        self._ensure_status(["negotiation_vendor"])
        for rec in self:
            history_line = "Vendor menolak permintaan / stok habis."
            if rec.vendor_offer_notes:
                history_line += " Alasan: %s" % rec.vendor_offer_notes
            rec.negotiation_history = "\n".join(
                [line for line in [rec.negotiation_history, history_line] if line]
            )
            rec.status = "revision"
            rec.vendor_revision_requested = False
            rec.vendor_cancellation_requested = False
            rec._clear_progress_fields()

    def action_approve_vendor_revision(self):
        """Disetujui oleh internal setelah vendor request revisi"""
        self._ensure_status(["inspection"])
        self.message_post(body="Tim Teknis / PP menyetujui permintaan Revisi dari Vendor.")
        self.action_set_revision()

    def action_approve_vendor_cancellation(self):
        """Disetujui oleh internal setelah vendor request batal"""
        self._ensure_status(["inspection"])
        self.message_post(body="Tim Teknis / PP menyetujui permintaan Pembatalan dari Vendor.")
        self.action_cancel()

    def action_to_negotiation_done(self):
        self._ensure_status(["negotiation_pp"])
        for rec in self:
            rec._ensure_required({"Harga Negosiasi": rec.negotiation_price})
            rec.status = "negotiation_done"

    def action_counter_offer(self):
        self._ensure_status(["negotiation_pp"])
        for rec in self:
            rec._ensure_required({"Harga Counter Admin": rec.admin_counter_price})
            rec.negotiation_price = rec.admin_counter_price
            history_line = "Admin melakukan counter offer Rp %s." % rec.admin_counter_price
            rec.negotiation_history = "\n".join(
                [line for line in [rec.negotiation_history, history_line] if line]
            )
            rec.status = "negotiation_vendor"

    def action_to_negotiation_minutes(self):
        self._ensure_status(["negotiation_done"])
        for rec in self:
            rec.status = "negotiation_minutes"

    def action_to_spk_preparation(self):
        self._ensure_status(["negotiation_minutes"])
        for rec in self:
            if not rec.ba_negotiation_file:
                raise ValidationError("Harap unggah File BA Negosiasi yang sudah di-TTE sebelum melanjutkan ke Persiapan SPK.")
            rec.status = "spk_preparation"

    def action_to_spk_process(self):
        self._ensure_status(["spk_preparation"])
        for rec in self:
            rec._ensure_required({"Nomor SP": rec.sp_number, "Tanggal SP": rec.sp_date})
            rec.status = "spk_process"

    def action_to_delivery(self):
        self._ensure_status(["spk_process"])
        for rec in self:
            if not (rec.sp_signed_ppk and rec.sp_signed_vendor):
                raise ValidationError("Harap centang konfirmasi TTE PPK dan TTE Vendor (SP) sebelum melanjutkan.")
            if not rec.sp_signed_file:
                raise ValidationError("Harap unggah File SPK/Kontrak final yang sudah di-TTE kedua belah pihak sebelum masuk ke tahap Pengiriman.")
            rec.status = "delivery"

    def action_to_inspection(self):
        self._ensure_status(["delivery"])
        for rec in self:
            rec._ensure_required({"Tanggal Pengiriman": rec.delivery_date})
            rec.status = "inspection"

    def action_to_done(self):
        self._ensure_status(["inspection"])
        for rec in self:
            if rec.inspection_status != "ok":
                raise ValidationError("Hasil pemeriksaan belum sesuai spek.")
            rec.status = "done"

    def action_set_revision(self):
        self._ensure_status([
            "negotiation_vendor",
            "negotiation_pp",
            "negotiation_done",
            "negotiation_minutes",
            "spk_preparation",
            "spk_process",
            "delivery",
            "inspection",
        ])
        for rec in self:
            # Catat catatan pemeriksaan ke chatter sebelum status berubah
            # agar riwayat ketidaksesuaian tidak hilang dan dapat dilihat semua pihak
            if rec.inspection_status == 'not_ok' and rec.inspection_notes:
                rec.message_post(
                    body=(
                        "<b>⚠️ Revisi: Barang Tidak Sesuai Spek</b><br/>"
                        "Hasil pemeriksaan: <b>Tidak Sesuai</b><br/>"
                        "Catatan ketidaksesuaian:<br/>%s" % rec.inspection_notes
                    ),
                    message_type='comment',
                    subtype_xmlid='mail.mt_note',
                )
            rec.status = "revision"
            # keep_inspection=True: catatan pemeriksaan tetap tersimpan di field
            # agar Tim Teknis tidak perlu mengetik ulang saat barang pengganti tiba
            rec._clear_progress_fields(keep_inspection=True)

    def action_set_addendum(self):
        self._ensure_status(["spk_process", "done"])
        for rec in self:
            rec.status = "addendum"

    def action_cancel(self):
        self._ensure_status([
            "draft",
            "negotiation_vendor",
            "negotiation_pp",
            "negotiation_done",
            "negotiation_minutes",
            "spk_preparation",
            "spk_process",
            "delivery",
            "inspection",
            "revision",
            "addendum",
        ])
        for rec in self:
            rec.status = "cancelled"

    def action_reset_draft(self):
        self._ensure_status(["revision", "cancelled"])
        for rec in self:
            rec.status = "draft"
            # Saat reset ke draft: hapus SEMUA termasuk catatan pemeriksaan lama
            rec._clear_progress_fields(keep_inspection=False)

    def action_notify_vendor_rejection(self):
        """Simpan catatan ketidaksesuaian & kirim notifikasi ke vendor via portal chatter.

        Method ini dipanggil oleh tombol "Simpan & Kirim Notifikasi ke Vendor"
        di Tab Pemeriksaan. Tidak memerlukan klik Save manual di header karena
        Odoo akan auto-save field form sebelum eksekusi method ini melalui
        mekanisme type="object" pada tombol.
        """
        self.ensure_one()
        self._ensure_status(['inspection'])

        if self.inspection_status != 'not_ok':
            raise ValidationError(
                "Notifikasi hanya bisa dikirim saat hasil pemeriksaan adalah 'Tidak Sesuai'."
            )
        if not self.inspection_notes:
            raise ValidationError(
                "Harap isi Catatan Pemeriksaan terlebih dahulu sebelum mengirim notifikasi ke vendor."
            )

        # Bangun pesan yang jelas dan informatif untuk vendor
        vendor_name = self.vendor_id.name if self.vendor_id else 'Vendor'
        body = (
            "<p><b>⚠️ Pemberitahuan Ketidaksesuaian Barang/Jasa</b></p>"
            "<p>Kepada <b>%s</b>,</p>"
            "<p>Tim Teknis telah melakukan pemeriksaan terhadap barang/jasa yang dikirimkan "
            "untuk paket <b>%s</b> dan menemukan ketidaksesuaian dengan spesifikasi yang disepakati.</p>"
            "<p><b>Catatan Ketidaksesuaian:</b><br/>%s</p>"
            "<p>Mohon segera menghubungi pihak kami untuk tindak lanjut pengembalian dan pengiriman "
            "barang/jasa pengganti yang sesuai spesifikasi.</p>"
        ) % (
            vendor_name,
            self.name or self.code or '-',
            self.inspection_notes.replace('\n', '<br/>'),
        )

        # Kirim sebagai 'comment' (bukan 'note') agar pesan muncul di portal vendor
        self.message_post(
            body=body,
            message_type='comment',
            subtype_xmlid='mail.mt_comment',
            partner_ids=self.vendor_id.ids if self.vendor_id else [],
        )

        # Tampilkan notifikasi sukses di UI
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Notifikasi Terkirim',
                'message': 'Catatan ketidaksesuaian telah disimpan dan notifikasi berhasil dikirim ke %s.' % vendor_name,
                'type': 'success',
                'sticky': False,
            },
        }

    def action_print_ba_negotiation(self):
        self.ensure_one()
        return self.env.ref('sadaya_rutin.action_report_ba_negotiation').report_action(self)
