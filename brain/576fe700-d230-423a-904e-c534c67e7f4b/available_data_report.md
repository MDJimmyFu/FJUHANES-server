# Available Data Report

The following is a list of all data currently available in the live HIS system for patients `003617083J` and `003509917D`, retrieved via the `HISOrmC430Facade` (Pre-Anesthesia) and `HISExmFacade` (Vitals) endpoints.

> [!IMPORTANT]
> **Lab Data is Missing**: The `INSPECTION` table (Lab Results) is **NOT** returned by the live system for either patient. Per your instruction, the fallback mechanism has been disabled, so no lab data will appear in the application.

## Patient: 003617083J (ORDSEQ: A75176986OR0041)

### 1. Vitals (from HISExmFacade)
| Field | Value | Timestamp |
| :--- | :--- | :--- |
| `WEIGHT` | 49.10 | - |
| `HEIGHT` | 157 | - |
| `SPO2` | 99 | 2026-02-18T12:59:11 |
| `SBPVALUE` / `DBPVALUE` | 111 / 67 | 2026-02-18T12:59:11 |
| `PULSEUSUAL` | 73 | 2026-02-18T12:59:11 |
| `RESPVALUE` | 16 | 2026-02-18T12:59:11 |
| `BTVALUE` | 36.90 | 2026-02-18T12:59:11 |

### 2. Surgery Info (from HISOrmC430Facade.ORDOP)
*Selected Fields:*
- `ORDIAG`: Peritonitis, r/o ruptured app
- `OROPROOM`: 11
- `OP_DATE`: 2026-02-18
- `ORDOCNM`: 蔡煥文 (Surgeon)
- `ORANENM`: GE (Anesthesia Method)
- `ORCATGY`: PEDS

### 3. Anesthesia Info (from HISOrmC430Facade.ORRANER)
*Selected Fields:*
- `ANEDOCNMC`: 楊凱 (Anesthesiologist)
- `ANEASA`: 1
- `ANEPTCAS`: 5

### 4. Admin Info (from HISOrmC430Facade.PAT_ADM_CASE)
*Selected Fields:*
- `HNURSTA`: 7A (Ward)
- `HBED`: 031 (Bed)
- `HCASENO`: 75176986
- `HFINANCL`: 7

---

## Patient: 003509917D (ORDSEQ: A75177038OR0007)

### 1. Vitals (from HISExmFacade)
| Field | Value | Timestamp |
| :--- | :--- | :--- |
| `WEIGHT` | 45 | - |
| `HEIGHT` | 153 | - |
| `SPO2` | 94 | 2026-02-18T12:26:35 |
| `SBPVALUE` / `DBPVALUE` | 98 / 58 | 2026-02-18T12:26:35 |
| `PULSEUSUAL` | 58 | 2026-02-18T12:26:35 |
| `RESPVALUE` | 16 | 2026-02-18T12:26:35 |
| `BTVALUE` | 37.10 | 2026-02-18T12:26:35 |

### 2. Surgery Info (from HISOrmC430Facade.ORDOP)
- `ORDIAG`: Fx. It. trochanter
- `PFNM`: Open reduction for fr. , femur, trochanter type III, IV
- `OP_DATE`: 2026-02-18
- `ORDOCNM`: 張建炳
- `ORANENM`: GE (Anesthesia Method)

### 3. Orders (from HISOrmC430Facade.OR_ORDER)
Sample Orders found:
- `PFNM`: Open reduction for fr. , femur, trochanter type III, IV
- `PFNM`: AO Synthes
- `PFNM`: 拋棄式沖洗器 5ml
- `PFNM`: 藥用塑膠尿壺

### 4. Admin Info (from HISOrmC430Facade.PAT_ADM_CASE)
- `HNURSTA`: 10B
- `HBED`: 091
- `HCASENO`: 75177038
