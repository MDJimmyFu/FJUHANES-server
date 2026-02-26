# 住院資訊系統 PCA 與無痛分娩處方開立方式分析報告

本報告分析了 `PCA.pcapng` 與 `painless.pcapng` 封包檔案，以找出在住院資訊系統 (`http://10.10.246.80/Ipo/IpoQ010`) 中開立 PCA (病人自控式止痛) 與無痛分娩 (Painless Labour) 處方的方法。

## 1. PCA (病人自控式止痛) 處方開立

PCA 的開立主要透過 `/Ipo/IpoC11G` 模組進行，該模組處理管制藥品的開立。

### 主要 API 資訊
- **Endpoint**: `POST http://10.10.246.80/Ipo/IpoC11G/IpoC11GSave`
- **關鍵參數 (Payload)**:
    - `hCaseNo`: 就醫序號 (例如 `75176383`)
    - `hHISNum`: 病歷號 (例如 `000000002C`)
    - `ipoC11CViewsJson`: 包含處方明細的 JSON 字串。
        - `UDDDrgCode`: `FEN02` (Fentanyl 管二 高 0.5 mg/10 mL/Amp)
        - `UDOGivRoute`: `PCA` (給藥途徑)
        - `UDOGivFreqn`: `ASORDER` (給藥頻率)
        - `UDDCmmDose`: `1` (給藥劑量)
    - `RxControlJson`: 管制藥品查核資訊。

---

## 2. 無痛分娩 (Painless Labour) 處方開立

無痛分娩的開立由兩個部分組成：**藥物處方**與**處置醫囑 (Treatment)**。

### A. 藥物處方 (PCA 模式)
與 PCA 類似，但給藥途徑不同。
- **Endpoint**: `POST http://10.10.246.80/Ipo/IpoC11G/IpoC11GSave`
- **關鍵參數差異**:
    - `UDOGivRoute`: `PAINL` (代表 Painless Labour / 減痛分娩)
    - `UDDDrgCode`: `FEN02` (Fentanyl)

### B. 處置醫囑 (Treatment Order)
系統透過 `/Ipo/IpoC151` 模組儲存相關的監測醫囑。
- **Endpoint**: `POST http://10.10.246.80/Ipo/IpoC151/Save`
- **關鍵處置代碼 (TRTCode)**:
    - `XTR00403`: `Check vital signs Q30min for 2 hours, then Q1H until delivery`
    - `XTR00024`: `@Check vital signs` (備註中包含無痛分娩後的監測要求)
- **模板選取**: 在儲存前，系統會呼叫 `POST /Ipo/IpoC151/ProcessBASOTGP` 來載入預設的無痛分娩套餐項目。

---

## 3. PCA 處方 PDF 列印方式

在開立處方後，系統會自動或手動觸發列印流程。該系統使用 Telerik Reporting 服務來產生 PDF。

### A. 初始化列印請求
- **Endpoint**: `GET http://10.10.246.80/Ipo/IpoC110/PrintP022`
- **參數**:
    - `HCaseNo`: 就醫序號 (例如 `75176383`)
    - `hPrintKind`: `P022` (代表 PCA/管制藥品處方箋)
    - `DrugTrackNo`: 藥物追蹤編號 (例如 `37`)
    - `OrdSeq`: 醫囑序號 (例如 `A75176383UD0031`)

### B. Telerik 報表產生流程 (API 調用順序)
系統會透過以下 API 進行報表渲染：
1. **建立客戶端**: `POST /Ipo/api/reports/clients`
2. **建立報表實例**: `POST /Ipo/api/reports/clients/{clientID}/instances`
   - **Payload**: 指定報表名稱為 `Ipo.ReportLibrary.IpoP022Report` 並傳入上述參數。
3. **產生 PDF 文件**: `POST /Ipo/api/reports/clients/{clientID}/instances/{instanceID}/documents`
   - **Payload**: `{"format":"PDF", ...}`
4. **下載 PDF**: `GET /Ipo/api/reports/clients/{clientID}/instances/{instanceID}/documents/{docID}?response-content-disposition=attachment`

---

## 4. 分析總結

要在該系統中完成「開立並列印」的完整流程：
1. **開立處方**: 透過 `IpoC11GSave` 開立藥物，獲取 `DrugTrackNo` 與 `OrdSeq`。
2. **(選填) 開立處置**: 若為無痛分娩，需額外呼叫 `IpoC151/Save` 開立監測醫囑。
3. **執行列印**: 帶入產生的序號呼叫 `PrintP022` 啟動 PDF 產生流程。
