# Data Management Plan (DMP) — 前列安汇 (probiopsy-rag)

> **Purpose**: IRB application, journal Data Availability section, full-lifecycle data governance reference
> **Created**: 2026-09-13
> **Version**: v1.0
> **Companion docs**: [ETHICS.en.md](ETHICS.en.md) | [IRB_Protocol_Summary.en.md](IRB_Protocol_Summary.en.md)

---

## 1. Data Overview

### 1.1 Data Sources

| # | Source | Type | PHI | Volume | License |
|---|---|---|---|---|---|
| 1 | [TODO: hospital_name] EMR | Retrospective records | **Yes** | 0 | DUA [TODO: dua_id] |
| 2 | CTD (ctdbase.org) | Chemical-gene-disease | No | 94M+ connections | CC BY 4.0 (curated); API ToS |
| 3 | EPA ToxCast/Tox21 (invitroDB V4.2) | In vitro HTS | No | 9500 chemicals × 625 assays | Public (federal work) |
| 4 | EPA CompTox Chemicals Dashboard | Chemical | No | 1M+ | Public |
| 5 | TEDX Endocrine Disruptor Exchange | EDC list | No | ~1500 | Academic free |
| 6 | California Prop 65 | Reproductive toxicants | No | ~300 | Public |
| 7 | ECHA REACH SVHC | Substances of concern | No | ~235 | CC BY 4.0 |
| 8 | ATSDR Toxicological Profiles | Toxicology | No | ~180 monographs | Public |
| 9 | DisGeNET | Gene-disease | No | 1M+ | CC BY-NC 4.0 (partial paid) |
| 10 | KEGG / Reactome | Pathways | No | Standard | Respective licenses |
| 11 | NHANES (CDC) | Population biomonitoring | No (de-identified) | Multi-cycle | Public |
| 12 | PubMed E-utilities | Literature | No | 36M+ abstracts | NCBI API ToS |
| 13 | FDA DailyMed | Drug labels | No | 100k+ | Public |
| 14 | IARC Monographs | Carcinogen/repro-tox | No | ~100 monographs | Public |
| 15 | NTP Reports | Toxicology | No | Hundreds | Public |

### 1.2 Data Classification

- **Tier 1 (PHI)**: Hospital EMR — protected under PIPL / HIPAA-equivalent
- **Tier 2 (Sensitive anonymized)**: De-identified hospital data — bound by DUA
- **Tier 3 (Public)**: Sources #2-#15 — under respective licenses

---

## 2. Data Collection

### 2.1 Hospital Data (Tier 1 + 2)

**Flow**:

```
[Hospital EMR system]
     ↓ Export via hospital IT (controlled environment)
[On-site secure server]
     ↓ HIPAA Safe Harbor de-identification (see §3)
[Tier 2 data]
     ↓ Encrypted transfer (TLS 1.3) to research server
[Huanyu research server]
```

**Collected fields**:
- Demographics: Age band (10-year strata), sex, region (province level)
- Diagnosis: ICD-11 codes, subtype (PCOS/POI/...)
- Exposure history: Occupation (industry), lifestyle (smoking / alcohol / diet pattern)
- Outcomes: IVF cycles, clinical pregnancy, live birth (if applicable)
- Labs: Hormone levels (aggregated to normal/abnormal binary)

**Excluded fields** (never collected):
- Name, ID number, insurance number, phone, email
- Detailed address (below province)
- Full birth date (only year)
- Visit dates (only year)
- Raw imaging files

### 2.2 Public Data (Tier 3)

- Via API / bulk download
- Record **release date** for version lock
- Naming: `data/raw/<source>/release-YYYY-MM.json`

---

## 3. De-Identification Protocol

### 3.1 Standard

**HIPAA Safe Harbor** 18 identifiers (45 CFR 164.514(b)(2)(i)) + China **PIPL Article 28** sensitive personal information requirements.

### 3.2 18 Identifiers Handling

| # | Identifier | Handling |
|---|---|---|
| 1 | Name | Drop; replace with pseudo-ID (hash) |
| 2 | Geography (sub-province) | Province only |
| 3 | Dates (non-year) | Year only; offset by random days |
| 4 | Phone / Fax | Drop |
| 5 | Email | Drop |
| 6 | SSN / National ID | Drop |
| 7 | Insurance ID | Drop |
| 8 | Account numbers | Drop |
| 9 | License / certificate | Drop |
| 10 | Vehicle ID / plate | Drop |
| 11 | Device ID / serial | Drop |
| 12 | URL | Drop |
| 13 | IP address | Drop |
| 14 | Biometric | Drop |
| 15 | Unique tattoos / marks | Drop |
| 16 | Photos | Drop (or face-obscure if needed) |
| 17 | Age > 89 | Aggregate to "≥ 90" |
| 18 | Other unique codes | Drop |

### 3.3 Execution

- **Executor**: Hospital IT + data manager ([TODO: data_manager_name])
- **Environment**: On-site secure server; never leaves hospital network
- **Audit**: Operation logs retained
- **Re-identification test**: Independent staff sample 100 cases; verify no re-ID possible

---

## 4. Storage & Access

### 4.1 Storage Location

| Tier | Location | Encryption |
|---|---|---|
| Tier 1 (PHI) | On-site hospital server (**never transferred**) | AES-256 + TLS 1.3 |
| Tier 2 (de-identified) | 本地工作站(加密磁盘),仅使用公开数据 (institution-controlled cloud) | AES-256 + TLS 1.3 |
| Tier 3 (public) | Local project server | Not required |

### 4.2 Access Control

- **RBAC** (Role-Based Access Control)
- **Least-privilege principle**
- **2FA** for all PHI/Tier 2 accounts
- **Audit logs**: All access recorded, retained 5+ years

### 4.3 Backup

- **Frequency**: Daily incremental, weekly full
- **Retention**: 6 months
- **Offline copy**: Quarterly

---

## 5. Data Sharing

### 5.1 Principles

**FAIR** (Findable, Accessible, Interoperable, Reusable) + controlled access for protected data.

### 5.2 Sharing Tiers

| Data Type | Sharing |
|---|---|
| **Code** | GitHub public (MIT / Apache 2.0) |
| **De-identified dataset (Tier 2)** | Released to Zenodo / OSF (DOI) after IRB approval |
| **Public data snapshots (Tier 3)** | GitHub releases (version locked) |
| **LLM call logs** | Retained 5 years controlled; then destroyed |
| **PHI (Tier 1)** | **Never shared**; DUA-based access at hospital only |

### 5.3 Data Use Agreement (DUA)

- **Template**: [TODO: dua_template_reference]
- **Approval**: PI → data manager → both institutional legal → IRB record
- **Typical terms**: Approved purpose only; no further sharing; destruction on completion

### 5.4 Data Availability Statement (for manuscript)

> "The code supporting this study is available at https://github.com/<TODO>/huanyu under the MIT license. De-identified clinical data will be available upon reasonable request to the corresponding author, subject to a Data Use Agreement and approval by the institutional review board. Public data sources (CTD, ToxCast, Prop 65, ECHA, ATSDR, etc.) are accessible via their respective APIs under the licenses noted in Supplementary Table S1."

---

## 6. Retention & Destruction

### 6.1 Retention Period

| Data | Retention | Basis |
|---|---|---|
| PHI (Tier 1) | 5 years post-study | Journal + IRB requirement |
| Tier 2 de-identified | 5 years post-study | Replication / re-review |
| Tier 3 public snapshots | Permanent (DOI) | Replication |
| LLM call logs | 5 years | AI transparency |
| Audit logs | 5 years | Compliance |

### 6.2 Destruction Method

- **Electronic**: NIST SP 800-88 "Clear/Purge" standard (≥ 3 overwrite passes)
- **Physical media**: Physical destruction (disk shredding)
- **Destruction certificate**: Retained; submitted to IRB in closure report

### 6.3 Destruction Timeline

- Study end: [TODO: study_end_date] (~10 weeks)
- Mandatory destruction: [TODO: destruction_date] (5 years post-study)

---

## 7. Data Quality & Integrity

### 7.1 Quality Control

- **Data entry**: Double-key independent entry + third-person arbitration
- **Logic checks**: Automated validation (e.g., age ≤ 120; diagnosis-sex consistency)
- **Outliers**: Flag and review

### 7.2 Version Control

- **Code**: Git (GitHub / Gitee)
- **Data snapshots**: `data/raw/<source>/release-YYYY-MM.json` with SHA-256 checksum
- **Model checkpoints**: `outputs/checkpoints/<date>/<seed>/`

### 7.3 Metadata

Each dataset includes `manifest.json`:

```json
{
  "source": "CTD",
  "release_date": "2026-03",
  "url": "https://ctdbase.org/downloads/",
  "downloaded_at": "2026-04-15T10:30:00Z",
  "sha256": "...",
  "license": "CC BY 4.0",
  "n_records": 94000000,
  "schema_version": "v1.2"
}
```

---

## 8. Security Incident Response

### 8.1 Incident Severity

| Severity | Definition | Response |
|---|---|---|
| Tier 1 (Severe) | PHI released to unauthorized party | Notify IRB + affected individuals within 24h |
| Tier 2 (Severe) | Unauthorized access to research data | Notify IRB within 48h |
| Tier 3 (General) | Internal misuse, no external leak | Log + post-mortem within 72h |

### 8.2 Response Flow

1. **Detection**: Any person (researcher / IT / auditor) reports immediately to PI
2. **Isolation**: Revoke access; isolate affected systems
3. **Forensics**: Preserve logs; assess scope
4. **Notification**: Per severity
5. **Remediation**: Fix vulnerabilities; strengthen controls
6. **Documentation**: Complete incident record

---

## 9. Regulatory Compliance

### 9.1 Chinese Regulations

- ✅ PIPL (2021) — Article 28 sensitive personal information handling
- ✅ DSL (2021)
- ✅ Health Big Data Management Measures (2018)
- ✅ Ethical Review Measures (2016)

### 9.2 International (if applicable)

- ✅ GDPR (if serving EU data subjects) — Article 9 special category data
- ✅ HIPAA Privacy Rule (if serving US subjects)
- ✅ Declaration of Helsinki (2013)

### 9.3 Standards

- ISO 27001 (Information Security Management)
- ISO 27701 (Privacy Information Management)
- NIST SP 800-88 (Data Destruction)
- FAIR Data Principles

---

## 10. DMP Maintenance

- **Owner**: Data manager [TODO: data_manager_name]
- **Update trigger**: Data source change, IRB amendment, regulatory update
- **Version**: Increment +0.1 per update
- **Archive**: All versions retained permanently

---

## Appendix A: Data Source License Details

| Source | License | Commercial | Derivatives |
|---|---|---|---|
| CTD curated | CC BY 4.0 | Yes (with attribution) | Yes |
| ToxCast | Public Domain (federal work) | Yes | Yes |
| DisGeNET | CC BY-NC 4.0 | **No** | Yes (non-commercial) |
| KEGG | Academic free / Commercial paid | Depends on subscription | Depends |
| PubMed abstracts | NCBI API ToS | Citation allowed | Abstracts not derivatives |
| Prop 65 | Public Domain | Yes | Yes |
| ECHA | CC BY 4.0 | Yes (with attribution) | Yes |
| ATSDR | Public Domain | Yes | Yes |
| IARC | CC BY-NC-ND 3.0 IGO | **No** | **No** |

→ **Important**: Post-publication, parts using DisGeNET / IARC data must note non-commercial use restrictions in Limitations.

---

## Appendix B: De-Identification Self-Check

Data manager checks before IRB submission:

- [ ] All 18 HIPAA Safe Harbor identifiers handled
- [ ] Any single dataset cell size ≥ 5 (prevent small-cell re-ID)
- [ ] Geographic granularity ≥ province level
- [ ] Dates offset or year-only
- [ ] Age > 89 aggregated
- [ ] Sample 100 cases; no cross-source re-ID possible
- [ ] Operation logs complete
- [ ] Independent reviewer signature

Completion date: ____________________  Data manager signature: ____________________
