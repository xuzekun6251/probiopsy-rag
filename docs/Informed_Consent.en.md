# Informed Consent Form — 前列安汇 (probiopsy-rag)

> **⚠️ Scope Note**:
> - **Retrospective study (Huanyu default)**: Consent typically **waived**; this template **not used**
> - **Prospective / biospecimen / follow-up**: **Mandatory** written consent using this template
> - **Special populations**: Add guardian consent + child assent sections
>
> This is a template; PI + IRB review required before submission.

---

## Informed Consent Form (Participant Version)

### Study Title

前列安汇: A rule-engine + knowledge-graph + LLM-arbiter decision support system for LightRAG混合决策支持系统:患者临床情境×穿刺决策项 screening

### Investigator Information

- **Principal Investigator**: [TODO: pi_name] ([TODO: pi_title])
- **Institution**: [TODO: pi_department], [TODO: hospital_name]
- **Contact**: [TODO: pi_email] / [TODO: pi_phone]
- **IRB Approval No.**: [TODO: irb_approval_id]
- **Funder**: [TODO: funding_source]

---

### 1. Purpose

We invite you to participate in research on LightRAG混合决策支持系统:患者临床情境×穿刺决策项. This study aims to build an intelligent system to help clinicians assess potential interactions between 穿刺决策项 and 患者临床情境要素, enabling personalized health recommendations.

Expected enrollment: **0** participants.

---

### 2. Procedures

If you agree to participate, we will:

1. **Collect your medical records** (from previous visits through study end):
   - Demographics: Age band, sex, clinic
   - Diagnosis: Specific 患者临床情境要素 subtype
   - Exposure history: Occupation, lifestyle (smoking / alcohol / diet)
   - Lab results: Relevant hormone levels

2. **Possible additional assessments** (prospective only):
   - Questionnaire: Detailed exposure history (~30 minutes)
   - Biospecimen: [TODO: sample_type] (if collected, separate risk/benefit statement)

3. **Follow-up** (if applicable):
   - Frequency: [TODO: followup_frequency]
   - Mode: Outpatient / phone / online
   - Total duration: [TODO: followup_total_duration]

4. **Data use**:
   - All personal data will be **de-identified**
   - Only de-identified data used for modeling and publication
   - Data stored at 本地工作站(加密磁盘),仅使用公开数据 for 5 years

**Estimated total participation time**: [TODO: total_participation_time]

---

### 3. Risks & Discomforts

**Common risks** (minor):
- **Privacy risk**: Despite de-identification, theoretical re-identification risk remains (very low)
- **Psychological discomfort**: Some questions may cause emotional response (e.g., infertility-related stress)
- **Time burden**: Questionnaires and follow-up consume personal time

**Biospecimen-related risks** (if applicable):
- Blood draw: Mild pain, bruising, very low infection risk
- Other samples: [TODO: sample_risks]

**LLM / AI risks**:
- AI models (DeepSeek, GPT-4) may produce incorrect outputs
- **Mitigation**: AI is decision support only; clinical judgment remains with physician

**Risk of non-participation**: None (your medical care is **not affected** by participation)

---

### 4. Benefits

**Direct benefits** (uncertain):
- You may receive additional 患者临床情境要素 risk assessment
- Your physician may gain decision-support information

**Indirect benefits**:
- Contributes to medical knowledge
- Helps improve future patient care

**Compensation** (if applicable):
- Time: [TODO: compensation_per_visit] per visit
- Travel: [TODO: travel_compensation]
- Maximum: [TODO: total_compensation_cap]

---

### 5. Alternatives

You may choose **not to participate**. Standard medical care continues regardless.

---

### 6. Voluntariness

Participation is **entirely voluntary**. You may:
- Decline without affecting your medical care
- Withdraw at any time without giving reasons
- After withdrawal, previously collected data continues to be used (unless you request destruction)

---

### 7. Confidentiality

- All data **de-identified** (HIPAA Safe Harbor standard)
- Encrypted in transit (TLS 1.3) and at rest (AES-256)
- Only authorized researchers have access
- Publications never reveal your identity
- Data destroyed 5 years post-study

**Exception**: IRB or regulatory authorities may review research records (still protected)

---

### 8. Data Use & Sharing

- **Domestic use**: Research team and collaborators
- **International sharing**: Only de-identified data via Zenodo / OSF (DOI)
- **Commercial use**: Your data **not** sold to commercial entities
- **AI training**: Your data **not** used for LLM training

---

### 9. Participant Rights

You have the right to:
- Be informed of purpose, risks, benefits (this document fulfills this obligation)
- Decline or withdraw at any time
- Request a copy of your data
- Correct inaccurate data
- Ask questions or file complaints ([TODO: irb_contact_email])

---

### 10. Injury Compensation

If injured due to study participation (prospective / interventional only):

- Free medical treatment
- Compensation per [TODO: injury_compensation_policy]

---

### 11. New Information

Any new information affecting your decision will be communicated promptly.

---

### 12. Contacts

| Purpose | Contact | Phone / Email |
|---|---|---|
| Research questions | [TODO: pi_name] | [TODO: pi_phone] / [TODO: pi_email] |
| Participant rights | IRB office | [TODO: irb_contact_phone] / [TODO: irb_contact_email] |
| Emergency | 24h hotline | [TODO: emergency_hotline] |

---

### Participant Signature

I have read (or had read to me) the above information, all my questions have been satisfactorily answered, and I voluntarily consent to participate.

- **Participant signature**: ____________________
- **Name (printed)**: ____________________
- **Last 4 of national ID**: ____________________
- **Date**: ____ / __ / ____

---

### Investigator Signature

I have fully explained this study to the participant, confirmed their understanding, and obtained voluntary consent.

- **Investigator signature**: ____________________
- **Name**: ____________________
- **Date**: ____ / __ / ____

---

## Appendix: Guardian Consent (Minors)

For participants < 18 years, guardian signature + child assent required:

**Guardian consent**:
"As the [relationship: __] of the above minor and their legal guardian, I understand this research and consent on their behalf."

- Guardian signature: ____________________
- Date: ____ / __ / ____

**Child assent (≥ 7 years)**:
"The researcher explained this study in a way I can understand, and I agree to participate."

- Child signature: ____________________
- Date: ____ / __ / ____

---

## Appendix: Project-Specific Notes (PI completes)

[TODO: project_specific_consent_notes]
