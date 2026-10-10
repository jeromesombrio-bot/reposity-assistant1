# Reflection & Emerging Tech Analysis

1. **Responsibility & Safeguards**:
   If the assistant provides an incorrect deadline causing a student to miss enrollment, ultimate operational responsibility lies with the institution (Bayanihan College). However, to prevent this, a critical safeguard before a live launch is adding a visible legal disclaimer on the chat UI emphasizing that AI outputs are informational only, paired with a mandatory fallback link directly to the official, verified Registrar Bulletin Board.

2. **Dataset Bias & Mitigation**:
   Training the classifier on only 50 self-written questions introduces author bias, failing to capture real student slang, typos, regional dialects, or complex Taglish phrasing. To fix this, I would replace the synthetic dataset with anonymized historical logs from Bayanihan College's Facebook page queries, continually retraining the model using real-world student inputs.

3. **Data Privacy Act of 2012 (RA 10173)**:
   Under RA 10173, the school must present a clear Privacy Notice on the chat interface informing users how their input data is processed. The system must strictly avoid storing Personally Identifiable Information (PII) such as full names, student ID numbers, phone numbers, or email addresses in plain text logs or database tables.

4. **Emerging Technology Extension (Blockchain)**:
   Blockchain technology could be used to issue cryptographic, tamper-proof digital credentials (such as Certificates of Enrollment or Grade Transcripts) directly accessible via the chat assistant interface. However, this implementation is likely not worth the operational expense due to high gas/transaction fees, complex key management for non-technical students, and the efficiency of existing centralized school database systems.