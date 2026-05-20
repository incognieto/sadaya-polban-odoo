# Sadaya Lelang Module - Procurement & Tendering System

## Module Overview

**Sadaya Lelang** is a comprehensive Odoo custom module for managing government procurement processes following the **SPSE (Sistem Pengadaan Secara Elektronik)** style. It implements the complete workflow for procurement/tender management in Indonesian institutions, specifically designed for Politeknik Negeri Bandung.

### Key Information
- **Module Name**: sadaya_lelang
- **Category**: Operations/Purchase
- **Version**: 1.0
- **Application Type**: Web-based procurement management
- **Dependencies**: base, mail, portal

---

## Business Context

This module implements the Indonesian government procurement process, commonly referred to as SPSE (Electronic Procurement System). It's designed for:

- **Government Institutions** (like Politeknik Negeri Bandung)
- **Large-value Procurement Projects** (typically Rp200M+)
- **Transparent & Fair Vendor Selection** with multiple evaluation stages
- **Compliance with Government Regulations** (e.g., LKPP guidelines)

---

## Workflow & Business Process

### Complete Procurement Lifecycle (12 Stages)

The module manages the entire procurement journey with these sequential stages:

1. **Persiapan Lelang (POKJA)** - Procurement Committee preparation
   - Define procurement needs and specifications
   - Prepare tender documents and technical requirements
   - Conduct market surveys to determine HPS (Harga Perkiraan Sendiri)

2. **Pengumuman Lelang** - Public announcement
   - Announce tender to eligible vendors
   - Provide access to tender documents
   - Publicize timeline and requirements

3. **Pendaftaran & Penawaran** - Registration & bidding
   - Vendors register and submit qualifications
   - Vendors submit price and technical offers
   - Auto-numbered proposal documents for traceability

4. **Evaluasi & Pembuktian** - Evaluation & verification
   - Evaluate vendor qualifications (administrative)
   - Evaluate technical proposals
   - Score price proposals relative to HPS
   - Verification of claims and capabilities

5. **Laporan Hasil Lelang** - Auction result report
   - Publish evaluation results
   - Announce winner selection
   - Provide appeal/protest period

6. **SPPBJ** - Procurement letter of intent
   - Issue official procurement letter to winner
   - Communicate contract terms

7. **Jaminan Pelaksanaan** - Performance bond
   - Winner uploads performance bond documentation
   - Verify bond authenticity

8. **Tanda Tangan Kontrak** - Contract signing
   - Official contract agreement between institution and vendor
   - Digital or physical signatures

9. **Pelaksanaan Pekerjaan** - Work execution
   - Vendor performs goods/services delivery
   - Progress monitoring and compliance checks

10. **Serah Terima (BAST)** - Handover/acceptance
    - Goods/services inspection and acceptance
    - Final documentation of delivery

11. **Selesai** - Completed
    - Project closure and archival
    - Final payments processed

12. **Dibatalkan** - Cancelled (alternate state)
    - Procurement cancelled by management decision

---

## Core Data Models

### 1. **SadayaLelangPaket** (Procurement Package)
**Purpose**: Main package representing a complete procurement project

**Key Fields**:
- `name` - Package/tender name (e.g., "Pengadaan Laptop 2026")
- `kode_tender` - Auto-generated unique tender code (sequence-based)
- `description` - Short procurement description
- `hps` (Harga Perkiraan Sendiri) - Government's estimated price
- `status` - Current workflow stage (12-stage lifecycle)
- `metode_pemilihan` - Selection method: Tender or Seleksi (Selection)
- `currency_id` - Currency for all financial values (linked to company currency)

**Role Assignment Fields** (SOP-based):
- `user_id` - USER/Pemohon (Requestor) - initiates procurement
- `manajemen_id` - MANAJEMEN/Approver - approves procurement needs
- `ppk_id` - PPK (Project Control Official) - supervises entire process
- `pokja_id` - POKJA (Procurement Committee) - evaluates and recommends
- `pphp_id` - PPHP (Procurement Supervisory) - verifies compliance

**Document Upload Fields** (SOP workflow documents):
- `file_kebutuhan` - Requirements document (justification for procurement)
- `file_disposisi` - Management approval/disposition
- `file_sppbj` - Official procurement letter
- `file_kontrak` - Contract document
- `file_jaminan_pelaksanaan` - Performance bond (from vendor)
- `file_bast` - Handover/acceptance document

**Relationships**:
- `jadwal_ids` (One2Many) → Schedule for each procurement stage
- `dokumen_ids` (One2Many) → Tender documents (specs, requirements)
- `penawaran_ids` (One2Many) → Vendor proposals/offers

### 2. **SadayaLelangJadwal** (Procurement Schedule)
**Purpose**: Timeline for each stage within a procurement package

**Key Fields**:
- `name` - Stage name (e.g., "Pendaftaran Vendor", "Evaluasi Teknis")
- `paket_id` - Link to parent procurement package
- `start_date` - Stage start date/time
- `end_date` - Stage end date/time
- `perubahan` - Change version number (tracks timeline modifications)

**Usage**: Multiple schedules per package (one for each stage)

### 3. **SadayaLelangDokumen** (Tender Documents)
**Purpose**: Store tender documents and specifications that vendors need

**Key Fields**:
- `name` - Document name (e.g., "Spesifikasi Teknis", "Volume Pekerjaan")
- `paket_id` - Link to parent procurement package
- `file_dokumen` - Actual document file (PDF, Excel, etc.)
- `file_name` - File name for reference
- `description` - Document description/notes

**Usage**: Vendors download these before submitting proposals

### 4. **SadayaLelangPenawaran** (Vendor Proposals/Offers)
**Purpose**: Track vendor submissions and evaluation results

**Key Fields**:
- `name` - Auto-generated proposal number (e.g., "POF-2026-001")
- `paket_id` - Link to procurement package
- `vendor_id` - Link to submitting vendor (res.partner)
- `file_kualifikasi` - Qualification/admin documents (registration, licenses, tax)
- `file_penawaran` - Price and technical proposal files
- `harga_penawaran` - Quoted price amount
- `status` - Evaluation status:
  - `submitted` - Initial submission
  - `evaluated` - Under evaluation
  - `passed` - Passed qualification
  - `failed` - Failed qualification
  - `winner` - Selected as winner
- `skor_teknis` - Technical score (out of 100)
- `skor_harga` - Price score (out of 100)
- `currency_id` - Currency (auto-linked from package)

**Business Logic**:
- Final winner = highest combined score (technical + price)
- Price scores factor in HPS compliance

### 5. **ResPartner Extension** (Vendor Data)
**Purpose**: Extends Odoo's partner model with tender-specific vendor info

**Added Fields**:
- `is_vendor_tender` - Boolean flag indicating vendor is registered for tenders
- `vendor_status` - Verification status:
  - `draft` - Registration incomplete
  - `waiting` - Awaiting verification
  - `verified` - Approved for tendering
  - `rejected` - Failed verification
- `nib_number` - NIB (Nomor Induk Berusaha - Business ID number)
- `npwp_number` - NPWP (Nomor Pokok Wajib Pajak - Tax ID)
- `file_nib` - NIB document/certificate
- `file_npwp` - NPWP document/certificate

**Workflow**: Vendors must be verified before can participate in procurements

---

## Key Business Rules

### 1. **Tender Code Generation**
- Automatically generated using Odoo's sequence system
- Code: `sadaya_lelang.paket`
- Ensures unique identifier for each procurement

### 2. **Proposal Numbering**
- Auto-generated sequence for each proposal
- Code: `sadaya_lelang.penawaran`
- Format enables easy reference in evaluation

### 3. **HPS (Harga Perkiraan Sendiri) - Government Estimated Price**
- Set during procurement package creation (Persiapan Lelang stage)
- Acts as benchmark for price evaluation
- Vendors should quote below HPS to be competitive
- Prevents budget overruns

### 4. **Vendor Verification Requirement**
- Vendors must be marked `is_vendor_tender = True` and `vendor_status = 'verified'` before participating
- Verifies NIB and NPWP documentation
- Ensures only legitimate vendors can bid

### 5. **Status Workflow Guard**
- Package moves through 12 stages sequentially
- Cannot skip stages
- Only authorized roles can change status
- Ensures compliance with government procedures

### 6. **Role-Based Access Control**
- **USER/Pemohon** - Initiates procurement requests
- **MANAJEMEN** - Approves requests for procurement
- **PPK** - Supervises entire process
- **POKJA** - Evaluates proposals, makes recommendations
- **PPHP** - Verifies compliance and monitors
- Different roles have different view/edit permissions

### 7. **Two-Stage Evaluation Process**
- **Administrative/Qualification (file_kualifikasi)** - Verifies company credentials, licenses, certifications
- **Technical & Price (file_penawaran)** - Evaluates technical approach and pricing

### 8. **Scoring System**
- `skor_teknis` - Technical evaluation (0-100)
- `skor_harga` - Price evaluation (0-100)
- Winner determined by combined scores
- Higher score = better proposal

---

## Workflow Activities

Each procurement package can have:
- **Mail Threading** - Enabled for discussions, comments, and communication history
- **Activity Tracking** - Todo items, reminders, and follow-ups
- **Change History** - Automatic tracking of field changes (via `tracking=True`)

---

## Portal & Vendor Self-Service

The module includes portal templates for:
- Vendor registration and profile management
- Viewing available procurement packages
- Submitting proposals
- Tracking proposal status
- Downloading tender documents

---

## Menu Structure

The Odoo interface organizes features under **Sadaya Lelang** root menu:

```
Sadaya Lelang (root menu)
├── Paket Lelang
│   └── List, form, search for procurement packages
│   └── Create new procurement package
│   └── Monitor workflow status
│
├── Evaluasi Penawaran
│   └── View vendor proposals
│   └── Score technical and price proposals
│   └── Mark winners
│   └── Announce results
│
└── Verifikasi Vendor
    └── List vendors registered for tenders
    └── Verify NIB and NPWP documents
    └── Approve/reject vendor participation
    └── Manage vendor status
```

---

## Security & Access Control

**Role-Based Access** (ir.model.access.csv):
- User group: Limited CRUD on procurement packages and proposals
- Manager group: Full CRUD on all models
- Vendor group: Limited access to assigned packages and proposals

**Document Upload Security**:
- Binary files stored in database
- Access controlled by role permissions
- Activity log tracks all document access

---

## Dependencies

| Module | Purpose |
|--------|---------|
| `base` | Core Odoo framework |
| `mail` | Email, threading, activities |
| `portal` | Vendor self-service portal |

---

## Key Features Implemented

✓ **Auto-Generated Identifiers** - Tender codes and proposal numbers
✓ **12-Stage Workflow** - Complete government procurement lifecycle  
✓ **Role-Based SOP** - USER, MANAJEMEN, PPK, POKJA, PPHP roles
✓ **Document Management** - Upload and track all procurement documents  
✓ **Vendor Verification** - NIB and NPWP validation workflow
✓ **Proposal Scoring** - Technical and price evaluation system
✓ **Change Tracking** - Audit trail of all modifications
✓ **Portal Integration** - Vendor self-service interface
✓ **Activity Management** - Mail threading and activity tracking
✓ **Status Guards** - Prevents invalid workflow transitions

---

## Comparison Notes for Documentation

When comparing with government procurement standards/documents:

### Check For:
1. **Status Stages** - Verify all 12 stages align with institution's SOP
2. **Roles & Approvals** - Confirm USER→MANAJEMEN→PPK→POKJA flow matches org structure
3. **Document Requirements** - Verify file_kebutuhan, file_disposisi, etc. match SOP requirements
4. **Vendor Criteria** - NIB/NPWP fields should align with government vendor registration
5. **HPS Logic** - Confirm how estimated price is calculated and used
6. **Evaluation Scoring** - Verify skor_teknis and skor_harga weights match procurement rules
7. **Timeline Controls** - Check jadwal dates against government minimum publication periods
8. **Performance Bond** - jaminan_pelaksanaan stage implementation

### Common Indonesian Government Procurement Terms:
- **POKJA** - Panitia/Kelompok Kerja (Procurement Committee)
- **PPK** - Pejabat Pembuat Komitmen (Project Control Officer)
- **PPHP** - Pejabat Pengawas Hibu Pelaksanaan (Procurement Supervisor)
- **HPS** - Harga Perkiraan Sendiri (Government's estimated cost)
- **NIB** - Nomor Induk Berusaha (Business Identity Number)
- **NPWP** - Nomor Pokok Wajib Pajak (Tax ID)
- **BAST** - Berita Acara Serah Terima (Handover-Acceptance Report)
- **SPPBJ** - Surat Perintah Pengadaan Barang/Jasa (Procurement Letter)

---

## Notes for Implementation

- All currency values use company currency (via res.currency)
- Mail threading enables collaborative procurement discussions
- Portal enables vendor transparency and self-service
- Document uploads are versioned at package level (perubahan field)
- Change history automatically tracked for compliance audit
