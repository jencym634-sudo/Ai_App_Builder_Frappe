<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f2027,50:7aa2f7,100:2c5364&height=220&section=header&text=AI%20App%20Builder&fontSize=45&fontColor=ffffff"/>
</p>

<h1 align="center"> AI-Powered ERP Application Builder</h1>

<p align="center">
Generate complete ERP applications from natural language using AI and the Frappe Framework.
</p>

<p align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Frappe](https://img.shields.io/badge/Frappe-v15-green)
![OpenRouter](https://img.shields.io/badge/OpenRouter-AI-purple)
![License](https://img.shields.io/badge/License-MIT-orange)

</p>

---

# Overview

AI App Builder is an intelligent application generation platform built using the **Frappe Framework** that converts natural language business requirements into complete ERP applications.

Instead of manually creating DocTypes, Workflows, Reports, APIs, and backend logic, users simply describe their business requirements. The platform automatically analyzes the request, generates a structured blueprint, validates it, applies self-healing when necessary, and produces a production-ready Frappe application.

---

#  Features

-  Natural Language → ERP Application
-  Automatic App Generation
-  AI Generated DocTypes
-  Child Tables & Relationships
-  Workflow Generation
-  Reports & Dashboards
-  Print Formats
-  REST API Generation
-  Jinja Templates
-  Validation Engine
-  Self-Healing Engine
-  Safe Schema Upgrade Engine
-  Multi-LLM Support
-  OpenRouter Integration

---

#  Architecture

```text
                 User Prompt
                      │
                      ▼
          AI Integration Layer
                      │
        ┌─────────────┴──────────────┐
        │                            │
 OpenRouter                    Multiple LLMs
        │                            │
        └─────────────┬──────────────┘
                      │
                      ▼
            Blueprint Generator
                      │
                      ▼
            Validation Engine
                      │
                      ▼
           Self-Healing Engine
                      │
                      ▼
       Safe Schema Upgrade Engine
                      │
                      ▼
      Frappe App Generation Engine
                      │
                      ▼
        Production ERP Application
```

---

#  Generation Pipeline

```text
Natural Language Prompt
        │
        ▼
Requirement Analysis
        │
        ▼
Blueprint Generation
        │
        ▼
Schema Validation
        │
        ▼
Self-Healing
        │
        ▼
Safe Schema Upgrade
        │
        ▼
Generate Frappe Application
        │
        ▼
Install & Migrate
```

---

#  AI Capabilities

The platform supports multiple Large Language Models through **OpenRouter**.

### Supported Features

- Multi-LLM Architecture
- Automatic Model Failover
- Provider Agnostic Design
- Prompt Templates
- Retry Mechanism
- Response Validation
- Error Recovery

---

#  Technology Stack

## Backend

- Python
- Frappe Framework
- ERPNext
- MariaDB
- Redis

## AI

- OpenRouter
- Multi-LLM Integration
- AI Agents
- Prompt Engineering

## Frontend

- Jinja Templates
- JavaScript

---

#  Project Structure

```text
ai_app_builder/
│
├── ai/
├── api/
├── core/
├── generators/
├── managers/
├── models/
├── validators/
├── self_healing/
├── templates/
├── tests/
└── docs/
```

---

#  Example

### Input

```text
Build a School Management ERP
```

### Output

```text
✔ Student
✔ Teacher
✔ Course
✔ Attendance
✔ Fees
✔ Reports
✔ Print Formats
✔ REST APIs
✔ Workflows
```

---

#  Demo

Watch the complete project demonstration below.

 **Demo Video:** https://drive.google.com/file/d/1tcJL8huEDe9zJFskPdN5oW24DTmHpdPZ/view?usp=drive_link



#  Roadmap

-  AI Integration Layer
-  Blueprint Generation
-  Validation Engine
-  Self-Healing Engine
-  Safe Schema Upgrade
-  Authentication
-  Visual Blueprint Editor
-  Plugin Marketplace

---

#  Contributing

Contributions, feature requests, and suggestions are welcome.

If you find a bug or have an idea for improvement, feel free to open an Issue or submit a Pull Request.

---

#  License

MIT License

---

#  Author

**Jency M**

Python Software Engineer • Frappe Framework Developer • AI-Powered ERP Applications

-  LinkedIn: https://linkedin.com/in/jency-m-31291735a
-  GitHub: https://github.com/jencym634-sudo
-  Email: jencym634@gmail.com

---

<p align="center">
⭐ If you found this project interesting, consider giving it a star!
</p>

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:2c5364,100:0f2027&height=120&section=footer"/>
</p>
