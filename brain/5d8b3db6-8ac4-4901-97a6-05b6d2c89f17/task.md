# Add Intubation Prescription

- [x] Analyze `intubation.pcapng` and `intubationinfection.pcapng` to extract API payloads.
- [x] Determine differences between regular and infection intubation procedures. (Regular: TR001210, Infection: TR001209)
- [x] Create/Update JSON logic for Intubation.
- [x] Update `his_client.py` to support intubation (no PDF needed).
- [x] Update `app.py` to support `INTUBATION` packageType.
- [x] Update frontend UI `templates/index.html` to add Intubation button(s).
- [x] Analyze `painless.pcapng` for check vital sign orders.
- [x] Implement `prescribe_painless_vitals` in `his_client.py`.
- [x] Integrate vitals orders into `app.py` after painless medication prescription.
