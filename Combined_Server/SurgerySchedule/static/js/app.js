/**
 * Surgery Schedule Premium Dashboard Logic - FINAL
 */

const PDF_FIELD_COORDS = [
    { "label": "病歷號 :", "pdflib_x": 121.24, "pdflib_y": 741.65 },
    { "label": "姓名 :", "pdflib_x": 235.52, "pdflib_y": 741.65 },
    { "label": "生日 :", "pdflib_x": 337.72, "pdflib_y": 741.65 },
    { "label": "床號 :", "pdflib_x": 433.0, "pdflib_y": 741.33 },
    { "label": "ID:", "pdflib_x": 496.92, "pdflib_y": 741.14 },
    { "label": "年齡 :", "pdflib_x": 114.5, "pdflib_y": 724.63 },
    { "label": "血型 :", "pdflib_x": 228.76, "pdflib_y": 724.63 },
    { "label": "性別 :", "pdflib_x": 312.87, "pdflib_y": 724.63 },
    { "label": "身高 :", "pdflib_x": 396.97, "pdflib_y": 724.63 },
    { "label": "體重 :", "pdflib_x": 495.29, "pdflib_y": 724.63 },
    { "label": "體溫 :", "pdflib_x": 114.5, "pdflib_y": 709.0 },
    { "label": "心跳 :", "pdflib_x": 198.61, "pdflib_y": 709.0 },
    { "label": "呼吸:", "pdflib_x": 295.13, "pdflib_y": 709.0 },
    { "label": "血壓 :", "pdflib_x": 397.68, "pdflib_y": 709.0 },
    { "label": "SPO2(RA):", "pdflib_x": 529.01, "pdflib_y": 709.0 },
    { "label": "預定手術日期_年", "pdflib_x": 178.67, "pdflib_y": 693.04 },
    { "label": "預定手術日期_月", "pdflib_x": 254.69, "pdflib_y": 693.04 },
    { "label": "預定手術日期_日", "pdflib_x": 320.68, "pdflib_y": 693.04 },
    { "label": "手術主治醫師 :", "pdflib_x": 450.58, "pdflib_y": 693.04 },
    { "label": "術前診斷 :", "pdflib_x": 138.62, "pdflib_y": 677.08 },
    { "label": "預計手術名稱 :", "pdflib_x": 162.76, "pdflib_y": 661.47 },
    { "label": "WBC :", "pdflib_x": 112.13, "pdflib_y": 448.72 },
    { "label": "Hb :", "pdflib_x": 99.37, "pdflib_y": 432.73 },
    { "label": "PLT :", "pdflib_x": 105.05, "pdflib_y": 400.81 },
    { "label": "PT :", "pdflib_x": 98.67, "pdflib_y": 384.83 },
    { "label": "Cre :", "pdflib_x": 286.73, "pdflib_y": 384.83 },
    { "label": "Glu :", "pdflib_x": 456.73, "pdflib_y": 384.83 }
];

const app = {
    state: {
        surgeries: [],
        currentPatient: null,
        currentDetails: { vitals: null, extended: null },
        evalData: {},
        resources: { pdf: null, fontTC: null, fontLatin: null }
    },

    init() {
        this.bindEvents();
        this.setDefaultDate();
        console.log("App Initialized v2 (Full Rebuild)");
    },

    bindEvents() {
        document.getElementById('btnSearch').onclick = () => this.fetchSchedule();
        document.getElementById('searchKeyword').oninput = () => this.applyFilters();
        document.getElementById('filterRoom').onchange = () => this.applyFilters();
        document.getElementById('btnSaveEval').onclick = () => this.saveEvaluation();
        document.getElementById('btnGenPdf').onclick = () => this.generatePdf();
        document.getElementById('panelBackdrop').onclick = (e) => {
            if (e.target.id === 'panelBackdrop') this.closePanel();
        };
    },

    setDefaultDate() {
        document.getElementById('searchDate').value = new Date().toISOString().split('T')[0];
    },

    async fetchSchedule() {
        const date = document.getElementById('searchDate').value;
        const grid = document.getElementById('scheduleGrid');
        grid.innerHTML = '<div class="glass-card" style="grid-column: 1/-1; text-align: center;"><div class="skeleton" style="height: 100px;"></div><p>載入中...</p></div>';
        try {
            const res = await fetch('/api/surgery_list', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ date })
            });
            this.state.surgeries = await res.json() || [];
            this.populateRooms();
            this.applyFilters();
        } catch (e) {
            grid.innerHTML = `<div class="glass-card" style="grid-column: 1/-1; color: var(--danger);">載入失敗: ${e.message}</div>`;
        }
    },

    populateRooms() {
        const rooms = [...new Set(this.state.surgeries.map(s => s.OROPROOM).filter(Boolean))].sort();
        const select = document.getElementById('filterRoom');
        select.innerHTML = '<option value="">全部房號</option>';
        rooms.forEach(r => {
            const opt = document.createElement('option');
            opt.value = r; opt.textContent = `房號: ${r}`;
            select.appendChild(opt);
        });
    },

    applyFilters() {
        const kw = document.getElementById('searchKeyword').value.toLowerCase();
        const room = document.getElementById('filterRoom').value;
        const filtered = this.state.surgeries.filter(s => {
            const match = (s.HNAMEC || '').toLowerCase().includes(kw) || (s.HHISTNUM || '').includes(kw);
            return match && (!room || s.OROPROOM === room);
        });
        this.renderSchedule(filtered);
    },

    renderSchedule(list) {
        const grid = document.getElementById('scheduleGrid');
        if (list.length === 0) { grid.innerHTML = '<div class="glass-card" style="grid-column: 1/-1; text-align: center;">查無資料</div>'; return; }
        grid.innerHTML = list.map(s => {
            const isFin = s.PREANEASSESFIN === 'Y' || s.PREANEASSESFIN === '完';
            return `
                <div class="glass-card surgery-item ${isFin ? 'status-done' : ''} ${s.EMG ? 'is-emg' : ''}" onclick="app.openDetail('${s.ORDSEQ}')">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <span class="room-tag">${s.OROPROOM || '??'}</span>
                        <span class="badge ${isFin ? 'badge-success' : ''}">${isFin ? '已評估' : '未評估'}</span>
                    </div>
                    <div><h3>${s.HNAMEC || 'Unknown'} (${s.HHISTNUM})</h3><p class="procedure-text">${s.ORDPROCED || '無紀錄'}</p></div>
                    <div style="margin-top: 10px; font-size: 0.8rem; color: var(--text-muted);"><i class="far fa-clock"></i> ${s.OP_TIME || '--:--'} | ${s.ANENM || '待定'}</div>
                </div>`;
        }).join('');
    },

    async openDetail(ordSeq) {
        const surgery = this.state.surgeries.find(s => s.ORDSEQ === ordSeq);
        if (!surgery) return;
        this.state.currentPatient = surgery;
        this.state.currentDetails = { vitals: null, extended: null };
        this.state.evalData = {}; // Reset local eval

        document.getElementById('panelBackdrop').classList.add('active');
        document.getElementById('pDetailName').textContent = surgery.HNAMEC;
        document.getElementById('pDetailMeta').textContent = `病歷號: ${surgery.HHISTNUM} | 就診號: ${surgery.HCASENO || '--'}`;

        const content = document.getElementById('pDetailContent');
        content.innerHTML = '<div class="skeleton" style="height: 200px;"></div><p>載入 Vitals/Labs...</p>';

        try {
            const vRes = await fetch('/api/details', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ordseq: ordSeq, hhistnum: surgery.HHISTNUM, section: 'vitals' }) });
            this.state.currentDetails.vitals = await vRes.json();
            this.renderPanelContent(true);

            const eRes = await fetch('/api/details', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ordseq: ordSeq, hhistnum: surgery.HHISTNUM, section: 'extended' }) });
            this.state.currentDetails.extended = await eRes.json();
            this.renderPanelContent(false);

            await this.loadSavedEvaluation(surgery.HHISTNUM);
        } catch (e) { content.innerHTML = `<div style="color:var(--danger)">載入失敗: ${e.message}</div>`; }
    },

    closePanel() { document.getElementById('panelBackdrop').classList.remove('active'); },

    renderPanelContent(isLoadingExt) {
        const content = document.getElementById('pDetailContent');
        const v = this.state.currentDetails.vitals || {};
        const pre = v.predata || {};
        const labs = v.lab_data || {};
        const findV = (l, k) => (l && l.length > 0) ? l[0][k] : '--';

        content.innerHTML = `
            <div class="section-head">生命徵象 (Vitals)</div>
            <div class="vitals-grid">
                <div class="vital-card"><div class="vital-label">HR/BP</div><div class="vital-value">${findV(pre.VITALSIGN_PULSEVALUE, 'PULSEVALUE')} / ${findV(pre.VITALSIGN_SBPDBPVALUE, 'SBPVALUE')}</div></div>
                <div class="vital-card"><div class="vital-label">SpO2</div><div class="vital-value">${findV(pre.VITALSIGN_SPO2, 'SPO2')}%</div></div>
                <div class="vital-card"><div class="vital-label">身高/體重</div><div class="vital-value">${findV(pre.VITALSIGN_HEIGHT, 'HEIGHT')}/${findV(pre.VITALSIGN_WEIGHT, 'WEIGHT')}</div></div>
            </div>
            <div class="section-head">檢驗精華 (Lab Data)</div>
            <div class="glass-card" style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 10px; font-size: 0.9rem;">
                <div>Hb: ${labs.HB || '--'}</div><div>PLT: ${labs.PLT || '--'}</div><div>PT/INR: ${labs.PT || '--'}/${labs.INR || '--'}</div>
                <div>K+: ${labs.K || '--'}</div><div>Cre: ${labs.CRE || '--'}</div><div>Glu: ${labs.GLUCOSE || '--'}</div>
            </div>
            <div id="evalSection">
                <div class="section-head">麻醉評估核心 (Assessment)</div>
                ${this.renderEvaluationForm()}
            </div>
            ${isLoadingExt ? '<div style="margin-top:20px; text-align:center;"><i class="fas fa-spinner fa-spin"></i> 載入病史中...</div>' : ''}
        `;
    },

    renderEvaluationForm() {
        const sections = [
            { id: 'cvs', title: '心血管系統', items: ['Hypertension', 'CAD', 'Heart Failure', 'Arrhythmia'] },
            { id: 'neuro', title: '神經精神系統', items: ['CVA', 'Seizure', 'Dementia'] },
            { id: 'resp', title: '呼吸系統', items: ['Asthma', 'COPD', 'Smoking'] },
            { id: 'airway', title: '呼吸道評估', items: ['Mallampati 3/4', 'Difficult Airway', 'Loose Teeth'] },
            { id: 'plan', title: '麻醉計畫', items: ['ETGA', 'LMA', 'Spinal', 'Epidural', 'TCI'] }
        ];
        return sections.map(s => `
            <div class="collapsible-section" id="sec_${s.id}">
                <div class="collapsible-trigger" onclick="this.parentElement.classList.toggle('open')">${s.title} <i class="fas fa-chevron-down"></i></div>
                <div class="collapsible-body">
                    ${s.items.map(item => `
                        <div class="form-group">
                            <label style="display:flex; align-items:center; gap:8px;"><input type="checkbox" name="${s.id}_${item}" onchange="app.saveEvalState()"> ${item}</label>
                            <input type="text" placeholder="Note..." name="note_${s.id}_${item}" oninput="app.saveEvalState()" style="width:100%; margin-top:4px;">
                        </div>`).join('')}
                </div>
            </div>`).join('');
    },

    saveEvalState() {
        const inputs = document.querySelectorAll('#evalSection input');
        inputs.forEach(i => {
            const val = i.type === 'checkbox' ? i.checked : i.value;
            this.state.evalData[i.name] = val;
            const sec = i.closest('.collapsible-section');
            if (val && val !== false) sec.classList.add('has-data');
        });
    },

    async saveEvaluation() {
        if (!this.state.currentPatient) return;
        try {
            await fetch('/api/save_eval', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ patient_id: this.state.currentPatient.HHISTNUM, data: this.state.evalData }) });
            alert("已暫存伺服器");
        } catch (e) { alert("失敗: " + e.message); }
    },

    async loadSavedEvaluation(pid) {
        try {
            const res = await fetch('/api/get_eval', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ patient_id: pid }) });
            const saved = await res.json();
            if (saved.data) {
                this.state.evalData = saved.data;
                Object.keys(saved.data).forEach(k => {
                    const i = document.querySelector(`[name="${k}"]`);
                    if (i) {
                        if (i.type === 'checkbox') i.checked = saved.data[k]; else i.value = saved.data[k];
                        if (saved.data[k]) i.closest('.collapsible-section').classList.add('has-data');
                    }
                });
            }
        } catch (e) { console.error("Load failed", e); }
    },

    async prepareResources() {
        if (this.state.resources.pdf) return;
        const btn = document.getElementById('btnGenPdf');
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 準備資源...';
        try {
            const [pdf, tc, lat] = await Promise.all([
                fetch('https://MDJimmyFu.github.io/FJUHOR/PreAnesEval.pdf').then(r => r.arrayBuffer()),
                fetch('https://raw.githubusercontent.com/google/fonts/main/ofl/notosanstc/NotoSansTC%5Bwght%5D.ttf').then(r => r.arrayBuffer()),
                fetch('https://raw.githubusercontent.com/google/fonts/main/ofl/notosans/NotoSans%5Bwdth%2Cwght%5D.ttf').then(r => r.arrayBuffer())
            ]);
            this.state.resources = { pdf, fontTC: tc, fontLatin: lat };
            btn.innerHTML = '<i class="fas fa-file-pdf"></i> 產生評估單';
        } catch (e) { alert("資源載入失敗: " + e.message); btn.innerHTML = '重試 PDF'; }
    },

    async generatePdf() {
        await this.prepareResources();
        try {
            const { pdf, fontTC: tcB, fontLatin: latB } = this.state.resources;
            const pdfDoc = await PDFLib.PDFDocument.load(pdf);
            pdfDoc.registerFontkit(fontkit);
            const fontTC = await pdfDoc.embedFont(tcB);
            const fontLat = await pdfDoc.embedFont(latB);
            const page = pdfDoc.getPages()[0];
            const patient = this.state.currentPatient;
            const vitals = this.state.currentDetails.vitals || {};
            const labs = vitals.lab_data || {};

            const draw = (txt, x, y, sz = 10) => page.drawText(String(txt || ''), { x, y, size: sz, font: fontLat });
            const drawTC = (txt, x, y, sz = 10) => page.drawText(String(txt || ''), { x, y, size: sz, font: fontTC });

            // Basic Mapping
            draw(patient.HHISTNUM, 121, 741);
            drawTC(patient.HNAMEC, 235, 741);
            draw(patient.HCASENO, 496, 741);
            draw(patient.AGE, 114, 724);
            draw(patient.HSEXE, 312, 724);

            // Labs mapping
            draw(labs.HB, 99, 432);
            draw(labs.PLT, 105, 400);
            draw(labs.K, 447, 432);
            draw(labs.CRE, 286, 384);

            // Checkboxes from evaluation
            const check = (x, y) => page.drawText('V', { x, y, size: 14, font: fontLat });
            if (this.state.evalData['cvs_Hypertension']) check(227, 613);
            if (this.state.evalData['resp_Asthma']) check(227, 585);

            const pdfBytes = await pdfDoc.save();
            const blob = new Blob([pdfBytes], { type: 'application/pdf' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `Eval_${patient.HHISTNUM}.pdf`;
            link.click();
        } catch (e) { alert("PDF 錯誤: " + e.message); }
    }
};

window.onload = () => app.init();
