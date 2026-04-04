# incident-ddr-automation
Post‑Incident Review Automation Tool and Detect → Diagnose → Recover (DDR) workflow.

# Incident DDR Automation

## Overview

Incident management within large organisations often relies on unstructured collaboration data generated during live incidents. Reconstructing accurate timelines and producing Post‑Incident Reviews (PIRs) is therefore time‑consuming and prone to inconsistency.

The **Incident DDR Automation** project addresses this challenge by providing an API‑based automation tool that supports the **Detect → Diagnose → Recover (DDR)** workflow. The application extracts incident‑related chat data, normalises it into a structured timeline, classifies events by DDR phase, and generates structured prompts to support efficient, blameless Post‑Incident Reviews.

This repository was developed as part of a Software Testing and Quality Assurance summative assessment and intentionally focuses on **testing strategy, quality assurance, and risk‑based evaluation**, rather than production‑grade feature completeness.

---

## Key Capabilities

- Pull incident‑specific chat messages for a defined time window  
- Extract and normalise incident timelines from unstructured text  
- Classify events into Detect, Diagnose, and Recover phases  
- Generate structured DDR prompts to support Post‑Incident Reviews  
- Provide a testable, auditable API suitable for organisational integration  

---

## Architecture Overview

The application is implemented as a **RESTful API** using Python and FastAPI.  
It exposes three primary endpoints:

- `POST /chats/pull` – Retrieve chat messages for an incident window  
- `POST /timeline/extract` – Extract and classify a DDR‑aligned incident timeline  
- `POST /prompts` – Generate structured PIR prompts based on the extracted timeline  

The system has no user interface and is designed to be consumed by internal tooling or analysts.

---

## Testing and Quality Assurance Focus

A comprehensive testing strategy is applied across the Software Development Life Cycle (SDLC), including:

- Static testing and code inspection  
- Unit testing of core logic  
- Integration testing across API components  
- System and end‑to‑end testing of the DDR workflow  
- Regression testing to support iterative enhancement  
- Performance testing for scalability risks  
- User Acceptance Testing (UAT) aligned to incident management practices  

Testing artefacts, defect logs, and traceability matrices are included to support auditability and quality evaluation.

---

## Disclaimer

This project is an academic artefact created for assessment purposes.  
It is not intended for direct production use without additional security, performance, and governance controls.


incident-ddr-automation/
│
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI entry point
│   ├── models.py            # Pydantic models
│   ├── services/
│   │   ├── chat_ingest.py   # Chat retrieval logic
│   │   ├── timeline.py      # Timeline extraction logic
│   │   └── ddr_mapper.py    # Detect / Diagnose / Recover classification
│   └── utils.py             # Shared helpers
│
├── tests/
│   ├── unit/
│   │   ├── test_ddr_mapper.py
│   │   ├── test_timeline.py
│   │   └── test_validation.py
│   ├── integration/
│   │   └── test_api_flows.py
│   └── system/
│       └── test_end_to_end_ddr.py
│
├── uat/
│   ├── uat_scenarios.md     # Manual UAT scripts and acceptance criteria
│   └── uat_results.md
│
├── qa/
│   ├── test_plan.md
│   ├── defect_log.md
│   ├── requirements_traceability_matrix.md
│
├── docs/
│   ├── architecture.md
│   └── testing_strategy.md
│
├── requirements.txt
├── README.md
└── .gitignore
