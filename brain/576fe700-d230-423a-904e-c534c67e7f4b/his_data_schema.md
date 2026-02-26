# HIS Data Schema Reference

This document lists all data fields and their content examples parsed from the HIS endpoints.

## 1. Surgery List (C250)
*Endpoint: `/HISOrmC250Facade`*

**Primary Key**: `ORDSEQ` (Surgery ID) + `HHISTNUM` (Patient ID)

| Field | Example Value | Description |
| :--- | :--- | :--- |
| `ORDSEQ` | `A75176797OR0014` | Unique Surgery Order Sequence |
| `HHISTNUM` | `003158375C` | Patient Medical Record Number |
| `HNAMEC` | `潘永銘` | Patient Name |
| `ORDOCNM` | `黃家偉` | Doctor Name |
| `ORDPROCED`| `Stomach Laparoscopic gastrostomy` | Procedure Name |
| `OROPROOM` | `01` | Operating Room Number |
| `HBED` | `11A-032` | Bed Number |
| `OP_TIME` | `TF` | Operation Time (or status) |
| `ORDSTATUS`| `31` | Order Status Code |

---

## 2. Pre-Anesthesia Evaluation (C430)
*Endpoint: `/HISOrmC430Facade`*

**Primary Key Context**: Data is grouped by Table Name.

### Table: VITALSIGN_* (Height, Weight, BP, etc.)
**Identifier**: `MEASURERECNO` (Measurement Record No)

| Field | Example | Description |
| :--- | :--- | :--- |
| `MEASURERECNO` | `0000019C4BDE029E` | Unique Measurement ID |
| `MEASUREDATETIME` | `20260211143800` | Timestamp of measurement |
| `HEIGHT` | `169` | Height (cm) |
| `WEIGHT` | `40` | Weight (kg) |
| `SBPVALUE` / `DBPVALUE` | `89` / `69` | Systolic / Diastolic BP |
| `PULSEVALUE` | `98` | Pulse Rate |
| `BTVALUE` | `36.6` | Body Temperature |
| `SPO2` | `98` | Oxygen Saturation |
| `RESPVALUE` | `15` | Respiration Rate |

### Table: INSPECTION (Lab Results)
**Identifier**: `TITLE` + `SIGNDATE`

| Field | Example | Description |
| :--- | :--- | :--- |
| `TITLE` | `WBC` | Lab Test Name |
| `SYB_VALUE` | `14.94` | Test Result Value |
| `SIGNDATE` | `20260211` | Date of test |

### Table: PAT_ADM_DRMEMO (Doctor Memos)
**Identifier**: `DRMID` (Memo ID)

| Field | Example | Description |
| :--- | :--- | :--- |
| `DRMID` | `20260211151029` | Memo ID / Timestamp |
| `CONTEXT` | `DM.Hypopharyngeal ca...` | Memo Content |
| `OPNM` | `吳珮嘉` | Author Name |

---

## 3. Anesthesia Charging (Q050)
*Endpoint: `/HISOrmQ050Facade`*

**Primary Key Context**: Data is grouped by Table Name.

### Table: ORRANER (Anesthesia Details)
**Identifier**: `ORDSEQ`

| Field | Example | Description |
| :--- | :--- | :--- |
| `ORDSEQ` | `A75176797OR0014` | Surgery Order Sequence |
| `PROCNMC` | `徐鳳霙` | Anesthesiologist Name |
| `ANEASA` | `1` | ASA Physical Status Classification |
| `ANEBGNDTTM` | `2026-02-12T09:14:00+08:00` | Anesthesia Start Time |
| `ANEENDDTTM` | `2026-02-12T11:14:00+08:00` | Anesthesia End Time |

### Table: OPDORDM (Billing Orders)
**Identifier**: `ORDSEQ` (Order Sequence)

*Note: This table contains both Procedures and Materials.*

| Field | Example | Description |
| :--- | :--- | :--- |
| `ORDSEQ` | `A75176797OR0015` | Unique Order ID for this item |
| `PFKEY` | `MCEE010001` | Billing Item Code |
| `PFNM` | `免針式點滴輸液套` | Item Name |
| `DOSE` | `1` | Quantity |
| `PROCNMC` | `顏孟婕` | Person executing/billing the order |
| `PROCDATETIME` | `20260211144044` | Time of billing |
| `OPDCASENO` | `75176797` | Case Number |

### Table: COMMON_ORDER
**Identifier**: `ORDSEQ`

| Field | Example | Description |
| :--- | :--- | :--- |
| `ORDSEQ` | `A75176797OR0014` | Surgery Order Sequence |
| `ORDPROCED`| `Stomach Laparoscopic gastrostomy` | Main Procedure Name |
| `ORDOENMC` | `黃家偉` | Ordering Doctor |

### Table: PAT_ADM_CASE (Admission Info)
**Identifier**: `HCASENO`

| Field | Example | Description |
| :--- | :--- | :--- |
| `HCASENO` | `75176797` | Hospital Case Number |
| `HVDOCNM` | `黃家偉` | Attending Doctor |
| `HNURSTA` | `11A` | Nurse Station |
| `HBED` | `032` | Bed Number |

