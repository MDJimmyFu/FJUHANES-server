# Anesthesia Form Mapping (100% Complete)

This document provides the definitive mapping between the HTML form elements in `legacy_schedule.html` and their corresponding placement and logic in the generated PDF.

---

## 1. Assessment Summary & Plan Summary (Aggregated Sections)
These fields do not have fixed coordinates for individual checked items. Instead, they are aggregated by the `collectSectionSummary` and `getRecursivelyCheckedText` functions.

-   **Assessment Summary**: Bottom multi-line text area. Aggregates all checked items from "Clinical Assessment" sections.
-   **Plan Summary**: Bottom multi-line text area. Aggregates all checked items from "Anesthesia Plan" sections.

---

## 2. Specific Field Mapping (Fixed Coordinates & Logic)

### A. 心血管系統 (Cardiovascular System)
| 階層 | 顯示名稱 | HTML ID | PDF 映射詳細資料 |
| :--- | :--- | :--- | :--- |
| 第1階 | (1) Hypertension (高血壓) | `chk_cv_htn` | Yes: 227.14, 613.78 / No: 195.19, 613.78 |
| 第2階 | 　└ Regular control | `chk_cv_htn_reg` | Summary 區文字串接 |
| 第2階 | 　└ Poor control | `chk_cv_htn_poor` | Summary 區文字串接 |
| 第1階 | (2) CAD (冠狀動脈疾病) | `chk_cv_cad` | **母項勾選即觸發 Cardiac Yes** (Y:599.57) |
| 第2階 | 　└ POBA/POBAS | `chk_cv_cad_poba` | Summary 區文字串接 |
| 第2階 | 　└ CABG | `chk_cv_cad_cabg` | Summary 區文字串接 |
| 第2階 | 　└ Others | `chk_cv_cad_oth` | Summary 區文字串接 |
| 第3階 | 　　└ [Others 文字輸入] | `txt_cv_cad_oth` | 顯示於心血管橫線處 (Y:586.88) |
| 第1階 | (3) Valvular disease (瓣膜疾病) | `chk_cv_valve` | **母項勾選即觸發 Cardiac Yes** (Y:599.57) |
| 第2階 | 　└ [補充說明文字] | `txt_cv_valve_note` | 顯示於心血管橫線處 (Y:586.88) |
| 第1階 | (4) Arrhythmia & ECG Abnormality (心律不整) | `chk_cv_arr` | **母項勾選即觸發 Cardiac Yes** (Y:599.57) |
| 第2階 | 　└ Pacemaker | `chk_cv_arr_pm` | Summary 區文字串接 |
| 第2階 | 　└ Atrial fibrillation | `chk_cv_arr_af` | Summary 區文字串接 |
| 第3階 | 　　└ Paroxysmal | `chk_cv_arr_af_par` | Summary 區文字串接 |
| 第3階 | 　　└ Persistent | `chk_cv_arr_af_per` | Summary 區文字串接 |
| 第2階 | 　└ AV Block | `chk_cv_arr_avb` | Summary 區文字串接 |
| 第3階 | 　　└ First degree / Mobitz I/II / Complete | `chk_cv_arr_avb_1/m1/m2/3` | Summary 區文字串接 |
| 第1階 | (5) Heart failure (心衰竭) | `chk_cv_hf` | **母項勾選即觸發 Cardiac Yes** (Y:599.57) |
| 第2階 | 　└ NYHA Class [下拉選單] | `sel_cv_hf_nyha` | 顯示於心血管橫線處 (Y:586.88) |
| 第2階 | 　└ HFpEF / HFrEF | `chk_cv_hf_pef/ref` | Summary 區文字串接 |
| 第1階 | (6) Dyslipidemia (血脂異常) | `chk_cv_lipid` | **母項勾選即觸發 Cardiac Yes** |
| 第1階 | (7) PAOD (周邊動脈阻塞疾病) | `chk_cv_paod` | **母項勾選即觸發 Cardiac Yes** |
| 第1階 | (8) Vascular disease | `chk_cv_vasc` | **母項勾選即觸發 Cardiac Yes** |
| 第1階 | (9) Congenital heart disease | `chk_cv_congen` | **母項勾選即觸發 Cardiac Yes** |
| 第1階 | (10) Pulmonary hypertension | `chk_cv_ph` | **母項勾選即觸發 Cardiac Yes** |
| 第1階 | (11) Others | `chk_cv_oth` | (內嵌文字 `txt_cv_oth` 顯示於橫線) |

### B. 神經精神系統 (Neurologic & Psychiatric)
| 階層 | 顯示名稱 | HTML ID | PDF 映射詳細資料 |
| :--- | :--- | :--- | :--- |
| 第1階 | (1) CVA (腦中風) | `chk_neu_cva` | Yes: 227.14, 627.61 / No: 195.19, 627.61 |
| 第2階 | 　└ Ischemic / Hemorrhagic / Hemiparesis | `chk_neu_cva_isc/hem/hemi` | Summary 區文字串接 |
| 第3階 | 　　└ Right / Left | `chk_neu_cva_hemi_r/l` | Summary 區文字串接 |
| 第1階 | (2) Traumatic Brain Injury (創傷性腦損傷) | `chk_neu_tbi` | Summary 區文字串接 |
| 第1階 | (3) Parkinson disease (帕金森氏症) | `chk_neu_park` | Summary 區文字串接 |
| 第1階 | (4) Seizure (癲癇) | `chk_neu_seiz` | Summary 區文字串接 |
| 第1階 | (5) Dementia (失智症) | `chk_neu_dem` | Summary 區文字串接 |
| 第1階 | (6) Psychiatric disorder (精神不齊) | `chk_neu_psy` | Summary 區文字串接 |
| 第2階 | 　└ Schizophrenia / Bipolar / Depression | `chk_neu_psy_sch/bip/dep` | Summary 區文字串接 |
| 第1階 | (7) Neuromuscular disease (神經肌肉疾病) | `chk_neu_nmd` | Summary 區文字串接 |
| 第2階 | 　└ Myasthenia Gravis | `chk_neu_nmd_mg` | Summary 區文字串接 |
| 第1階 | (8) GCS (昏迷指數) | `chk_neu_gcs` | 組合 E/V/M 數值顯示於 Summary 區 |
| 第2階 | 　└ E-V-M [輸入框] | `txt_neu_gcs_e/v/m` | 組合後加入 Summary |

### C. 內分泌系統 (Endocrine System)
| 階層 | 顯示名稱 | HTML ID | PDF 映射詳細資料 |
| :--- | :--- | :--- | :--- |
| 第1階 | (1) DM (糖尿病) | `chk_end_dm` | Yes: 227.14, 642.1 / No: 195.19, 642.1 |
| 第2階 | 　└ OAD / Insulin | `chk_end_dm_oad/ins` | Summary 區文字串接 |
| 第2階 | 　└ Others | `chk_end_dm_oth` | Text: `txt_end_dm_oth` |
| 第1階 | (2) Thyroid disease (甲狀腺疾病) | `chk_end_thy` | Summary 區文字串接 |
| 第2階 | 　└ Hyperthyroidism / Hypothyroidism | `chk_end_thy_hyper/hypo` | Summary 區文字串接 |

### D. 呼吸系統 (Respiratory System)
| 階層 | 顯示名稱 | HTML ID | PDF 映射詳細資料 |
| :--- | :--- | :--- | :--- |
| 第1階 | (1) Asthma (氣喘) | `chk_res_asth` | Yes: 227.14, 585.73 / No: 195.19, 585.73 |
| 第2階 | 　└ Inhalational control / steroid / Oral steroid | `chk_res_asth_inh/inh_st/oral_st` | Summary 區文字串接 |
| 第1階 | (2) COPD (慢性阻塞性肺病) | `chk_res_copd` | Yes: 227.14, 571.53 / No: 195.19, 571.53 |
| 第1階 | (3) Smoking (抽菸) | `chk_res_smok` | Yes: 227.14, 501.32 / No: 195.19, 501.32 |
| 第2階 | 　└ Quit / Persistent [時間/PPD] | `txt_res_smok_quit_dur/per_ppd` | 顯示於吸菸備註橫線處 (Y:488.94) |

### E. 呼吸道評估 (Airway)
| 階層 | 顯示名稱 | HTML ID | PDF 映射詳細資料 |
| :--- | :--- | :--- | :--- |
| 第1階 | (1) Mallampati score | - | 1: 227.85 / 2: 255.87 / 3: 287.81 / 4: 323.66 (Y:278.44) |
| 第1階 | (2) Neck ROM (頸部活動度) | - | Limited 勾選 -> 觸發 Airway Abnormal (245.58, 260.32) |
| 第1階 | (3) Mouth opening (張口度) | - | <1FB 勾選 -> 觸發 Airway Abnormal |
| 第1階 | (4) Intubated (已插管) | `chk_aw_intub_yes` | Summary 區文字串接 |
| 第1階 | (5) Tracheostomy (氣切) | `chk_aw_trach_yes` | Summary 區文字串接 |
| 第1階 | (7) OSA (睡眠呼吸中止症) | `chk_aw_osa_yes` | Summary 區文字串接 |
| 第1階 | (8) Dentition (牙齒狀況) | - | Loose/Remov 勾選 -> 觸發 Airway Abnormal |
| 第1階 | (9) Expected difficult airway | `chk_aw_diff_yes` | 觸發 Airway Abnormal |

### F. 腎臟/血液/消化/過敏 (Renal / Hematologic / Digestive / Allergy)
| 區域 | 主項 ID | Yes 座標 (X, Y) | No 座標 (X, Y) | 主要備註映射 |
| :--- | :--- | :--- | :--- | :--- |
| **Renal** | `chk_ren_esrd` | 227.14, 543.5 | 195.19, 543.5 | `txt_ren_oth` (Y:530.81) |
| **Hematologic** | `chk_hem_coag` | 227.14, 529.36 | 195.19, 529.36 | `txt_hem_oth` (Y:516.98) |
| **Digestive** | `chk_dig_carrier` | 227.14, 557.7 | 195.19, 557.7 | `txt_dig_oth` (Y:545.0) |
| **Allergy** | `chk_alg_yes` | 227.14, 515.17 | 195.19, 515.17 | `txt_alg_note` (Y:502.79) |

### G. ASA 分級與手術麻醉史 (ASA & History)
| 階層 | 顯示名稱 | HTML ID | PDF 映射詳細資料 |
| :--- | :--- | :--- | :--- |
| 第1階 | 1 / 2 / 3 / 4 / 5 / 6 | `chk_asa_1`~`6` | X: [158.14, 186.1, 218.06, 254, 291.13, 323.09], Y: 314.26 |
| 第1階 | Emergency (緊急手術) E | `chk_asa_e` | 361.21, 314.26 |
| 第1階 | (1) History of Surgery | `chk_his_surg_yes` | **觸發 Major Surgery Yes** (Y:487.13) |
| 第2階 | 　└ [手術史文字輸入] | `txt_his_surg_note` | **有內容即觸發 Major Surgery Yes** |
| N/A | [系統查詢麻醉歷史] | `window.aneHist` | **有歷史數據即自動勾選 Major Surgery Yes** |
| 第1階 | (2) Events | `chk_his_anes_yes` | Summary 區文字串接 |
| 第2階 | 　└ PONV | `chk_his_anes_ponv` | Summary 區文字串接 |

---

## 3. High-level Logic Summary
- **Abnormal Assessment**: 只要任一系統分類 (呼吸、心血管等) 被標記為 Abnormal 或 Yes，PDF 上對應的 Assess 欄位會打勾。
- **Auto-Check Yes**:
    - **Cardiac**: 包含 CAD, Valve, Arr, HF, Lipid, PAOD, Vasc, Congen, PH 任一勾選，皆自動勾選 PDF "Cardiac disease Yes"。
    - **Major Surgery**: 包含 Major operation 勾選、手術史勾選、手術史有文字、或系統內有麻醉歷史，皆自動勾選 PDF "Major operations Yes"。
- **Specific Highlight Areas**:
    - **Loose Teeth / Dentition**: 觸發 Airway Abnormal 區塊高亮。
    - **Mallampati Score >= 3**: 觸發 Airway Abnormal 區塊高亮。
    - **Neck ROM Limited**: 觸發 Airway Abnormal 區塊高亮。
