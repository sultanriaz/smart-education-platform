# COMSATS University Islamabad, Sahiwal Campus, Pakistan
## Department of Computer Science

---

# SmartEdu
### An Enterprise-Scale Distributed Academic Platform with Universal Campus Gateway, Autonomous Gemini RAG Self-Learning Studio, and Integrated Institutional Governance

---

**A project presented to**  
**COMSATS University Islamabad, Sahiwal Campus**  
*In partial fulfillment of the requirement for the degree of*  
**Bachelor of Science in Computer Science (2023–2027)**

---

**By**

| Student Name | Registration Number |
| :--- | :--- |
| **Ali Hassan** | CIIT/SP23-BCS-000/SWL |
| **Saba Mustafa** | CIIT/SP23-BCS-000/SWL |

---

### DECLARATION

We hereby declare that this software, neither whole nor as a part, has been copied out from any source. It is further declared that we have developed this software and the accompanying report entirely on the basis of our personal efforts. If any part of this project is proved to be copied out from any source or found to be a reproduction of some other work, we will stand by the consequences. No portion of the work presented has been submitted in support of any application for any other degree or qualification of this or any other university or institute of learning.

<br />

| Ali Hassan | Saba Mustafa |
| :--- | :--- |
| ____________________ | ____________________ |

---

### CERTIFICATE OF APPROVAL

This is to certify that the final year project of BS (CS) **“SmartEdu”** was developed by **ALI HASSAN** and **SABA MUSTAFA**, under the supervision of **“Ms. SAMRA FIRDOUS”** and that in her opinion it is fully adequate, in scope and quality, for the degree of Bachelor of Science in Computer Science.

<br />

_____________________________  
**Supervisor**  
**Ms. Samra Firdous**  
Lecturer / Assistant Professor  
Department of Computer Science  
COMSATS University Islamabad, Sahiwal Campus  

<br />

_____________________________  
**External Examiner**  
Dr.  
Assistant Professor  
Department of Computer Science  

<br />

_____________________________  
**Head of Department**  
**Dr. Zafar Iqbal Roy**  
Assistant Professor / Incharge Department of Computer Science  
COMSATS University Islamabad, Sahiwal Campus  

---

### Executive Summary

The modern higher-education ecosystem is plagued by operational fragmentation, cognitive overload, and disconnected data silos. Students, faculty, and administrative officers navigate disjointed portals, static PDF schedules, uncoordinated transit networks, and ad-hoc physical classroom hunting. Furthermore, although generative artificial intelligence has emerged as a transformative pedagogical tool, prevailing commercial chatbots act as ungrounded, hallucination-prone conversationalists detached from university-specific syllabi, grading rubrics, and formal assessment standards.

**SmartEdu** is an enterprise-scale, cloud-native educational intelligence and institutional governance platform designed to resolve institutional friction. Built on a decoupled microservices architecture with a unified serverless API Gateway, SmartEdu integrates twelve domain-driven backend microservices, a responsive React 19 / TypeScript / Vite frontend, and an autonomous AI Self-Learning Studio powered by Google Gemini and LangGraph.

At the client boundary, SmartEdu introduces the **Universal Adaptive Campus Gateway**, providing public, frictionless access to campus telemetry without mandatory credentials. Users explore eight core operational modules:
1. **Student Academic Cockpit & Course Command Centers**: Consolidating course operations into high-density interactive cards with regulatory HEC attendance thresholds ($\ge 75\%$) and eight sub-cards (*Assignments, Quizzes, Attendance, Marks, Notifications, Resources, Lecture Hub, Course Information*).
2. **Intelligent Timetable & Schedule Engine**: Adaptive day timelines with moving current-time markers, section-based and teacher-based schedule matrices, hall capacities, and 1-click `.ics` calendar synchronization.
3. **Dynamic Space Finder & Free Slot Navigator**: Real-time empty room discovery across Block A, Block B, Block C, Block D, and Engineering Labs with equipment telemetry and 90-minute study reservation holds.
4. **Smart Transit & Fleet Telemetry**: Live city commuter routes (*Farid Town Point, Mall Road Express, Canal Line*) and intra-campus loops with stop-by-stop ETAs, vehicle capacities, and disruption bulletins.
5. **Campus Hub, Directory & Spatial Wayfinding**: Centralized directory spanning Faculty, Administrative Offices with live queue token counters, Classrooms, Specialized Labs with equipment inventories, Library study-seat meters, and interactive SVG floor blueprints.
6. **Campus Life, Marquee Events & Sports Gala Portal**: Dynamically morphing calendar portal supporting Spring Sports Week, Fall Tech Hackathons, and Winter Convocation/Career Fairs with live fixture timelines, elimination knockout brackets, and department trophy standings.
7. **AI Self-Learning & Adaptive Assessment Studio**: Autonomous student-driven learning workspace leveraging Google Gemini (`gemini-2.0-flash` and `text-embedding-004`) via a cyclical LangGraph state machine. It features multi-format document ingestion (PDF, DOCX, PPTX), semantic vector retrieval with `pgvector`, Bloom's Taxonomy test generation, step-by-step KaTeX mathematical derivations, SVG Topic Mastery Radar charts, and 1-click weakness-targeted test regeneration.
8. **Institutional Governance, Double-Entry Finance & Automated Payroll**: Institutional ERP subsystem enforcing strict double-entry general ledger balance ($\sum \text{Debits} = \sum \text{Credits}$), multi-part installment billing, late penalty schedulers, maker-checker dual control on refunds and payroll runs, and simulated 1Link banking settlements.

Security and resilience are architected at every tier: Ed25519 cryptographic inter-service tokens, RS256 JWT client authentication, SHA-256 document deduplication with 100MB per-student storage quotas, database schema isolation across 12 services, and zero-network JWKS mock interception in serverless environments. Verified across 1,864 backend test cases, 41 frontend unit/contract test suites, and extensive Playwright browser journeys, SmartEdu represents a complete, robust, and standards-compliant campus management ecosystem.

---

### Acknowledgment

All praise is due to Almighty Allah, the Most Beneficent, the Most Merciful, who bestowed upon us the knowledge, perseverance, and intellectual capability to accomplish this challenging final year project.

We express our deepest gratitude and indebtedness to our esteemed project supervisor, **Ms. Samra Firdous**, whose invaluable guidance, academic rigor, constructive critique, and continuous encouragement steered this research and development endeavor from conceptualization to fruition. Her patient mentorship and insightful recommendations ensured our architecture adhered to highest industry standards.

We extend our sincere thanks to **Dr. Zafar Iqbal Roy**, Head of the Computer Science Department, and all respected faculty members of COMSATS University Islamabad, Sahiwal Campus, for providing an enriching academic environment and foundational knowledge throughout our undergraduate studies.

Lastly, our heartfelt appreciation goes to our beloved parents and families, whose endless prayers, unwavering moral support, and sacrifices have been our perpetual source of inspiration and strength.

<br />

| Ali Hassan | Saba Mustafa |
| :--- | :--- |
| ____________________ | ____________________ |

---

### Abbreviations

| Abbreviation | Full Form |
| :--- | :--- |
| **AES** | Advanced Encryption Standard |
| **AI** | Artificial Intelligence |
| **API** | Application Programming Interface |
| **ASCII** | American Standard Code for Information Interchange |
| **ASGI** | Asynchronous Server Gateway Interface |
| **CRUD** | Create, Read, Update, Delete |
| **CSP** | Content Security Policy |
| **CSRF** | Cross-Site Request Forgery |
| **DAG** | Directed Acyclic Graph |
| **DOCX** | Microsoft Word OpenXML Document |
| **DPI** | Dots Per Inch |
| **E2E** | End-to-End Testing |
| **ERD** | Entity Relationship Diagram |
| **ETA** | Estimated Time of Arrival |
| **FIDO2** | Fast Identity Online 2 |
| **FR** | Functional Requirement |
| **GL** | General Ledger |
| **GPA** | Grade Point Average |
| **HEC** | Higher Education Commission of Pakistan |
| **HMAC** | Hash-based Message Authentication Code |
| **HOD** | Head of Department |
| **HTML** | HyperText Markup Language |
| **HTTP** | HyperText Transfer Protocol |
| **HTTPS** | HyperText Transfer Protocol Secure |
| **IDOR** | Insecure Direct Object Reference |
| **IEEE** | Institute of Electrical and Electronics Engineers |
| **JSON** | JavaScript Object Notation |
| **JWT** | JSON Web Token |
| **KaTeX** | Fast Math Typesetting Library for the Web |
| **LLM** | Large Language Model |
| **MCQ** | Multiple Choice Question |
| **NFR** | Non-Functional Requirement |
| **NLP** | Natural Language Processing |
| **NIST** | National Institute of Standards and Technology |
| **OCR** | Optical Character Recognition |
| **OpenAPI** | Specification for Machine-Readable REST APIs |
| **PDF** | Portable Document Format |
| **PPTX** | Microsoft PowerPoint OpenXML Presentation |
| **RAG** | Retrieval-Augmented Generation |
| **RBAC** | Role-Based Access Control |
| **REST** | Representational State Transfer |
| **RSA** | Rivest–Shamir–Adleman Cryptosystem |
| **SHA-256** | Secure Hash Algorithm, 256-bit |
| **SPA** | Single Page Application |
| **SQL** | Structured Query Language |
| **SSE** | Server-Sent Events |
| **SVG** | Scalable Vector Graphics |
| **UI / UX** | User Interface / User Experience |
| **UML** | Unified Modeling Language |
| **URL** | Uniform Resource Locator |
| **UUID** | Universally Unique Identifier |
| **Vite** | Next Generation Frontend Tooling |
| **WAL** | Write-Ahead Logging |
| **WCAG** | Web Content Accessibility Guidelines |

---

### Table of Contents

```text
1 Introduction ................................................................ 1
  1.1 Project and Brief (Brief Overview) ...................................... 1
  1.2 Relevance to Course Modules ............................................. 2
  1.3 Project Background ...................................................... 3
  1.4 Literature Review ....................................................... 4
  1.5 Analysis from Literature Review ......................................... 7
  1.6 Methodology and Software Lifecycle for This Project ..................... 8
  1.7 Rationale Behind Selected Methodology ................................... 9
2 Problem Definition .......................................................... 11
  2.1 Problem Statement ....................................................... 11
  2.2 Deliverables and Development Requirements ............................... 11
      2.2.1 Deliverables ...................................................... 12
      2.2.2 Development Requirements .......................................... 12
            2.2.2.1 Technical Development Requirements ........................ 12
  2.3 Current System .......................................................... 14
3 Requirement Analysis ........................................................ 17
  3.1 Use Case Diagram ........................................................ 17
  3.2 Detailed Use Cases ...................................................... 18
  3.3 Functional Requirements ................................................. 27
  3.4 Non-Functional Requirements ............................................. 33
      3.4.1 Performance ....................................................... 33
      3.4.2 Usability ......................................................... 33
      3.4.3 Security .......................................................... 33
      3.4.4 Reliability ....................................................... 33
      3.4.5 Maintainability ................................................... 34
      3.4.6 Scalability ....................................................... 34
      3.4.7 Portability ....................................................... 34
      3.4.8 Compliance ........................................................ 34
4 Design and Architecture ..................................................... 37
  4.1 System Architecture ..................................................... 37
      4.1.1 Client Layer (Frontend Interface) ................................. 38
      4.1.2 Edge and Security Middleware Layer ................................ 38
      4.1.3 Application Layer (Microservices & Serverless Gateway) ............ 39
      4.1.4 AI and Autonomous Learning Layer .................................. 39
      4.1.5 Data Layer (PostgreSQL, pgvector, Redis & S3) ..................... 39
      4.1.6 Integration Layer (External Banking & Cloud AI) .................. 39
      4.1.7 Communication Flow ................................................ 39
  4.2 Process Flow ............................................................ 40
  4.3 System Modules .......................................................... 42
      4.3.1 Universal Adaptive Gateway & Main Dashboard Module ................ 42
      4.3.2 Student Academic Cockpit & Course Command Center Module ........... 42
      4.3.3 Intelligent Timetable & Schedule Engine Module .................... 42
      4.3.4 Dynamic Space Finder & Free Slot Navigator Module ................. 42
      4.3.5 Smart Transit & Fleet Telemetry Module ............................ 42
      4.3.6 Campus Hub, Directory & Spatial Wayfinding Module ................. 42
      4.3.7 Campus Life, Marquee Events & Sports Gala Portal Module ........... 42
      4.3.8 AI Self-Learning & Adaptive Assessment Studio Module .............. 43
      4.3.9 Identity, Authentication & Role Governance Module ................. 43
      4.3.10 Institutional Finance & General Ledger Module .................... 44
      4.3.11 Automated Payroll & Compensation Module .......................... 44
      4.3.12 Platform Operations, Security & Audit Logging Module ............. 44
  4.4 Design Models ........................................................... 44
      4.4.1 Sequence Diagram .................................................. 44
      4.4.2 Class Diagram ..................................................... 45
5 Implementation .............................................................. 48
  5.1 Algorithms .............................................................. 48
      5.1.1 Multi-Tenant Role-Enforced Login Algorithm ........................ 48
      5.1.2 Multi-Format Document Ingestion & Deduplication Algorithm ......... 49
      5.1.3 LangGraph Bloom's Taxonomy Test Generation Algorithm .............. 49
      5.1.4 Step-by-Step LaTeX Numerical Proof & Audit Algorithm .............. 50
      5.1.5 Topic Mastery Profiling & Cognitive Radar Algorithm ............... 51
      5.1.6 Adaptive Weakness-Remediating Test Regeneration Algorithm .......... 51
      5.1.7 Double-Entry General Ledger Balance & Installment Algorithm ....... 52
      5.1.8 Real-Time Transit Arrival (ETA) Calculation Algorithm ............. 53
  5.2 External APIs and Libraries ............................................. 54
      5.2.1 Google Gemini API & text-embedding-004 ............................ 54
      5.2.2 LangGraph & LangChain StateGraph .................................. 54
      5.2.3 pgvector & PostgreSQL 16 .......................................... 54
      5.2.4 Document Extractors (pypdf, python-docx, python-pptx) ............. 54
      5.2.5 KaTeX & Mathematical Rendering .................................... 54
      5.2.6 FastAPI, Pydantic v2 & SQLAlchemy 2.0 ............................. 55
      5.2.7 PyJWT, Cryptography & Password Hashing ............................ 55
      5.2.8 React 19, TypeScript & Vite ....................................... 55
      5.2.9 Tailwind CSS & Lucide React ....................................... 55
      5.2.10 TanStack Query & React Hook Form ................................. 55
  5.3 User Interface .......................................................... 56
6 Testing and Evaluation ...................................................... 64
  6.1 Manual Testing .......................................................... 64
      6.1.1 System Testing .................................................... 64
      6.1.2 Unit Testing ...................................................... 65
      6.1.3 Functional Testing ................................................ 67
      6.1.4 Integration Testing ............................................... 68
  6.2 Automated Testing ....................................................... 69
7 Conclusion .................................................................. 72
  7.1 Future Work ............................................................. 72
      7.1.1 Mobile Push Notifications & Progressive Web App Offline Mode ...... 72
      7.1.2 Biometric Edge Hardware Integration for Classrooms ................ 72
      7.1.3 Multi-Campus Cross-Federation Protocol ............................ 73
      7.1.4 Urdu Natural Language Interface & Speech Interaction .............. 73
      7.1.5 Automated HEC Compliance & Accreditation Data Exporters ........... 73
      7.1.6 GPS Hardware Transit Telemetry with LoRaWAN Tracking .............. 73
      7.1.7 Advanced Predictive Early-Warning Intervention Engine ............. 73
References .................................................................... 74
Appendix A: API Endpoint Catalog .............................................. 78
Appendix B: Requirement Traceability Matrix ................................... 79
Appendix C: Environment Configuration ......................................... 81
List of Figures ............................................................... 83
List of Tables ................................................................ 84
```

---

### List of Figures

| Figure Number | Caption | Page |
| :--- | :--- | :--- |
| **Figure 3.1** | Use Case Diagram for SmartEdu | 18 |
| **Figure 4.1** | Layered System Architecture of SmartEdu | 38 |
| **Figure 4.2** | Multi-Format Document Ingestion & RAG Indexing Flow | 41 |
| **Figure 4.3** | Cyclical LangGraph Test Generation & Verification Pipeline | 43 |
| **Figure 4.4** | Sequence Diagram for Student Test Generation, Attempt & Grading | 45 |
| **Figure 4.5** | Class Diagram for the SmartEdu Core Educational & Assessment Domain | 46 |
| **Figure 5.1** | Universal Adaptive Gateway & Main Dashboard Interface | 56 |
| **Figure 5.2** | Role-Enforced Student & Faculty Portal Authentication | 57 |
| **Figure 5.3** | Student Academic Cockpit & Course Command Center Dashboard | 57 |
| **Figure 5.4** | Subject Command Center Detail with 8 Sub-Cards | 58 |
| **Figure 5.5** | Intelligent Timetable & Schedule Engine (Student & Teacher Views) | 58 |
| **Figure 5.6** | Dynamic Space Finder & Free Slot Navigator with Telemetry | 59 |
| **Figure 5.7** | Smart Transit & Fleet Telemetry with Stop-by-Stop Itineraries | 59 |
| **Figure 5.8** | Campus Hub Directory & Interactive Vector Spatial Wayfinding | 60 |
| **Figure 5.9** | Campus Life, Marquee Events & Sports Gala Tournament Engine | 60 |
| **Figure 5.10** | AI Self-Learning Studio with Multi-Format Material Vault | 61 |
| **Figure 5.11** | Interactive Test Runner with Bloom's Taxonomy & KaTeX Proofs | 61 |
| **Figure 5.12** | Topic Mastery Profiler with SVG Radar Chart & Smart Regeneration | 62 |

---

### List of Tables

| Table Number | Caption | Page |
| :--- | :--- | :--- |
| **Table 1.1** | Comparison of Existing Educational Platforms with SmartEdu | 6 |
| **Table 2.1** | Tools and Technologies used in SmartEdu | 14 |
| **Table 3.1** | User Registration & Role Onboarding (UC-01) | 18 |
| **Table 3.2** | Multi-Factor Authentication & Role-Enforced Sign-In (UC-02) | 19 |
| **Table 3.3** | Ingest Study Materials into Subject Vault (UC-03) | 20 |
| **Table 3.4** | Generate AI Assessment via Bloom's Taxonomy (UC-04) | 20 |
| **Table 3.5** | Interactive Test Attempt & Timed Submission (UC-05) | 21 |
| **Table 3.6** | Diagnostic Evaluation & Step-by-Step LaTeX Review (UC-06) | 22 |
| **Table 3.7** | Topic Mastery Profiling & Smart Test Regeneration (UC-07) | 22 |
| **Table 3.8** | Query Class Timetable & Export Calendar (UC-08) | 23 |
| **Table 3.9** | Discover & Reserve Free Classroom Space (UC-09) | 24 |
| **Table 3.10** | Inspect Transit Routes & Stop Arrival ETAs (UC-10) | 24 |
| **Table 3.11** | Campus Hub Directory & Office Queue Ticket Tracking (UC-11) | 25 |
| **Table 3.12** | Sports Gala Fixtures & Elimination Tournament Tracking (UC-12) | 25 |
| **Table 3.13** | Student Fee Invoice Checkout & Installment Payment (UC-13) | 26 |
| **Table 3.14** | Institutional Payroll Run & Maker-Checker Approval (UC-14) | 26 |
| **Table 3.15** | Platform Audit Log & System Configuration Inspection (UC-15) | 27 |
| **Table 3.16** | Functional Requirement: Multi-Factor Authentication (FR-001) | 28 |
| **Table 3.17** | Functional Requirement: Multi-Format Document Ingestion (FR-002) | 28 |
| **Table 3.18** | Functional Requirement: Asynchronous Extraction & Deduplication (FR-003) | 28 |
| **Table 3.19** | Functional Requirement: Semantic Embedding & Vector Indexing (FR-004) | 29 |
| **Table 3.20** | Functional Requirement: Bloom's Taxonomy Assessment Generator (FR-005) | 29 |
| **Table 3.21** | Functional Requirement: Step-by-Step LaTeX Proof Solver (FR-006) | 29 |
| **Table 3.22** | Functional Requirement: Diagnostic Grading & Pedagogical Feedback (FR-007) | 30 |
| **Table 3.23** | Functional Requirement: Cognitive Topic Mastery Radar Profiling (FR-008) | 30 |
| **Table 3.24** | Functional Requirement: Weakness-Remediating Test Regeneration (FR-009) | 31 |
| **Table 3.25** | Functional Requirement: Universal Public Gateway Navigation (FR-010) | 31 |
| **Table 3.26** | Functional Requirement: Timetable Matrix & .ics Synchronization (FR-011) | 31 |
| **Table 3.27** | Functional Requirement: Dynamic Room Telemetry & Booking Hold (FR-012) | 32 |
| **Table 3.28** | Functional Requirement: Transit Fleet Tracking & Disruption Notices (FR-013) | 32 |
| **Table 3.29** | Functional Requirement: Double-Entry Financial Ledger & Invoicing (FR-014) | 32 |
| **Table 3.30** | Functional Requirement: Cryptographic Audit Logging & Traceability (FR-015) | 33 |
| **Table 3.31** | Summary of Non-Functional Requirements (NFR-001 to NFR-008) | 34 |
| **Table 5.1** | External APIs and Libraries used in SmartEdu | 55 |
| **Table 6.1** | Manual System Testing Matrix (ST-01 to ST-06) | 65 |
| **Table 6.2** | Unit Testing Specifications & Mathematical Invariants | 66 |
| **Table 6.3** | Functional Testing Results & Acceptance Criteria | 67 |
| **Table 6.4** | Integration Testing Across Microservices & Database Boundaries | 68 |
| **Table 6.5** | Automated Testing Tools and Suite Verification Summary | 70 |
| **Table 6.6** | Automated Testing Execution Results & Quality Gate Audits | 70 |
| **Table A.1** | API Gateway REST Routes and Microservice Dispatch Catalog | 78 |
| **Table B.1** | Comprehensive Requirement Traceability Matrix | 79 |
| **Table C.1** | Runtime Platform Environment Configuration Variables | 81 |

---

# Chapter 1: Introduction

## 1 Introduction
This chapter introduces **SmartEdu**, an enterprise-scale distributed educational intelligence platform engineered to unify university administration, academic course delivery, campus wayfinding, transit telemetry, and autonomous AI-powered student self-learning. It provides a comprehensive project overview, contextualizes its relationship with the core curriculum of the BS (CS) program, delineates the systemic background of modern university ecosystems, reviews prior academic and industrial systems, and substantiates the chosen software development lifecycle methodology.

Higher education institutions operate as complex, multi-stakeholder operational landscapes. On any single instructional day, a university campus coordinates thousands of undergraduate and postgraduate students, hundreds of faculty members, administrative registrars, transit operators, financial accountants, and facility managers. Despite the rapid digital transformation of enterprise sectors, university operations remain predominantly fragmented. Academic timetables are published as unparsed, static PDF documents; physical classrooms sit vacant while student project groups struggle to locate study spaces; commuter shuttle services experience unpredictable urban delays without real-time passenger telemetry; and course learning management systems act as passive file repositories rather than dynamic learning environments.

Furthermore, student assessment in university environments has historically been constrained to periodic, high-stakes formal examinations (midterms and finals). Between these intervals, students lack mechanisms for objective self-evaluation and targeted remediation. While general-purpose commercial Large Language Models (LLMs) have gained popularity among students, their open-ended deployment introduces critical pedagogical risks: hallucinated course guidelines, mathematical proofs with arithmetic inconsistencies, uncalibrated cognitive difficulty, and lack of alignment with approved institutional syllabi. SmartEdu bridges these systemic gaps by providing an integrated, secure, and verifiable platform that standardizes institutional operations while delivering fact-grounded, curriculum-aligned artificial intelligence directly to students.

### 1.1 Project and Brief (Brief Overview)
SmartEdu is a comprehensive web-based platform structured around twelve microservices and an adaptive single-page frontend. Its core purpose is to modernize academic administration and replace disjointed university portals with a cohesive, data-driven, and AI-augmented campus ecosystem.

The platform provides a dual-surface operational paradigm:
1. **The Universal Adaptive Campus Gateway**: A public, frictionless interface allowing students, visiting scholars, and faculty to query campus operational state without credential barriers. Users access real-time transit fleet itineraries with stop-by-stop ETAs, dynamic room availability across campus blocks, master schedule timelines, institutional directories with live administrative queue tokens, and seasonal marquee event tournament brackets.
2. **The Authenticated Role-Enforced Workspace**: A secure, authenticated portal partitioned across three distinct actor roles:
   - **Students**: Equipped with the *Student Academic Cockpit*, tracking regulatory attendance compliance ($\ge 75\%$ HEC exam clearance cutoff), eight consolidated course command cards (*Assignments, Quizzes, Attendance, Marks, Notifications, Resources, Lecture Hub, Course Information*), and the *AI Self-Learning Studio*. The AI Studio enables students to create custom subjects, ingest multi-format documents (PDF, DOCX, PPTX), generate Bloom's Taxonomy-calibrated practice tests via Google Gemini, inspect KaTeX-rendered step-by-step mathematical proofs, visualize mastery on SVG radar charts, and regenerate tests focusing on identified knowledge gaps.
   - **Faculty / Teachers**: Provided with course management tools, bulk attendance marking interfaces, assessment authoring, student gradebooks, assigned class timetables, and personalized monthly payslip inspection.
   - **Institutional Administrators**: Overseeing academic catalog definitions, double-entry general ledger fee accounting with installment plans, human resources payroll with gross-to-net computation, security audit logging, and platform feature flag toggling.

SmartEdu is developed using Python 3.12, FastAPI, and SQLAlchemy for the backend microservices, and React 19, TypeScript 5.9, Vite 8, and Tailwind CSS 4 for the frontend client. Data persistence is governed by PostgreSQL 16 with the `pgvector` extension for semantic vector embeddings, RabbitMQ 4.1 for asynchronous message bus event dispatching, and Redis 7.4 for idempotency caching. The platform runs both as a multi-container Docker Compose topology and as a unified serverless Python deployment on Vercel backed by Neon PostgreSQL.

### 1.2 Relevance to Course Modules
SmartEdu synthesizes practical and theoretical principles across the undergraduate Computer Science curriculum:
- **Software Engineering**: Applying formal software lifecycle models, requirement elicitation, UML structural and behavioral modeling, microservices decomposition, architectural boundary verification, and continuous integration quality gates.
- **Artificial Intelligence & Machine Learning**: Implementing Retrieval-Augmented Generation (RAG) using Google Gemini (`gemini-2.0-flash` and `text-embedding-004`), vector similarity search with Euclidean and cosine metrics in `pgvector`, and multi-agent workflow orchestration using LangGraph.
- **Natural Language Processing**: Extracting multi-format document structures, parsing academic syllabi, semantic chunking with sliding windows, automated topic discovery, and Bloom's Taxonomy classification.
- **Database Systems**: Designing twelve isolated relational database schemas, enforcing third normal form (3NF), executing zero-downtime Alembic schema migrations, configuring connection pooling with Neon PgBouncer, and implementing vector indexing using Hierarchical Navigable Small World (HNSW) graphs.
- **Web Technologies & Frontend Engineering**: Building modern single-page applications with React 19, TypeScript, and Vite, utilizing TanStack Query for cache invalidation, React Hook Form and Zod for schema validation, Tailwind CSS 4 for responsive typography, and KaTeX for high-performance LaTeX formula rendering.
- **Information Security & Cryptography**: Enforcing JSON Web Tokens (JWT) with RS256 client signing and Ed25519 inter-service trust delegation, Argon2id password hashing, cryptographic document deduplication via SHA-256, Cross-Origin Resource Sharing (CORS) origin restrictions, and append-only tamper-evident audit logging.
- **Distributed Systems & Computer Networks**: Designing asynchronous event-driven microservices over RabbitMQ, implementing idempotency keys to guarantee at-least-once message processing without duplicate transactions, and architecting RESTful API gateways.
- **Data Structures & Algorithms**: Formulating graph algorithms for schedule conflict detection, cyclical state machine execution in LangGraph, least-squares regression for academic grade trajectory modeling, and double-entry ledger invariant reconciliation.

### 1.3 Project Background
The conceptualization of SmartEdu emerged from direct observation of daily operational friction at COMSATS University Islamabad, Sahiwal Campus. Over successive academic semesters, students and faculty consistently encountered recurring coordination challenges:
1. **Timetable Inflexibility**: Changes in classroom allocations or instructor substitutions were communicated via notice boards or informal WhatsApp groups, resulting in widespread student disorientation.
2. **Underutilized Campus Facilities**: While students wandered academic blocks seeking quiet spaces for senior design projects or study groups, numerous lecture halls and specialized laboratories sat vacant between scheduled lecture slots.
3. **Transit Telemetry Gaps**: University commuter buses traversing city routes (such as Farid Town, Mall Road, and Canal Line) frequently encountered urban traffic congestion. Commuters arrived at designated pickup points without visibility into whether a shuttle had already departed or was delayed.
4. **Pedagogical Inefficiencies**: Traditional learning management systems functioned as static document repositories. Students preparing for examinations had no automated diagnostic tools to evaluate their comprehension across cognitive tiers or identify conceptual weaknesses prior to formal evaluation.

By consolidating institutional administration, facility navigation, fleet tracking, and adaptive diagnostic assessment into a single, cohesive architecture, SmartEdu demonstrates how modern software engineering and artificial intelligence can solve practical university challenges.

### 1.4 Literature Review
To benchmark SmartEdu against contemporary solutions, existing commercial platforms, academic learning management systems, and AI research were evaluated across six criteria: administrative integration, facility wayfinding, transit telemetry, adaptive assessment, RAG grounding, and architectural resilience.

#### Traditional Campus Management Systems (CMS) & Portals
Commercial systems like Ellucian Banner, PeopleSoft Campus Solutions, and SAP Student Lifecycle Management provide robust administrative, financial, and registrar databases. However, these legacy enterprise platforms feature monolithic architectures, high licensing costs, rigid user interfaces, and minimal mobile responsiveness. They lack real-time facility telemetry, commuter bus tracking, and adaptive AI assessment capabilities.

#### Open-Source Learning Management Systems (LMS)
Platforms such as Moodle, Canvas LMS, and Open edX dominate online course delivery. Moodle and Canvas provide gradebooks, assignment submission dropboxes, and quiz modules. However, their assessment engines rely entirely on manual question authoring by instructors. They lack automated question generation from ingested syllabi, cannot construct Bloom's Taxonomy cognitive ladders automatically, and offer no native spatial wayfinding or campus transit telemetry.

#### Intelligent Tutoring Systems (ITS) & AI Question Generation
Early Intelligent Tutoring Systems (such as Cognitive Tutors and ASSISTments) used rule-based expert systems to model student knowledge states. Recent research has shifted toward transformer-based Large Language Models. Lewis et al. demonstrated that Retrieval-Augmented Generation (RAG) significantly improves factual accuracy in knowledge-intensive domains. However, unconstrained LLM generation in educational contexts suffers from prompt injection, ungrounded mathematical claims, and hallucinated grading criteria. Ji et al. highlighted the necessity of cyclical verification and deterministic guardrails in educational NLP.

Table 1.1 compares SmartEdu with representative institutional and commercial platforms.

#### Table 1.1: Comparison of Existing Systems with SmartEdu

| Evaluation Feature | Ellucian Banner / PeopleSoft | Moodle / Canvas LMS | Google Classroom | Commercial AI Chatbots | SmartEdu (Our Platform) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **System Architecture** | Heavy Monolith | Monolith / Modular | Multi-Tenant SaaS | Cloud Microservice | 12 Microservices / Serverless Gateway |
| **Universal Public Gateway** | None (Login Required) | None (Login Required) | None (Login Required) | Generic Web UI | Open Public Gateway + Role Workspaces |
| **Course Cockpit** | Tabular Tables | Multi-Screen Modules | Stream & Classwork | Not Applicable | High-Density Card + 8 Sub-Cards |
| **Attendance Guard** | Static Roll | Manual Entry | None | None | $\ge 75\%$ Regulatory Alert + Recovery Calc |
| **Dynamic Space Finder** | Basic Facility DB | None | None | None | Real-Time Block Filters + Telemetry |
| **Transit Telemetry** | None | None | None | None | Stop ETAs + Disruption Bulletins |
| **Campus Wayfinding** | None | None | None | None | 6 Directories + Vector Floor Blueprints |
| **Marquee Events** | None | Calendar Feed | Calendar Feed | None | Calendar Morphing + Knockout Brackets |
| **Document Ingestion** | None | Upload Only | File Attachment | File Upload (Ephemeral) | PDF/DOCX/PPTX RAG + Quota Meter |
| **Assessment Generator** | None | Manual Authoring | Manual Authoring | Ungrounded Prompts | LangGraph Bloom's Taxonomy Engine |
| **Numerical Proofs** | None | Static Text | Static Text | Text Equation | Step-by-Step KaTeX Derivations |
| **Mastery Profiling** | None | Basic Gradebook | Rubric Scoring | None | SVG Topic Radar + Smart Regeneration |
| **Financial Ledger** | Proprietary ERP | Third-Party Plugin | None | None | Double-Entry ($\sum \text{Debits} = \sum \text{Credits}$) |

### 1.5 Analysis from Literature Review
The comparative analysis identifies five fundamental gaps in current educational software:
1. **The Architectural Disconnect**: Existing platforms separate campus operational telemetry (rooms, buses, directory) from academic learning systems, forcing students to navigate multiple disconnected tools.
2. **The Assessment Authoring Burden**: LMS platforms depend entirely on human instructors to author question banks, leading to sparse formative assessment opportunities.
3. **The Ungrounded LLM Risk**: General-purpose chatbots generate convincing but hallucinated academic explanations that fail to cite official course textbooks and course outlines.
4. **The Lack of Cognitive Trajectory Modeling**: Traditional gradebooks present static percentage scores without mapping student mastery across cognitive tiers (Recall, Application, Synthesis) or specific syllabus topics.
5. **The Enterprise Rigidity**: Existing university ERP systems are monolithic, expensive to maintain, and completely closed to public or prospective student inquiry.

SmartEdu directly resolves these deficiencies by integrating deterministic microservices for campus operations with an autonomous, document-grounded LangGraph RAG assessment studio.

### 1.6 Methodology and Software Lifecycle for This Project
SmartEdu was engineered following the **Agile Software Development Methodology**, employing structured **Scrum** sprint cycles. The project demanded continuous empirical evaluation—particularly regarding Gemini vector chunking strategies, prompt calibration across Bloom's Taxonomy tiers, and microservice resilience under high concurrency.

Development proceeded across eighteen structured bi-weekly sprints grouped into four macro phases:
- **Phase 1: Foundation & Distributed Infrastructure (Sprints 1–5)**: Designing the twelve microservice schemas, establishing RabbitMQ event topologies, configuring Docker environments, and building the RS256/Ed25519 identity and RBAC subsystem.
- **Phase 2: Academic Core, Scheduling & Campus Operations (Sprints 6–9)**: Building academic catalog services, attendance tracking, the Intelligent Timetable Engine, Dynamic Space Finder, and Smart Transit fleet tracking.
- **Phase 3: Campus Hub, Marquee Events & ERP Subsystems (Sprints 10–13)**: Implementing campus wayfinding with vector floor plans, seasonal marquee event tournament engines, double-entry financial ledger accounting, and institutional payroll runs.
- **Phase 4: Autonomous AI Learning Studio, Hardening & Verification (Sprints 14–18)**: Integrating Google Gemini API RAG, LangGraph state graphs, Bloom's Taxonomy test generation, KaTeX numerical proof rendering, SVG mastery radar profiling, and end-to-end automated testing.

### 1.7 Rationale Behind Selected Methodology
Agile Scrum was chosen over linear waterfall models due to the following project constraints:
1. **Iterative Refinement of AI Guardrails**: Determining optimal system prompts, few-shot exemplars, and distractor plausibility thresholds in LangGraph required continuous empirical tuning and regression testing.
2. **De-Risked Microservices Integration**: By delivering working software at the end of each sprint, cross-service event contracts (such as enrollment provisioning fee accounts via RabbitMQ) were verified incrementally.
3. **Continuous Quality Gate Enforcement**: Every sprint incorporated automated unit, contract, and end-to-end browser tests, ensuring zero regression across legacy modules as new features were introduced.

---

# Chapter 2: Problem Definition

## 2 Problem Definition
This chapter formalizes the specific challenges addressed by SmartEdu, outlines the concrete project deliverables, specifies the development environment, and analyzes the operational shortcomings of current university systems.

### 2.1 Problem Statement
University campus operations and self-directed academic learning currently suffer from four core operational failures:
1. **Disjointed Academic Navigation & Cognitive Friction**: Students enrolled in multiple courses must navigate through complex, nested LMS hierarchies to check attendance, view assignments, or download lecture notes. In addition, static PDF timetables fail to notify students of room swaps or instructor cancellations in real time.
2. **Invisible Campus Resources & Spatial Inefficiency**: Because universities lack real-time space telemetry, students wander corridors searching for empty classrooms for study groups. Simultaneously, campus commuter buses operate on rigid schedules without traffic-aware ETAs, causing students to miss transit or wait at stops unnecessarily.
3. **Fragmented Campus Information Architecture**: Information regarding faculty office hours, administrative queue status, laboratory equipment, and sports tournament fixtures is scattered across disparate paper notices and social media channels.
4. **Lack of Grounded, Adaptive Self-Assessment**: Students preparing for midterms and final examinations lack customized diagnostic evaluation. When students use commercial AI chatbots for study support, the models frequently hallucinate syllabus content, miscalculate mathematical derivations, and provide false reassurance without reference to prescribed course materials.

### 2.2 Deliverables and Development Requirements

#### 2.2.1 Deliverables
1. **Universal Adaptive Campus Gateway**: A responsive public portal featuring eight operational module cards (*Student Portal, Free Slots, Timetable, Campus Hub, Transport Service, Faculty, Sports Week, Self Assessment*).
2. **Student Academic Cockpit**: Course command centers displaying course metadata, color-coded HEC attendance dials, standing projections, and eight consolidated sub-cards.
3. **Intelligent Timetable Hub**: Dynamic day timelines and weekly block schedules supporting both Student and Teacher views with capacity indicators and `.ics` calendar sync.
4. **Dynamic Space Finder**: Interactive classroom vacancy engine with Block A–D filtering, equipment inventories, and 90-minute study reservation holds.
5. **Smart Transit & Fleet Telemetry**: City commuter bus and campus shuttle tracking engine with stop-by-stop itineraries and disruption notices.
6. **Campus Hub & Directory**: Multi-division campus directory with live administrative queue token counters and interactive SVG vector floor plans.
7. **Marquee Events Portal**: Tournament engine supporting seasonal calendar morphing (Sports Week, Tech Gala, Career Fair), live fixtures, and knockout elimination brackets.
8. **AI Self-Learning Studio**: Autonomous study hub with multi-format material ingestion (PDF, DOCX, PPTX), Gemini RAG vector search, Bloom's Taxonomy test generator, KaTeX step-by-step proofs, SVG mastery radar charts, and adaptive smart regeneration.
9. **Institutional ERP Subsystem**: Double-entry general ledger accounting engine, multi-part fee installment billing, maker-checker dual control, and automated monthly payroll runs.
10. **Automated Verification Suites**: Complete testing suite comprising 1,864 backend unit/contract tests, 41 frontend test suites, and Playwright E2E browser journeys.

#### 2.2.2 Development Requirements

##### 2.2.2.1 Technical Development Requirements
- **Frontend Architecture**: React 19.0, TypeScript 5.9, Vite 8.3, Tailwind CSS 4.3, TanStack Query 5, React Hook Form, Zod, and KaTeX 0.19.
- **Backend Architecture**: Python 3.12, FastAPI 0.115, Pydantic v2, SQLAlchemy 2.0, Alembic 1.13, Uvicorn, and Starlette.
- **AI & RAG Infrastructure**: Google Gemini API (`gemini-2.0-flash`), Gemini Embeddings (`text-embedding-004`), LangGraph 0.2, LangChain 0.3, and PostgreSQL `pgvector`.
- **Document Processing**: `pypdf` 5.0, `pdfplumber` 0.11, `python-docx` 1.1, and `python-pptx` 1.0.
- **Distributed Infrastructure**: PostgreSQL 16 (12 isolated database schemas), RabbitMQ 4.1 (AMQP message bus), Redis 7.4 (idempotency store), and MinIO (S3 object storage).
- **Deployment & Hosting**: Docker Compose containerized topology for enterprise on-premise hosting, and unified Python serverless gateway (`api/index.py`) for cloud deployment on Vercel backed by Neon PostgreSQL.

#### Table 2.1: Tools and Technologies used in SmartEdu

| Architectural Layer | Technologies / Tools Employed |
| :--- | :--- |
| **Frontend Framework & Language** | React 19.2, TypeScript 5.9, Vite 8.3 |
| **Styling & UI Components** | Tailwind CSS 4.3, Lucide React, Radix UI Primitives |
| **Frontend State & Data Fetching** | TanStack Query v5, Zustand v5, React Hook Form, Zod |
| **Mathematical Typesetting** | KaTeX 0.19.1 (Step-by-Step LaTeX Rendering) |
| **Backend Framework & Language** | Python 3.12, FastAPI 0.115, Starlette, Uvicorn |
| **Data Validation & ORM** | Pydantic v2.9, SQLAlchemy 2.0, Alembic 1.13 |
| **AI Orchestration & LLMs** | Google Gemini API (`gemini-2.0-flash`), LangGraph 0.2, LangChain 0.3 |
| **Vector Search & Embeddings** | Google `text-embedding-004` (768 dimensions), `pgvector` 0.3.0 |
| **Document Parsing & Extraction** | `pypdf`, `pdfplumber`, `python-docx`, `python-pptx` |
| **Relational Database** | PostgreSQL 16 (12 microservice databases), Neon PgBouncer |
| **Message Broker & Cache** | RabbitMQ 4.1 (AMQP), Redis 7.4 (Idempotency & Session Store) |
| **Security & Cryptography** | PyJWT (RS256 / Ed25519), Argon2id (`pwdlib`), Cryptography (Fernet) |
| **Testing & Quality Assurance** | Pytest 8.4, Vitest 5.0, Playwright 1.50, Testing Library |
| **DevOps & Cloud Deployment** | Docker, Docker Compose, GitHub Actions CI/CD, Vercel Serverless |

### 2.3 Current System
At present, campus operations across most Pakistani universities are managed through a patchwork of manual, disconnected procedures:
1. **Academic Notice Boards & Spreadsheets**: Class schedules and room changes are maintained in Excel spreadsheets and periodically pinned to physical bulletin boards or broadcast over informal social media groups. Students have no live visibility into timetable alterations.
2. **Manual Classroom Inspection**: To find an empty room for collaborative study, students walk from wing to wing peeking through door windows. Faculty members have no automated way to declare an unoccupied room temporarily available.
3. **Unpredictable Commuter Shuttles**: University buses follow static departure times. Urban traffic delays, maintenance issues, and route diversions cannot be tracked by waiting commuters.
4. **Passive Course File Repositories**: Learning management systems function purely as static file download hubs. They do not evaluate student understanding, generate diagnostic practice questions, or highlight knowledge gaps.
5. **Vulnerable Financial & Accounting Procedures**: Manual fee voucher generation, bank challan submission, and reconciliation lead to accounting backlogs, missed late fee penalties, and potential financial discrepancies.

SmartEdu replaces this fragmented and error-prone landscape with an integrated, automated, and secure digital platform.

---

# Chapter 3: Requirement Analysis

## 3 Requirement Analysis
This chapter specifies the behavioral, functional, and non-functional requirements of SmartEdu. Requirements were gathered through operational workflows at COMSATS University Islamabad, Higher Education Commission (HEC) academic guidelines, and enterprise software engineering best practices.

### 3.1 Use Case Diagram
The platform serves five primary human actors and two external system actors:
- **Student**: Explores public campus gateway, logs into Student Portal, views course command centers, tracks attendance compliance, queries timetable, reserves free study rooms, tracks transit shuttles, and interacts with the AI Self-Learning Studio.
- **Faculty / Teacher**: Manages assigned course sections, records student attendance, authors assessments, grades submissions, inspects teaching schedules, and views monthly payroll slips.
- **Institutional Administrator**: Manages academic catalogs, configures fee structures, audits double-entry general ledger transactions, approves student refunds via maker-checker dual control, and supervises monthly payroll runs.
- **Transit Operator / Driver**: Broadcasts route departure telemetry and reports service disruption alerts.
- **Platform Security Officer**: Audits cryptographic system logs, monitors microservice health probes, and manages feature flag rollouts.
- **Google Gemini API (External System)**: Generates semantic vector embeddings and structured Bloom's Taxonomy test questions.
- **Simulated 1Link Banking Gateway (External System)**: Processes electronic fee checkout settlements and salary disbursements.

```mermaid
flowchart TD
    subgraph Actors ["Platform Actors"]
        Student["Student Actor"]
        Teacher["Teacher Actor"]
        Admin["Administrator Actor"]
        Gemini["Google Gemini API"]
        Bank["1Link Banking System"]
    end

    subgraph GatewayCore ["Universal Gateway & Campus Operations"]
        UC01["UC-01: User Registration"]
        UC02["UC-02: Role-Enforced Login"]
        UC08["UC-08: Query Timetable & Export"]
        UC09["UC-09: Discover & Reserve Free Space"]
        UC10["UC-10: Track Transit Telemetry"]
        UC11["UC-11: Campus Hub Wayfinding"]
        UC12["UC-12: Sports Gala Tracking"]
    end

    subgraph AISelfLearning ["AI Self-Learning Studio"]
        UC03["UC-03: Ingest Study Materials"]
        UC04["UC-04: Generate AI Assessment"]
        UC05["UC-05: Attempt Timed Assessment"]
        UC06["UC-06: Diagnostic LaTeX Review"]
        UC07["UC-07: Mastery Radar & Smart Regen"]
    end

    subgraph InstitutionalERP ["Institutional Governance & Finance"]
        UC13["UC-13: Fee Checkout & Installments"]
        UC14["UC-14: Monthly Payroll Run"]
        UC15["UC-15: System Audit Inspection"]
    end

    Student --> UC01
    Student --> UC02
    Student --> UC03
    Student --> UC04
    Student --> UC05
    Student --> UC06
    Student --> UC07
    Student --> UC08
    Student --> UC09
    Student --> UC10
    Student --> UC11
    Student --> UC12
    Student --> UC13

    Teacher --> UC02
    Teacher --> UC08
    Teacher --> UC09
    Teacher --> UC11
    Teacher --> UC12
    Teacher --> UC14

    Admin --> UC02
    Admin --> UC13
    Admin --> UC14
    Admin --> UC15

    UC03 -.-> Gemini
    UC04 -.-> Gemini
    UC13 -.-> Bank
    UC14 -.-> Bank
```
**Figure 3.1: Use Case Diagram for SmartEdu**

---

### 3.2 Detailed Use Cases

#### Table 3.1: User Registration & Role Onboarding (UC-01)
| Field | Specification |
| :--- | :--- |
| **Use Case ID** | **UC-01** |
| **Use Case Name** | User Registration & Role Onboarding |
| **Actors** | Student, Faculty Member, Institutional Administrator |
| **Description** | Allows a new institutional user to register an account with verified credentials. |
| **Trigger** | User navigates to `/register` or `/login/student` and selects registration. |
| **Pre-Condition** | User holds a valid institutional email domain (`@comsats.edu.pk` or authorized domain). |
| **Post-Condition** | User record is persisted with an Argon2id password hash, assigned a base role, and issued a verification token. |
| **Normal Flow** | 1. User submits full name, institutional email, registration/employee roll number, and password.<br>2. System validates email domain, registration pattern, and password entropy (min 8 chars, 1 digit, 1 symbol).<br>3. System hashes the password with Argon2id and creates the database entity.<br>4. System assigns the designated role (`student` or `teacher`).<br>5. System emits `identity.user.registered.v1` event to RabbitMQ. |
| **Alternative Flow** | If registration is initiated by an Administrator, the user is directly provisioned with verified status. |
| **Exceptions** | - Duplicate email: System returns HTTP 409 Conflict.<br>- Weak password: Form displays inline complexity requirements. |
| **Business Rules** | Passwords must never be stored in plaintext. Student accounts must specify a valid academic department. |

#### Table 3.2: Multi-Factor Authentication & Role-Enforced Sign-In (UC-02)
| Field | Specification |
| :--- | :--- |
| **Use Case ID** | **UC-02** |
| **Use Case Name** | Multi-Factor Authentication & Role-Enforced Sign-In |
| **Actors** | Student, Faculty Member, Institutional Administrator |
| **Description** | Authenticates users and enforces strict role-based access to designated portal workspaces. |
| **Trigger** | User submits login form on `/login`, `/login/student`, or `/login/faculty`. |
| **Pre-Condition** | User account exists and is in an active, non-locked state. |
| **Post-Condition** | User receives a signed RS256 JWT access token (15-min expiry) and an HttpOnly refresh cookie. |
| **Normal Flow** | 1. User enters email and password on the role-designated portal.<br>2. System checks sliding-window rate limiting (max 5 failed attempts/minute).<br>3. System verifies password hash in constant time.<br>4. System validates that the user possesses the required portal role (e.g., student attempting student login).<br>5. System generates RS256 access token containing `sub`, `roles`, and `permissions` claims.<br>6. User is redirected to `/app/student`, `/app/teacher`, or `/app/admin`. |
| **Alternative Flow** | If a student attempts to log in via `/login/faculty`, the system rejects the attempt with a role-mismatch error. |
| **Exceptions** | - Rate limit exceeded: System returns HTTP 429 Too Many Requests.<br>- Invalid credentials: System returns generic error to prevent account enumeration. |
| **Business Rules** | Access tokens expire in 15 minutes. Refresh tokens rotate upon every invocation. |

#### Table 3.3: Ingest Study Materials into Subject Vault (UC-03)
| Field | Specification |
| :--- | :--- |
| **Use Case ID** | **UC-03** |
| **Use Case Name** | Ingest Study Materials into Subject Vault |
| **Actors** | Student |
| **Description** | Allows a student to upload course slides, past papers, and notes into an isolated subject vault. |
| **Trigger** | Student drops a file into `/app/student/learning` under the Study Materials tab. |
| **Pre-Condition** | Student is authenticated and has created or selected a subject. File size $\le 10\text{ MB}$. |
| **Post-Condition** | Document text is extracted, deduplicated via SHA-256, chunked, embedded, and stored in `pgvector`. |
| **Normal Flow** | 1. Student selects a PDF, DOCX, or PPTX file.<br>2. System calculates SHA-256 hash and checks the student's 100MB storage quota.<br>3. Document parser extracts text headers, sections, and paragraphs.<br>4. Semantic chunker splits text into 500-token chunks with 50-token overlaps.<br>5. Google `text-embedding-004` generates 768-dimensional vector embeddings.<br>6. Embeddings and metadata are saved to `learning_document_chunks` in PostgreSQL.<br>7. System discovers topic units and updates the subject topic inventory. |
| **Alternative Flow** | If an identical file hash exists for this student, the system references the existing chunks without re-embedding. |
| **Exceptions** | - Quota exceeded ($>100\text{ MB}$): System rejects upload with HTTP 413.<br>- Unsupported format: System returns HTTP 415 Unsupported Media Type. |
| **Business Rules** | Storage quota is strictly enforced at 100MB per student. Ingested files are accessible only by the owner. |

#### Table 3.4: Generate AI Assessment via Bloom's Taxonomy (UC-04)
| Field | Specification |
| :--- | :--- |
| **Use Case ID** | **UC-04** |
| **Use Case Name** | Generate AI Assessment via Bloom's Taxonomy |
| **Actors** | Student, Google Gemini API |
| **Description** | Generates an objective multiple-choice practice test calibrated across cognitive tiers. |
| **Trigger** | Student clicks "Generate Assessment" in `/app/student/learning`. |
| **Pre-Condition** | The selected subject contains at least one ingested document. |
| **Post-Condition** | A structured test containing 5–30 questions with distractor explanations and proofs is created. |
| **Normal Flow** | 1. Student selects question count (5–30), cognitive difficulty (Basic, Medium, Hard, Mixed), and topic tags.<br>2. LangGraph `RetrievalNode` fetches relevant document chunks using `pgvector` cosine similarity.<br>3. `DraftQuestionNode` prompts Google Gemini (`gemini-2.0-flash`) using strict Pydantic JSON schemas.<br>4. `DistractorAuditorNode` verifies that distractors are plausible yet unambiguous.<br>5. `NumericalSolverNode` detects quantitative questions and generates step-by-step LaTeX proofs.<br>6. `QualityGateNode` validates JSON schema conformity and commits the test to the database. |
| **Alternative Flow** | If specific topics are omitted, the system samples evenly across all indexed syllabus units. |
| **Exceptions** | - LLM timeout or quota error: LangGraph retries up to 2 times, then falls back to cached template items.<br>- Empty context: System prompts student to upload additional study materials. |
| **Business Rules** | Every question must link to an extracted syllabus topic. Numerical items must include LaTeX proofs. |

#### Table 3.5: Interactive Test Attempt & Timed Submission (UC-05)
| Field | Specification |
| :--- | :--- |
| **Use Case ID** | **UC-05** |
| **Use Case Name** | Interactive Test Attempt & Timed Submission |
| **Actors** | Student |
| **Description** | Student attempts an AI-generated assessment under live countdown timer supervision. |
| **Trigger** | Student clicks "Start Test" on an active assessment. |
| **Pre-Condition** | Assessment status is `READY` and has not been previously finalized. |
| **Post-Condition** | Answers are recorded, automatic score is calculated, and attempt status becomes `EVALUATED`. |
| **Normal Flow** | 1. System displays test questions with randomized options and starts countdown timer.<br>2. Student navigates via question grid, selecting options and flagging questions for review.<br>3. Student clicks "Submit Test" and confirms dialog.<br>4. System evaluates student selections against official answer keys in constant time.<br>5. System stores attempt score, duration, and individual question choices.<br>6. UI transitions immediately to the Diagnostic Review Screen. |
| **Alternative Flow** | Timer expiration: If countdown reaches 00:00, the system automatically finalizes and submits answers. |
| **Exceptions** | - Browser disconnect: Selected choices persist in local browser storage and re-synchronize on reconnect. |
| **Business Rules** | Assessment timer is enforced both on the client and server side. Resubmissions are blocked. |

#### Table 3.6: Diagnostic Evaluation & Step-by-Step LaTeX Review (UC-06)
| Field | Specification |
| :--- | :--- |
| **Use Case ID** | **UC-06** |
| **Use Case Name** | Diagnostic Evaluation & Step-by-Step LaTeX Review |
| **Actors** | Student |
| **Description** | Displays granular question-by-question scoring, pedagogical rationale, and mathematical derivations. |
| **Trigger** | Student completes a test attempt or views a completed test from the history list. |
| **Pre-Condition** | Assessment attempt has been evaluated. |
| **Post-Condition** | Diagnostic review is displayed; student review timestamp is recorded. |
| **Normal Flow** | 1. System presents aggregate score percentage, correct/incorrect counts, and time taken.<br>2. For each question, system contrasts the student's selected answer against the correct key.<br>3. System renders the pedagogical "Why is this correct?" explanation citing source materials.<br>4. For quantitative questions, student clicks "View Step-by-Step Solution".<br>5. System renders mathematical derivations dynamically using KaTeX (e.g., matrix proofs, calculus). |
| **Alternative Flow** | If student answered all questions correctly, the system offers an immediate "Challenge Mode" test. |
| **Exceptions** | - KaTeX rendering syntax error: System falls back to rendering raw mathematical text in code spans. |
| **Business Rules** | Explanations must be grounded in the student's uploaded documents. |

#### Table 3.7: Topic Mastery Profiling & Smart Test Regeneration (UC-07)
| Field | Specification |
| :--- | :--- |
| **Use Case ID** | **UC-07** |
| **Use Case Name** | Topic Mastery Profiling & Smart Test Regeneration |
| **Actors** | Student |
| **Description** | Classifies syllabus topic proficiency on an SVG radar chart and generates weakness-targeted tests. |
| **Trigger** | Student opens "Mastery & Analytics" tab or clicks "Smart Regenerate". |
| **Pre-Condition** | Student has completed at least one assessment attempt for the active subject. |
| **Post-Condition** | Topic mastery scores are updated, SVG radar chart is rendered, and a targeted test is provisioned. |
| **Normal Flow** | 1. System aggregates historical attempts across all topic tags.<br>2. System computes mastery percentages and classifies topics into:<br>   - Strong ($\ge 75\%$)<br>   - Moderate ($50\text{--}74\%$)<br>   - Weak ($<50\%$)<br>3. System renders multi-axis SVG Radar Chart displaying cognitive mastery polygon.<br>4. Student selects "Smart Regenerate (Focus on Weak Topics)".<br>5. System constructs a targeted generation request allocating **70% of questions to weak topics** and **30% to moderate/strong topics** for reinforcement. |
| **Alternative Flow** | Student selects "Challenge Mode" (allocating 100% of questions to Hard Bloom's Taxonomy items). |
| **Exceptions** | - Insufficient data ($<1$ test): System displays informational placeholder inviting initial test attempt. |
| **Business Rules** | Mastery calculations use recency-weighted scoring ($0.7 \times \text{recent} + 0.3 \times \text{historical}$). |

#### Table 3.8: Query Class Timetable & Export Calendar (UC-08)
| Field | Specification |
| :--- | :--- |
| **Use Case ID** | **UC-08** |
| **Use Case Name** | Query Class Timetable & Export Calendar |
| **Actors** | Student, Faculty Member |
| **Description** | Allows students and teachers to view weekly schedules and export to Google/Apple Calendar. |
| **Trigger** | User navigates to Timetable card on Gateway or `/app/student/timetable`. |
| **Pre-Condition** | Timetable slots are published by the Scheduling Service. |
| **Post-Condition** | Timetable is displayed with room/teacher context; `.ics` file is downloaded upon request. |
| **Normal Flow** | 1. User selects "Student" or "Teacher" mode.<br>2. If Student: User selects section (e.g., `BCS-7C`). System displays weekly slots, subjects, instructors, classrooms, and student capacities.<br>3. If Teacher: User selects faculty name (e.g., `Dr. Munir Ahmad`). System displays assigned teaching slots.<br>4. System computes total weekly lectures and displays daily lecture counts.<br>5. User clicks "Export to Calendar (.ics)".<br>6. System generates standard iCalendar file with VEVENT blocks and triggers browser download. |
| **Alternative Flow** | User switches to "Interactive Timeline" view to see a moving current-time marker. |
| **Exceptions** | - Section has no published slots: System displays clear empty-state notification. |
| **Business Rules** | Timetable views must indicate room capacities and scheduled student cohort sizes. |

#### Table 3.9: Discover & Reserve Free Classroom Space (UC-09)
| Field | Specification |
| :--- | :--- |
| **Use Case ID** | **UC-09** |
| **Use Case Name** | Discover & Reserve Free Classroom Space |
| **Actors** | Student, Faculty Member |
| **Description** | Discovers vacant lecture rooms and allows students to place a 90-minute study reservation hold. |
| **Trigger** | User opens Free Slots card on Gateway or `/app/student/facilities`. |
| **Pre-Condition** | Facility service contains active room inventory and schedule slot mappings. |
| **Post-Condition** | Available rooms are displayed; reservation record is created with auto-release timer. |
| **Normal Flow** | 1. User filters by Day and Slot, or clicks "Available Right Now".<br>2. User selects campus block (Block A, Block B, Block C, Block D, or Engineering Labs).<br>3. System lists vacant rooms with seating capacities, equipment chips (Projector, AC, Power, Wi-Fi), and "Free Until" indicators.<br>4. Student selects an empty room and clicks "Reserve for Study Group".<br>5. System checks concurrency locks, assigns 90-minute reservation hold, and issues check-in QR code. |
| **Alternative Flow** | If reservation is not verified via QR check-in within 15 minutes, the room hold auto-releases. |
| **Exceptions** | - Concurrent booking: System returns HTTP 409 Conflict if another student reserved the slot first. |
| **Business Rules** | Reservations are capped at 90 minutes. Only authorized enrolled students may hold study spaces. |

#### Table 3.10: Inspect Transit Routes & Stop Arrival ETAs (UC-10)
| Field | Specification |
| :--- | :--- |
| **Use Case ID** | **UC-10** |
| **Use Case Name** | Inspect Transit Routes & Stop Arrival ETAs |
| **Actors** | Student, Faculty Member, Transit Operator |
| **Description** | Displays comprehensive city transit networks, campus shuttles, stop ETAs, and disruption notices. |
| **Trigger** | User opens Transport Service card on Gateway or `/app/student/transit`. |
| **Pre-Condition** | Route networks and vehicle telemetries are registered in the Transit repository. |
| **Post-Condition** | Route itinerary timeline, stop ETAs, driver contacts, and active disruption banners are displayed. |
| **Normal Flow** | 1. User selects "City Commuter Routes" or "Intra-Campus Shuttles".<br>2. User selects route (e.g., *Farid Town Point*, *Mall Road Express*, *Canal Line*).<br>3. System displays designated bus number, driver contact number, and seating status (*Seats Available, Standing Only, Full*).<br>4. System renders stop-by-stop itinerary timeline with scheduled vs. estimated actual arrival times (ETAs).<br>5. System displays active emergency disruption banners (e.g., route diversions, maintenance). |
| **Alternative Flow** | Transit operator updates vehicle location; client updates stop arrival ETAs in real time. |
| **Exceptions** | - Service suspended: System displays high-visibility alert banner with administrative remarks. |
| **Business Rules** | ETA calculations must account for traffic delay offsets. Driver contacts must be verified. |

#### Table 3.11: Campus Hub Directory & Office Queue Ticket Tracking (UC-11)
| Field | Specification |
| :--- | :--- |
| **Use Case ID** | **UC-11** |
| **Use Case Name** | Campus Hub Directory & Office Queue Ticket Tracking |
| **Actors** | Student, Faculty Member, Administrative Staff |
| **Description** | Centralizes institutional directories, office working hours, live queue counters, and vector floor plans. |
| **Trigger** | User opens Campus Hub card on Gateway or `/app/student/hub`. |
| **Pre-Condition** | Directory entities and office queue servers are active. |
| **Post-Condition** | Directory information, live queue status, and interactive floor plans are rendered. |
| **Normal Flow** | 1. User selects from six directory tabs: *Faculty & Teachers, Office Directory, Lab Directory, Classrooms, Library, Statistics*.<br>2. In Office Directory: User inspects Registrar, Accounts, or Examination counter hours, and views current serving ticket token (e.g., "Token #42 in Service").<br>3. In Lab Directory: User inspects hardware and robotics equipment inventory.<br>4. In Library: User views live silent-study seat meter (e.g., "78% Seats Occupied").<br>5. User clicks "View Floor Blueprint": System renders interactive SVG map highlighting room location. |
| **Alternative Flow** | User enters search term (e.g., "Robotics Lab" or "Dr. Munir"); system filters directory cards dynamically. |
| **Exceptions** | - Queue server offline: System shows static office hours with "Queue Offline" status chip. |
| **Business Rules** | Administrative offices must display official operational timings and contact extensions. |

#### Table 3.12: Sports Gala Fixtures & Elimination Tournament Tracking (UC-12)
| Field | Specification |
| :--- | :--- |
| **Use Case ID** | **UC-12** |
| **Use Case Name** | Sports Gala Fixtures & Elimination Tournament Tracking |
| **Actors** | Student, Faculty Member, Sports Coordinator |
| **Description** | Tracks seasonal marquee events with day-grouped fixtures, knockout brackets, and trophy standings. |
| **Trigger** | User opens Sports Week card on Gateway or `/app/student/events`. |
| **Pre-Condition** | Event schedules and tournament draws are published in the Event database. |
| **Post-Condition** | Live fixture scores, knockout tournament trees, and department leaderboard are displayed. |
| **Normal Flow** | 1. System detects current academic calendar mode (*Sports Gala in Spring, Tech Gala in Fall*).<br>2. User selects tournament day via top date pills (*Monday, Tuesday, Wednesday, Thursday, Friday*).<br>3. System displays day-grouped fixtures with sport type (Cricket, Football, Badminton, Table Tennis), venue, participating departments, and live score status.<br>4. User toggles to "Knockout Brackets" to view visual quarter-final, semi-final, and final progression.<br>5. User toggles to "Trophy Standings" to view department points table (Gold, Silver, Bronze tallies). |
| **Alternative Flow** | User clicks "Subscribe to Alerts": System registers browser notification push token for department matches. |
| **Exceptions** | - Match postponed: Status updates to `POSTPONED` with weather/ground delay notes. |
| **Business Rules** | Department standings points: Gold = 10 pts, Silver = 5 pts, Bronze = 2 pts. |

#### Table 3.13: Student Fee Invoice Checkout & Installment Payment (UC-13)
| Field | Specification |
| :--- | :--- |
| **Use Case ID** | **UC-13** |
| **Use Case Name** | Student Fee Invoice Checkout & Installment Payment |
| **Actors** | Student, 1Link Banking Gateway |
| **Description** | Manages semester fee payments, scholarship concessions, installment plans, and digital checkout. |
| **Trigger** | Student navigates to `/app/student/finance` and selects "Pay Now". |
| **Pre-Condition** | Student has an active fee invoice generated by the Finance Service. |
| **Post-Condition** | Invoice/installment status updates to `PAID`, general ledger records postings, and receipt is issued. |
| **Normal Flow** | 1. Student reviews tuition breakdown, concessions (e.g., 25% Merit Discount), and due dates.<br>2. Student selects full payment or active installment plan.<br>3. Student clicks "Pay Now" and selects payment channel (JazzCash, EasyPaisa, or 1Link Online Transfer).<br>4. System creates checkout intent with unique transaction idempotency key.<br>5. Simulated banking gateway executes settlement and returns cryptographic success signature.<br>6. System records double-entry GL postings (`Debit: Cash, Credit: Accounts Receivable`).<br>7. Invoice status updates to `PAID`, outstanding balance drops to zero, and digital receipt is generated. |
| **Alternative Flow** | Overdue fee: If current date exceeds due date + 10-day grace period, system appends flat PKR 500 penalty. |
| **Exceptions** | - Payment declined: System leaves invoice in `ISSUED` state and displays banking failure message. |
| **Business Rules** | Double-entry invariant must hold ($\sum \text{Debits} = \sum \text{Credits}$). Dual control prohibits self-refunds. |

#### Table 3.14: Institutional Payroll Run & Maker-Checker Approval (UC-14)
| Field | Specification |
| :--- | :--- |
| **Use Case ID** | **UC-14** |
| **Use Case Name** | Institutional Payroll Run & Maker-Checker Approval |
| **Actors** | Institutional Administrator, HR Officer |
| **Description** | Computes monthly faculty salaries and enforces dual-control approval before bank disbursement. |
| **Trigger** | HR Officer initiates monthly payroll run in `/app/admin/payroll`. |
| **Pre-Condition** | Active monthly payroll period is open and employee profiles are verified. |
| **Post-Condition** | Gross-to-net calculations are sealed, dual approval is recorded, and payslips are published. |
| **Normal Flow** | 1. HR Officer initiates payroll calculation for active month.<br>2. System executes gross-to-net calculation engine (Base Salary + Allowances - Tax/Provident Deductions).<br>3. System sets payroll run status to `PENDING_APPROVAL`.<br>4. Distinct Authorized Approver (Maker-Checker enforcement) inspects aggregate gross-to-net ledger.<br>5. Approver executes cryptographic sign-off; status transitions to `APPROVED`.<br>6. System dispatches simulated 1Link batch disbursements and publishes individual employee payslips. |
| **Alternative Flow** | Approver detects discrepancy: Rejects run with remarks; creator must adjust parameters and recompute. |
| **Exceptions** | - Self-approval attempt: System returns HTTP 403 Forbidden (Creator cannot approve their own run). |
| **Business Rules** | Segregation of duties is mandatory. Ordinary student accounts cannot possess payroll profiles. |

#### Table 3.15: Platform Audit Log & System Configuration Inspection (UC-15)
| Field | Specification |
| :--- | :--- |
| **Use Case ID** | **UC-15** |
| **Use Case Name** | Platform Audit Log & System Configuration Inspection |
| **Actors** | Platform Administrator, Security Officer |
| **Description** | Inspects immutable audit trails, feature flags, and microservice health probes. |
| **Trigger** | Administrator opens `/app/admin/platform`. |
| **Pre-Condition** | User holds verified `admin` role with platform management scopes. |
| **Post-Condition** | Audit logs are displayed with redacted secrets; health states of all 12 services are verified. |
| **Normal Flow** | 1. Administrator accesses platform dashboard.<br>2. System displays health and readiness probes across all twelve microservices.<br>3. Administrator inspects security audit logs with actor IDs, correlation IDs, timestamps, and action types.<br>4. Sensitive credentials, passwords, and JWT payloads are automatically redacted.<br>5. Administrator manages dynamic feature flags (e.g., toggling experimental assessment modes). |
| **Alternative Flow** | Administrator exports audit log as structured JSON for compliance archiving. |
| **Exceptions** | - Non-admin access attempt: Protected route immediately redirects to `/forbidden`. |
| **Business Rules** | Audit logs are append-only. Modification or deletion of audit records is programmatically blocked. |

---

### 3.3 Functional Requirements

#### Table 3.16: Functional Requirement: Multi-Factor Authentication (FR-001)
| Field | Specification |
| :--- | :--- |
| **Identifier** | **FR-001** |
| **Title** | Multi-Factor Authentication & Role-Enforced Identity |
| **Requirement** | The system shall authenticate users via email and Argon2id-hashed credentials, issuing an RS256-signed JWT access token (15-minute lifetime) and a rotating HttpOnly refresh cookie (7-day lifetime), enforcing dedicated role boundaries for students, faculty, and administrators. |
| **Source** | Enterprise Security Standard & HEC Identity Guidelines |
| **Rationale** | Ensures secure access control and prevents unauthorized cross-role privilege escalation. |
| **Business Rule** | Access tokens must contain user UUID, role array, and permission scopes. Passwords must meet NIST SP 800-63B standards. |
| **Dependencies** | None |
| **Priority** | High |

#### Table 3.17: Functional Requirement: Multi-Format Document Ingestion (FR-002)
| Field | Specification |
| :--- | :--- |
| **Identifier** | **FR-002** |
| **Title** | Multi-Format Document Ingestion & Storage Quota Meter |
| **Requirement** | The system shall accept syllabus, lecture notes, and past paper uploads in PDF, DOCX, and PPTX formats up to 10 MB per file, enforcing an aggregate 100 MB storage quota per student account. |
| **Source** | Academic Self-Learning Specification (Module 8) |
| **Rationale** | Students require flexible document ingestion to ground the AI assessment engine in real course materials. |
| **Business Rule** | Uploaded files must be validated via MIME-type signature checks; path traversal characters must be sanitized. |
| **Dependencies** | FR-001 |
| **Priority** | High |

#### Table 3.18: Functional Requirement: Asynchronous Extraction & Deduplication (FR-003)
| Field | Specification |
| :--- | :--- |
| **Identifier** | **FR-003** |
| **Title** | Asynchronous Document Extraction & SHA-256 Deduplication |
| **Requirement** | The system shall compute a SHA-256 cryptographic checksum for every uploaded document to prevent duplicate chunking, extracting text via `pypdf`, `python-docx`, and `python-pptx` within asynchronous background worker tasks. |
| **Source** | System Performance & Storage Optimization Requirement |
| **Rationale** | Prevents redundant vector storage overhead and maintains snappy frontend responsiveness during ingestion. |
| **Business Rule** | If an identical SHA-256 hash exists for the student, existing document chunks must be linked immediately. |
| **Dependencies** | FR-002 |
| **Priority** | High |

#### Table 3.19: Functional Requirement: Semantic Embedding & Vector Indexing (FR-004)
| Field | Specification |
| :--- | :--- |
| **Identifier** | **FR-004** |
| **Title** | Semantic Vector Embedding & `pgvector` Storage |
| **Requirement** | The system shall chunk extracted text into 500-token units with 50-token overlaps, generate 768-dimensional dense vector embeddings via Google `text-embedding-004`, and persist chunks in PostgreSQL using the `pgvector` extension. |
| **Source** | AI Architecture Specification |
| **Rationale** | Provides high-precision semantic retrieval of relevant textbook and slide passages during assessment drafting. |
| **Business Rule** | Vector searches must partition strictly by `student_id` to prevent cross-tenant data leakage. |
| **Dependencies** | FR-003 |
| **Priority** | High |

#### Table 3.20: Functional Requirement: Bloom's Taxonomy Assessment Generator (FR-005)
| Field | Specification |
| :--- | :--- |
| **Identifier** | **FR-005** |
| **Title** | LangGraph Bloom's Taxonomy Assessment Generator |
| **Requirement** | The system shall implement a multi-node cyclical LangGraph workflow orchestrating Google Gemini (`gemini-2.0-flash`) to generate 5 to 30 multiple-choice questions calibrated across Bloom's Taxonomy levels (Recall, Application, Synthesis). |
| **Source** | Pedagogical Assessment Standard |
| **Rationale** | Ensures practice tests evaluate deep analytical problem-solving rather than rote memorization alone. |
| **Business Rule** | Every generated question must specify a target topic, cognitive level, plausible distractors, and an answer key. |
| **Dependencies** | FR-004 |
| **Priority** | High |

#### Table 3.21: Functional Requirement: Step-by-Step LaTeX Proof Solver (FR-006)
| Field | Specification |
| :--- | :--- |
| **Identifier** | **FR-006** |
| **Title** | Quantitative Step-by-Step LaTeX Derivation Solver |
| **Requirement** | The system shall detect quantitative, mathematical, or algorithmic questions during generation and author exhaustive, step-by-step LaTeX derivations renderable via KaTeX on the client review interface. |
| **Source** | STEM Course Pedagogy Requirement |
| **Rationale** | Students studying computer science, engineering, and mathematics require explicit mathematical derivations to understand mistakes. |
| **Business Rule** | Mathematical formulas must be enclosed in valid KaTeX delimiters (`$...$` or `$$...$$`). |
| **Dependencies** | FR-005 |
| **Priority** | High |

#### Table 3.22: Functional Requirement: Diagnostic Grading & Pedagogical Feedback (FR-007)
| Field | Specification |
| :--- | :--- |
| **Identifier** | **FR-007** |
| **Title** | Instant Diagnostic Grading & Document-Cited Rationale |
| **Requirement** | The system shall evaluate submitted assessment attempts in constant time, compute aggregate percentage scores, and display pedagogical explanations that cite specific concepts from the student's ingested documents. |
| **Source** | Diagnostic Evaluation Requirement |
| **Rationale** | Provides immediate formative feedback, eliminating the multi-week delay of traditional manual grading. |
| **Business Rule** | Scoring logic must execute deterministically on the server; client-supplied scores must never be trusted. |
| **Dependencies** | FR-005 |
| **Priority** | High |

#### Table 3.23: Functional Requirement: Cognitive Topic Mastery Radar Profiling (FR-008)
| Field | Specification |
| :--- | :--- |
| **Identifier** | **FR-008** |
| **Title** | Cognitive Topic Mastery Profiling & SVG Radar Visualization |
| **Requirement** | The system shall calculate running student proficiency scores across syllabus topics, classify mastery into Strong ($\ge 75\%$), Moderate ($50\text{--}74\%$), and Weak ($<50\%$), and render an interactive multi-axis SVG radar chart. |
| **Source** | Student Mastery Analytics Specification |
| **Rationale** | Visualizes knowledge gaps intuitively, allowing students to target study time efficiently. |
| **Business Rule** | Topic mastery must incorporate exponential decay to favor performance in recent attempts over older ones. |
| **Dependencies** | FR-007 |
| **Priority** | High |

#### Table 3.24: Functional Requirement: Weakness-Remediating Test Regeneration (FR-009)
| Field | Specification |
| :--- | :--- |
| **Identifier** | **FR-009** |
| **Title** | 1-Click Adaptive Weakness-Remediating Test Regeneration |
| **Requirement** | The system shall provide an automated "Smart Regenerate" capability that inspects historical topic weaknesses and dynamically allocates 70% of new assessment questions to weak topics and 30% to reinforcement topics. |
| **Source** | Adaptive Learning Engine Specification |
| **Rationale** | Closes learning loops automatically by actively challenging students on concepts they previously failed. |
| **Business Rule** | Smart regeneration must support three modes: Weakness-Remediation, Balanced Review, and Challenge Mode. |
| **Dependencies** | FR-008 |
| **Priority** | High |

#### Table 3.25: Functional Requirement: Universal Public Gateway Navigation (FR-010)
| Field | Specification |
| :--- | :--- |
| **Identifier** | **FR-010** |
| **Title** | Universal Public Campus Gateway & Direct Module Navigation |
| **Requirement** | The system shall expose a credential-free public gateway at `/` and `/explore` rendering eight distinct operational module cards, enabling instant exploration of public campus schedules, transit, directory, and facility data. |
| **Source** | Client Usability Specification (Module 1) |
| **Rationale** | Eliminates login friction for everyday campus inquiries while securing private academic records behind auth guards. |
| **Business Rule** | Public gateway routes must never expose confidential student identities, grades, or financial ledgers. |
| **Dependencies** | None |
| **Priority** | High |

#### Table 3.26: Functional Requirement: Timetable Matrix & .ics Synchronization (FR-011)
| Field | Specification |
| :--- | :--- |
| **Identifier** | **FR-011** |
| **Title** | Dual-Perspective Timetable Engine & Calendar Export |
| **Requirement** | The system shall display weekly academic timetables filtered by Student Section (with capacity and lecture counts) and Teacher Name, providing 1-click `.ics` calendar export for Google, Apple, and Outlook calendars. |
| **Source** | Schedule Engine Specification (Module 3) |
| **Rationale** | Provides responsive schedule parsing on mobile devices and eliminates reliance on static PDF tables. |
| **Business Rule** | Generated `.ics` files must conform to RFC 5545 specifications with valid `UID`, `DTSTART`, and `DTEND` properties. |
| **Dependencies** | None |
| **Priority** | High |

#### Table 3.27: Functional Requirement: Dynamic Room Telemetry & Booking Hold (FR-012)
| Field | Specification |
| :--- | :--- |
| **Identifier** | **FR-012** |
| **Title** | Dynamic Space Telemetry & 90-Minute Study Reservation Hold |
| **Requirement** | The system shall query vacant classrooms across Block A, Block B, Block C, Block D, and Engineering Labs, displaying student capacities, equipment chips, and "Free Until" indicators, allowing authorized students to hold rooms for 90 minutes. |
| **Source** | Space Finder Specification (Module 4) |
| **Rationale** | Optimizes physical campus asset utilization and eliminates corridor wandering during study hours. |
| **Business Rule** | Unchecked room reservations must automatically release after a 15-minute grace period. |
| **Dependencies** | FR-001 |
| **Priority** | Medium |

#### Table 3.28: Functional Requirement: Transit Fleet Tracking & Disruption Notices (FR-013)
| Field | Specification |
| :--- | :--- |
| **Identifier** | **FR-013** |
| **Title** | Smart Transit Fleet Telemetry & Emergency Bulletins |
| **Requirement** | The system shall render stop-by-stop itineraries for city commuter routes and intra-campus shuttles with scheduled vs. estimated actual arrival times (ETAs), vehicle numbers, driver contacts, and active disruption banners. |
| **Source** | Transit Telemetry Specification (Module 5) |
| **Rationale** | Protects commuter students from missing buses or waiting at remote stops during urban traffic delays. |
| **Business Rule** | Emergency disruption notices must display high-visibility alert styling with administrative verification flags. |
| **Dependencies** | None |
| **Priority** | Medium |

#### Table 3.29: Functional Requirement: Double-Entry Financial Ledger & Invoicing (FR-014)
| Field | Specification |
| :--- | :--- |
| **Identifier** | **FR-014** |
| **Title** | Double-Entry General Ledger, Invoicing & Installment Billing |
| **Requirement** | The system shall record all financial transactions (billings, concessions, payments, refunds) in an immutable double-entry general ledger enforcing the invariant $\sum \text{Debits} = \sum \text{Credits}$, supporting multi-part installment plans and maker-checker dual approval on refunds. |
| **Source** | Institutional Finance Specification |
| **Rationale** | Guarantees audit compliance, eliminates accounting discrepancies, and prevents fraudulent unauthorized self-refunds. |
| **Business Rule** | A user who drafts a refund request cannot approve it. Ledger journal entries are strictly append-only. |
| **Dependencies** | FR-001 |
| **Priority** | High |

#### Table 3.30: Functional Requirement: Cryptographic Audit Logging & Traceability (FR-015)
| Field | Specification |
| :--- | :--- |
| **Identifier** | **FR-015** |
| **Title** | Cryptographic Audit Logging & Platform Observability |
| **Requirement** | The system shall record all security-critical actions, logins, role modifications, and financial transitions in an append-only audit log with correlation IDs, automatic credential redaction, and microservice health observability. |
| **Source** | Enterprise Security & Compliance Standard |
| **Rationale** | Provides non-repudiation and forensic auditability for institutional compliance. |
| **Business Rule** | Audit records must never contain plain-text passwords, tokens, or confidential exam question keys. |
| **Dependencies** | FR-001 |
| **Priority** | High |

---

### 3.4 Non-Functional Requirements

#### 3.4.1 Performance
- **API Latency**: 95% of standard REST API requests must respond within **200 ms** under nominal concurrent load.
- **RAG Retrieval Speed**: Semantic vector similarity searches against `pgvector` across 5,000 document chunks must execute in under **150 ms**.
- **Frontend Bundle Performance**: The production single-page application must compile to under **350 kB** gzipped entry bundle, ensuring initial paint in $<1.2\text{ s}$ on 4G networks.

#### 3.4.2 Usability
- **Adaptive Responsive Design**: The web interface must render seamlessly across mobile viewports (360px width) up to ultra-wide desktop monitors (2560px width).
- **Accessibility**: Interface components must satisfy WCAG 2.1 Level AA contrast ratios ($\ge 4.5:1$ for normal text) and support full keyboard navigation.
- **Cognitive Clarity**: Mathematical proofs must render crisp, vector-scaled KaTeX typography without horizontal page layout breaking.

#### 3.4.3 Security
- **Cryptographic Password Hashing**: User credentials must be hashed using Argon2id with parameters $m=65536\text{ KiB}, t=3, p=4$.
- **Token Signing**: Client tokens must use RS256 with 2048-bit asymmetric keys; internal microservice communication must use Ed25519 signing.
- **Data Protection**: Document chunks and student study materials must be isolated by `student_id` foreign keys enforced at the SQL query layer.

#### 3.4.4 Reliability
- **Transactional Consistency**: Relational database operations must operate under `READ COMMITTED` isolation level with ACID transactional integrity.
- **Idempotent Operations**: Asynchronous event handlers and financial checkout webhooks must utilize Redis-backed idempotency keys to prevent duplicate state mutation.
- **Fault-Tolerant AI Fallback**: If external LLM API endpoints experience rate limits or network degradation, LangGraph must execute deterministic template fallbacks without crashing the user session.

#### 3.4.5 Maintainability
- **Domain-Driven Microservices Isolation**: The twelve backend microservices must maintain independent database schemas and communicate exclusively via published REST contracts or RabbitMQ events.
- **Strict Architecture Boundaries**: Automated architecture fitness tests must scan the Python import graph to guarantee zero prohibited cross-service module imports.
- **Type Safety**: Frontend code must pass strict TypeScript compilation (`tsc -b --pretty false`) with zero `any` type bypasses.

#### 3.4.6 Scalability
- **Connection Pooling**: Backend services must utilize PgBouncer connection pooling to support at least 500 concurrent client sessions against Neon PostgreSQL.
- **Horizontal Worker Scaling**: Asynchronous document ingestion and test generation workers must scale horizontally as stateless Docker containers.

#### 3.4.7 Portability
- **Dual Deployment Architecture**: The platform must deploy cleanly both as a multi-container Docker Compose stack on Ubuntu/Debian Linux, and as a serverless full-stack deployment on Vercel.
- **Cross-Browser Compatibility**: The user interface must operate without functional degradation across Google Chrome, Mozilla Firefox, Microsoft Edge, and Apple Safari.

#### 3.4.8 Compliance
- **Higher Education Regulatory Alignment**: Course attendance calculations must enforce the mandatory 75% HEC examination eligibility threshold.
- **Financial Accounting Standards**: General ledger accounting routines must adhere to GAAP double-entry debit/credit reconciliation.

#### Table 3.31: Summary of Non-Functional Requirements

| Requirement ID | Category | Target Metric / Evaluation Standard | Verification Mechanism |
| :--- | :--- | :--- | :--- |
| **NFR-001** | **Performance** | API response $\le 200\text{ ms}$; Vector search $\le 150\text{ ms}$ | Automated HTTP benchmarks & Locust load tests |
| **NFR-002** | **Scalability** | Support 500 concurrent sessions without lock contention | Concurrent PgBouncer connection tests |
| **NFR-003** | **Security** | Argon2id hashing; RS256 / Ed25519 cryptographic tokens | Security unit test suite (`test_security.py`) |
| **NFR-004** | **Privacy** | Strict multi-tenant isolation by `student_id` | Automated tenant boundary isolation tests |
| **NFR-005** | **Reliability** | Zero duplicate financial postings on network retry | Redis idempotency verification tests |
| **NFR-006** | **AI Grounding** | 100% of generated questions cite extracted topics | Pydantic JSON schema gatekeeper assertion |
| **NFR-007** | **Usability** | WCAG 2.1 Level AA compliance; Full mobile responsiveness | Playwright automated cross-viewport journeys |
| **NFR-008** | **Portability** | 1-Click execution via Docker Compose & Vercel serverless | Clean container deployment validation script |

---

# Chapter 4: Design and Architecture

## 4 Design and Architecture
SmartEdu is architected as an enterprise-grade distributed system combining decoupled, domain-driven microservices for core institutional operations with a serverless API Gateway and an asynchronous LangGraph AI pipeline. This chapter details the layered architecture, process flows, module specifications, and UML structural and behavioral models.

### 4.1 System Architecture
The system architecture is structured across six cohesive tiers designed to enforce high separation of concerns, scalability, and strict security isolation.

```mermaid
flowchart TD
    subgraph ClientTier ["1. Client Presentation Layer (React 19 / TypeScript / Vite)"]
        GatewayUI["Universal Public Gateway (/explore)"]
        StudentUI["Student Academic Cockpit (/app/student)"]
        TeacherUI["Faculty Workspace (/app/teacher)"]
        AdminUI["Institutional Admin (/app/admin)"]
        KaTeXEngine["KaTeX Mathematical Typesetting Engine"]
    end

    subgraph SecurityTier ["2. Edge & Security Middleware Layer"]
        CORSGuard["CORS & Origin Filtering"]
        JWTAuth["RS256 JWT Token & Role Validator"]
        RateLimiter["Sliding-Window Rate Limiter"]
        Idempotency["Redis Idempotency Verifier"]
    end

    subgraph GatewayTier ["3. Unified API Gateway Layer (Port 18080 / api/index.py)"]
        APIRouter["Dynamic REST Path Router"]
        JWKSMock["In-Process JWKS & Zero-Network Dispatch"]
        PathNormalizer["Vercel Trailing-Slash Normalizer"]
    end

    subgraph ServiceTier ["4. Domain Microservices Layer (FastAPI / Python 3.12)"]
        IdentitySvc["Identity & Auth (:8001)"]
        AcademicSvc["Academic & Enrollment (:8002)"]
        AttendanceSvc["Attendance (:8003)"]
        SchedulingSvc["Timetable & Scheduling (:8004)"]
        FacilitySvc["Facility & Space Finder (:8006)"]
        TransitSvc["Smart Transit & Fleet (:8006/transit)"]
        LearningSvc["Learning & AI Studio (:8007)"]
        FinanceSvc["Finance & GL Ledger (:8011)"]
        PayrollSvc["Payroll & HR (:8012)"]
    end

    subgraph AITier ["5. AI & Autonomous Assessment Engine (LangGraph & Gemini)"]
        LangGraphPipe["LangGraph Cyclical State Machine"]
        GeminiFlash["Google Gemini 2.0 Flash"]
        GeminiEmbed["Google text-embedding-004"]
        ProofSolver["Step-by-Step LaTeX Solver"]
    end

    subgraph DataTier ["6. Persistent Data & Messaging Layer"]
        PostgresDB[(PostgreSQL 16 - 12 Schemas)]
        PgVector[(pgvector - Vector Index)]
        RabbitMQ[(RabbitMQ 4.1 Event Bus)]
        RedisCache[(Redis 7.4 Idempotency Cache)]
        S3Storage[(MinIO / S3 Document Vault)]
    end

    ClientTier --> SecurityTier
    SecurityTier --> GatewayTier
    GatewayTier --> ServiceTier
    LearningSvc --> AITier
    ServiceTier --> DataTier
    AITier --> PgVector
```
**Figure 4.1: Layered System Architecture of SmartEdu**

#### 4.1.1 Client Layer (Frontend Interface)
Built with React 19, TypeScript, and Vite, the frontend delivers a zero-latency Single Page Application (SPA). TanStack Query manages server state caching, optimistic UI updates, and background data synchronization. KaTeX provides instant client-side rendering of complex mathematical formulas without external network calls.

#### 4.1.2 Edge and Security Middleware Layer
Every incoming request is intercepted by edge middleware that validates CORS headers, checks client IP against sliding-window rate limiters, verifies RS256 JWT signatures, inspects required role claims, and enforces Redis-backed idempotency tokens on mutating requests.

#### 4.1.3 Application Layer (Microservices & Serverless Gateway)
Business logic is encapsulated across twelve domain microservices implemented in FastAPI. The services expose OpenAPI-compliant REST endpoints. When deployed on Vercel, `api/index.py` dynamically mounts all microservice routers into a single unified ASGI application using in-process zero-network JWKS dispatch to optimize cold-start performance.

#### 4.1.4 AI and Autonomous Learning Layer
The Learning Service incorporates a cyclical LangGraph state graph governing Google Gemini. Rather than issuing unconstrained prompts, the workflow routes requests through specialized validation nodes: semantic chunk retrieval, Bloom's Taxonomy question drafting, distractor plausibility auditing, and step-by-step LaTeX formula generation.

#### 4.1.5 Data Layer (PostgreSQL, pgvector, Redis & S3)
Data persistence is strictly partitioned. PostgreSQL 16 houses twelve independent database schemas, guaranteeing schema isolation. Dense vector embeddings (768-dimensional) are indexed using `pgvector`. RabbitMQ manages asynchronous domain events (e.g., student enrollment triggering fee billing), and Redis handles deduplication locks.

#### 4.1.6 Integration Layer (External Services)
SmartEdu integrates with Google Gemini API for generative AI, simulated 1Link banking gateways for fee settlement and payroll disbursement, and external SMTP services for notification delivery.

#### 4.1.7 Communication Flow
A standard request flows as follows: The user interacts with the React 19 SPA, which issues an HTTPS request with an `Authorization: Bearer <JWT>` header. The API Gateway validates the token, asserts user role permissions, and routes the payload to the appropriate microservice. The microservice executes domain operations inside an ACID transaction, emits events to RabbitMQ if state mutated, and returns typed Pydantic JSON responses with security headers.

---

### 4.2 Process Flow
The central workflow of the AI Self-Learning Studio involves turning unstructured study documents into verified, diagnostic assessment questions and tracking topic mastery over time.

```mermaid
flowchart TD
    Start([Student Uploads Study Material]) --> CheckQuota{Check 100MB Quota}
    CheckQuota -- Exceeded --> RejectUpload[Reject: HTTP 413 Quota Exceeded]
    CheckQuota -- OK --> CalcHash[Compute SHA-256 Checksum]

    CalcHash --> DupCheck{Hash Exists?}
    DupCheck -- Yes --> LinkExisting[Link Existing Document Chunks]
    DupCheck -- No --> ParseDoc[Extract Text: pypdf / docx / pptx]

    ParseDoc --> SemanticChunk[Semantic Chunker: 500 Tokens / 50 Overlap]
    SemanticChunk --> Embeddings[Google text-embedding-004]
    Embeddings --> StoreVector[(Store in PostgreSQL pgvector)]

    StoreVector --> RequestTest([Student Requests AI Test Generation])
    RequestTest --> ConfigPrompt[Configure: Question Count, Bloom Tier, Topics]

    ConfigPrompt --> RetrieveChunks[Cosine Similarity Retrieval in pgvector]
    RetrieveChunks --> LangGraphStart[LangGraph: DraftQuestionNode]

    LangGraphStart --> AuditDistractors[LangGraph: DistractorAuditorNode]
    AuditDistractors --> CheckMath{Quantitative Question?}

    CheckMath -- Yes --> LaTeXSolver[LangGraph: NumericalSolverNode with KaTeX]
    CheckMath -- No --> QualityGate[LangGraph: QualityGateNode Pydantic Check]
    LaTeXSolver --> QualityGate

    QualityGate -- Valid --> SaveAssessment[(Commit Test to Assessment DB)]
    QualityGate -- Invalid --> RetryDraft[Regenerate Question Draft]
    RetryDraft --> LangGraphStart

    SaveAssessment --> TakeTest([Student Attempts Timed Test])
    TakeTest --> AutoGrade[Deterministic Server-Side Grading]
    AutoGrade --> UpdateMastery[Calculate Topic Mastery: Strong / Moderate / Weak]
    UpdateMastery --> RenderRadar[Render SVG Mastery Radar Chart]
    RenderRadar --> SmartRegen([1-Click Smart Test Regeneration: 70% Weak Focus])
```
**Figure 4.2: Multi-Format Document Ingestion & RAG Indexing Flow**

---

### 4.3 System Modules

#### 4.3.1 Universal Adaptive Gateway & Main Dashboard Module
The gateway module provides the public entry point at `/` and `/explore`, presenting eight cards (*Student Portal, Free Slots, Timetable, Campus Hub, Transport Service, Faculty, Sports Week, Self Assessment*). It manages tab routing and directs authenticated users to their designated role dashboards.

#### 4.3.2 Student Academic Cockpit & Course Command Center Module
Consolidates student course operations. It monitors HEC attendance compliance, displaying warning banners and calculating required consecutive lectures if attendance drops below 75%. Each course expands into eight sub-cards: *Assignments, Quizzes, Attendance, Marks, Notifications, Resources, Lecture Hub, Course Information*.

#### 4.3.3 Intelligent Timetable & Schedule Engine Module
Processes lecture schedules across Student (by section with student capacities) and Teacher perspectives. It provides an hour-by-hour timeline with a moving current-time marker, room capacity telemetry, and 1-click `.ics` calendar export.

#### 4.3.4 Dynamic Space Finder & Free Slot Navigator Module
Maintains real-time classroom vacancy maps across Block A, Block B, Block C, Block D, and Engineering Labs. Features include an "Available Right Now" filter, equipment inventory tags, "Free Until" indicators, and 90-minute reservation holds with QR check-in governance.

#### 4.3.5 Smart Transit & Fleet Telemetry Module
Tracks campus commuter buses (Farid Town Point, Mall Road Express, Canal Line) and intra-campus loops. It computes stop-by-stop ETAs, monitors bus capacities (*Seats Available, Standing Only, Full*), and broadcasts service disruption alerts.

#### 4.3.6 Campus Hub, Directory & Spatial Wayfinding Module
A multi-division registry covering Faculty, Administrative Offices with live queue token counters, Classrooms, Specialized Labs with equipment inventories, Library study-seat occupancy meters, and interactive SVG floor blueprints.

#### 4.3.7 Campus Life, Marquee Events & Sports Gala Portal Module
A calendar-aware event management engine that morphs seasonally (Spring Sports Week, Fall Tech Gala, Winter Convocation). It renders day-grouped fixtures, interactive knockout elimination brackets, and department trophy leaderboards.

#### 4.3.8 AI Self-Learning & Adaptive Assessment Studio Module
The core intelligence engine. It manages student subject vaults, coordinates multi-format ingestion (PDF, DOCX, PPTX), runs the LangGraph Bloom's Taxonomy test generator via Google Gemini, authors step-by-step KaTeX mathematical derivations, renders SVG Topic Mastery Radar charts, and triggers adaptive smart test regeneration.

```mermaid
flowchart TD
    Query([Test Generation Request]) --> RetrievalNode["1. RetrievalNode: pgvector Cosine Search"]
    RetrievalNode --> DraftNode["2. DraftQuestionNode: Gemini 2.0 Flash"]
    DraftNode --> DistractorNode["3. DistractorAuditorNode: Plausibility Check"]
    DistractorNode --> QuantCheck{Quantitative Item?}
    QuantCheck -- Yes --> SolverNode["4. NumericalSolverNode: KaTeX Step-by-Step Proof"]
    QuantCheck -- No --> QualityNode["5. QualityGateNode: Pydantic Schema Validation"]
    SolverNode --> QualityNode
    QualityNode -- Passes Schema --> FinalTest([Finalized JSON Assessment])
    QualityNode -- Schema Violation --> DraftNode
```
**Figure 4.3: Cyclical LangGraph Test Generation & Verification Pipeline**

#### 4.3.9 Identity, Authentication & Role Governance Module
Implements Argon2id password hashing, RS256 JWT generation, Ed25519 inter-service token minting, sliding-window rate limiting, and role-based route guards (`/login/student`, `/login/faculty`).

#### 4.3.10 Institutional Finance & General Ledger Module
Implements double-entry bookkeeping ($\sum \text{Debits} = \sum \text{Credits}$), fee structure versioning, installment plans, overdue penalty calculation (10-day grace period, flat PKR 500 fee), and maker-checker dual approval for refunds.

#### 4.3.11 Automated Payroll & Compensation Module
Calculates monthly employee salaries via a gross-to-net computation engine (Base + Allowances - Deductions), enforces maker-checker segregation of duties on run approvals, and executes simulated 1Link bank disbursements.

#### 4.3.12 Platform Operations, Security & Audit Logging Module
Manages append-only security audit trails with automatic credential redaction, exposes microservice health/readiness probes, and manages dynamic feature flags.

---

### 4.4 Design Models

#### 4.4.1 Sequence Diagram
Figure 4.4 illustrates the end-to-end interactions between the Student, Web Client, API Gateway, Learning Service, Google Gemini API, and Database during assessment generation, testing, and diagnostic evaluation.

```mermaid
sequenceDiagram
    autonumber
    actor Student
    participant UI as React 19 Frontend
    participant GW as API Gateway (:18080)
    participant LS as Learning Service (:8007)
    participant Gemini as Google Gemini API
    participant DB as PostgreSQL (pgvector)

    Student->>UI: Select Subject & Click "Generate Test"
    UI->>GW: POST /api/v1/learning/self-learning/tests/generate
    GW->>LS: Forward with Verified Student Claims
    LS->>DB: Query Relevant Chunks via Cosine Similarity
    DB-->>LS: Return Top-K Semantic Chunks
    LS->>Gemini: Prompt with Bloom's Taxonomy & Pydantic Schema
    Gemini-->>LS: Return Structured MCQ JSON
    LS->>Gemini: Verify Quantitative Items & Solve Proofs
    Gemini-->>LS: Return LaTeX Numerical Steps
    LS->>DB: Save Assessment Record (Status: READY)
    LS-->>GW: Return HTTP 201 Created (Test JSON)
    GW-->>UI: Deliver Test Payload to Frontend
    UI->>Student: Render Interactive Test Runner with Timer
    Student->>UI: Select Answers & Click "Submit Test"
    UI->>GW: POST /api/v1/learning/self-learning/tests/{id}/submit
    GW->>LS: Evaluate Choices Against Answer Key
    LS->>DB: Save Attempt Scores & Durations
    LS->>LS: Update Topic Mastery Aggregates
    LS-->>GW: Return Diagnostic Evaluation Payload
    GW-->>UI: Deliver Score, Explanations & LaTeX Proofs
    UI->>Student: Display Review Screen & SVG Mastery Radar
```
**Figure 4.4: Sequence Diagram for Student Test Generation, Attempt & Grading**

#### 4.4.2 Class Diagram
Figure 4.5 illustrates the domain entities, relationships, and methods of the core educational, assessment, and timetable subsystems.

```mermaid
classDiagram
    class Student {
        +UUID id
        +String rollNumber
        +String department
        +Int semester
        +getEnrolledCourses()
        +getStudyQuotaUsage()
    }

    class CourseOffering {
        +UUID id
        +String code
        +String title
        +Int creditHours
        +String section
        +calculateAttendanceRate()
        +isEligibleForExam()
    }

    class AttendanceRecord {
        +UUID id
        +Date lectureDate
        +Int lectureNumber
        +String status
        +String excuseDocumentUrl
    }

    class SubjectVault {
        +UUID id
        +String name
        +String code
        +String department
        +Int totalMaterials
        +Float storageUsedBytes
        +addMaterial(file)
    }

    class StudyMaterial {
        +UUID id
        +String title
        +String fileType
        +String sha256Checksum
        +Int fileSizeBytes
        +extractAndChunk()
    }

    class DocumentChunk {
        +UUID id
        +String contentText
        +Vector embedding768
        +String topicTag
    }

    class Assessment {
        +UUID id
        +String title
        +String bloomTier
        +Int timeLimitMinutes
        +Int totalQuestions
        +evaluateAttempt(answers)
    }

    class QuestionItem {
        +UUID id
        +String prompt
        +List options
        +Int correctIndex
        +String rationale
        +String latexProof
        +String topic
    }

    class AssessmentAttempt {
        +UUID id
        +Float scorePercentage
        +Int timeTakenSeconds
        +DateTime attemptedAt
    }

    class TimetableSlot {
        +UUID id
        +String dayOfWeek
        +String slotTime
        +String roomCode
        +String block
        +Int capacity
        +exportToICS()
    }

    Student "1" --> "*" CourseOffering : enrolls
    CourseOffering "1" --> "*" AttendanceRecord : logs
    Student "1" --> "*" SubjectVault : creates
    SubjectVault "1" --> "*" StudyMaterial : contains
    StudyMaterial "1" --> "*" DocumentChunk : chunks into
    SubjectVault "1" --> "*" Assessment : generates
    Assessment "1" --> "*" QuestionItem : comprises
    Assessment "1" --> "*" AssessmentAttempt : records
    CourseOffering "1" --> "*" TimetableSlot : scheduled in
```
**Figure 4.5: Class Diagram for the SmartEdu Core Educational & Assessment Domain**

---

# Chapter 5: Implementation

## 5 Implementation
This chapter details the concrete implementation of SmartEdu, including core algorithms in formal pseudocode, external libraries, and visual documentation of key user interfaces.

### 5.1 Algorithms

#### 5.1.1 Multi-Tenant Role-Enforced Login Algorithm
```text
Algorithm: AuthenticateAndEnforceRole
Input: email (string), password (string), targetPortalRole (string), clientIP (string)
Output: JWT access token and session cookie, or rejection error

1. Apply sliding-window rate limit on (clientIP, email);
   if attempts in last 60 seconds > 5 then
       raise HTTP 429 ("Rate limit exceeded. Try again in 60 seconds.");
   end if

2. Query database for User record matching email;
   if User record not found then
       execute constant-time dummy password hash comparison;
       raise HTTP 401 ("Invalid email or password.");
   end if

3. Verify password against stored Argon2id hash;
   if password verification fails then
       log security audit failure event;
       raise HTTP 401 ("Invalid email or password.");
   end if

4. Check user roles array:
   if targetPortalRole is specified and targetPortalRole not in User.roles then
       log unauthorized portal access attempt;
       raise HTTP 403 ("Access denied: Insufficient role permissions for this portal.");
   end if

5. Generate RS256 JWT access token with claims:
   sub = User.id, roles = User.roles, permissions = User.permissions,
   iss = "http://localhost:8001", aud = "smartedu-platform",
   iat = currentTime, exp = currentTime + 15 minutes, jti = generateUUID();

6. Generate rotating cryptographic refresh token;
   store SHA-256 hash of refresh token in database with 7-day expiry;

7. Set HttpOnly, Secure, SameSite=Lax cookie containing refresh token;
8. Write login audit event to audit outbox;
9. Return HTTP 200 with access token and user metadata profile.
```

#### 5.1.2 Multi-Format Document Ingestion & Deduplication Algorithm
```text
Algorithm: IngestAndIndexDocument
Input: studentId (UUID), subjectId (UUID), fileBytes (binary), fileName (string)
Output: Document ingestion summary with extracted topic units

1. Validate file extension and magic byte signature;
   if extension not in [".pdf", ".docx", ".pptx"] then
       raise HTTP 415 ("Unsupported media format. Upload PDF, DOCX, or PPTX.");
   end if

2. Calculate aggregate storage used by studentId;
   if currentStorage + length(fileBytes) > 100 Megabytes then
       raise HTTP 413 ("Storage quota exceeded. Limit is 100MB per student.");
   end if

3. Compute fileHash = SHA-256(fileBytes);
4. Check database for existing StudyMaterial where student_id = studentId and sha256 = fileHash;
   if duplicate found then
       link existing document to subjectId;
       return existing document metadata with status "DUPLICATE_LINKED";
   end if

5. Parse file text according to format:
   if format is PDF then extract text blocks via pypdf / pdfplumber;
   else if format is DOCX then extract paragraphs and tables via python-docx;
   else if format is PPTX then extract slide shapes via python-pptx;
   end if

6. Split normalized text into semantic chunks of 500 tokens with 50-token sliding overlap;
7. For each chunk:
       embedding = Google_Gemini_Embedding(chunk.text, model="text-embedding-004");
       insert into learning_document_chunks (chunk_text, embedding, student_id, subject_id);
   end for

8. Extract topic tags using Gemini Topic Extraction prompt;
9. Update SubjectVault storage meter and topic registry;
10. Return HTTP 201 with document ID, chunk count, and discovered topics.
```

#### 5.1.3 LangGraph Bloom's Taxonomy Test Generation Algorithm
```text
Algorithm: GenerateBloomsTaxonomyAssessment
Input: subjectId (UUID), questionCount (int), bloomTier (string), topicFilters (list)
Output: Validated assessment JSON object conforming to Pydantic schema

1. Initialize LangGraph StateGraph with schema:
   State = {topics: list, contextChunks: list, rawQuestions: list, validatedQuestions: list}

2. Execute Node 1 (RetrievalNode):
   if topicFilters is not empty then
       queryText = concatenate(topicFilters);
   else
       queryText = fetchSubjectSyllabusSummary(subjectId);
   end if
   queryVector = Google_Gemini_Embedding(queryText);
   contextChunks = ExecuteSQL("SELECT content FROM learning_document_chunks 
                              WHERE subject_id = :subjectId 
                              ORDER BY embedding <=> :queryVector LIMIT 10");

3. Execute Node 2 (DraftQuestionNode):
   systemPrompt = constructBloomsPrompt(bloomTier, questionCount);
   rawJSON = Google_Gemini_Generate(prompt=systemPrompt, context=contextChunks, 
                                   model="gemini-2.0-flash", response_schema=AssessmentSchema);

4. Execute Node 3 (DistractorAuditorNode):
   for each question in rawJSON.questions:
       verify that distractors are mutually exclusive and grammatically congruent;
       assert that exactly one option is marked correct;
   end for

5. Execute Node 4 (NumericalSolverNode):
   for each question in rawJSON.questions:
       if isQuantitative(question.prompt) then
           latexProof = Google_Gemini_GenerateProof(question.prompt, question.options[question.correctIndex]);
           question.latexProof = latexProof;
       end if
   end for

6. Execute Node 5 (QualityGateNode):
   validate entire payload against Pydantic TestSchema;
   if validation fails then
       re-enter DraftQuestionNode with error feedback;
   else
       persist Assessment to database with status READY;
       return Assessment JSON;
   end if
```

#### 5.1.4 Step-by-Step LaTeX Numerical Proof & Audit Algorithm
```text
Algorithm: AuthorAndAuditNumericalProofs
Input: questionPrompt (string), correctOption (string), documentContext (string)
Output: Validated KaTeX-compliant step-by-step mathematical derivation string

1. Identify mathematical variables, units, equations, and numerical constants in prompt;
2. Formulate step-by-step prompt:
   "Given the problem: [questionPrompt] and answer: [correctOption],
    construct an exhaustive, pedagogical mathematical proof.
    Express every step in explicit LaTeX math notation.
    Include initial formula statement, variable substitution, intermediate arithmetic,
    and final boxed answer. Ensure all symbols compile under KaTeX."

3. Invoke Google Gemini API with temperature = 0.1 to enforce deterministic arithmetic;
4. Receive raw derivation text;
5. Validate LaTeX delimiter balance:
   count of opening "$" must equal count of closing "$";
   count of opening "$$" must equal count of closing "$$";
   if mismatch detected then
       repair unescaped symbols and sanitize delimiters;
   end if

6. Execute regex scan for unsupported KaTeX macros (e.g., \DeclareMathOperator);
   replace with standard LaTeX equivalents (e.g., \operatorname);
7. Return sanitized KaTeX proof string.
```

#### 5.1.5 Topic Mastery Profiling & Cognitive Radar Algorithm
```text
Algorithm: ComputeTopicMasteryRadar
Input: studentId (UUID), subjectId (UUID)
Output: List of topic mastery records with radial coordinates for SVG rendering

1. Query all completed AssessmentAttempt records for studentId under subjectId;
2. Initialize topicScores = Dictionary<string, list of (score, timestamp)>;
3. For each attempt in historical attempts:
       for each question in attempt.questions:
           record whether question was answered correctly along with attempt timestamp;
           append to topicScores[question.topic];
       end for
   end for

4. For each topic, scoresList in topicScores:
       # Apply recency-weighted exponential smoothing
       totalWeight = 0; weightedSum = 0;
       for score, timestamp in scoresList:
           ageDays = (currentTime - timestamp).inDays();
           weight = exp(-0.05 * ageDays);
           weightedSum += (score ? 1.0 : 0.0) * weight;
           totalWeight += weight;
       end for
       masteryPercentage = (weightedSum / totalWeight) * 100;

       if masteryPercentage >= 75.0 then tier = "STRONG";
       else if masteryPercentage >= 50.0 then tier = "MODERATE";
       else tier = "WEAK";
       end if
   end for

5. Calculate radial polygon vertices for SVG rendering:
   N = count(topics); angleStep = (2 * PI) / N;
   for index i from 0 to N-1:
       r = (masteryPercentage[i] / 100) * maxRadius;
       x = centerX + r * cos(i * angleStep - PI / 2);
       y = centerY + r * sin(i * angleStep - PI / 2);
       append (x, y) to svgPolygonPoints;
   end for

6. Return topics, tier classifications, and svgPolygonPoints string.
```

#### 5.1.6 Adaptive Weakness-Remediating Test Regeneration Algorithm
```text
Algorithm: RegenerateWeaknessTargetedTest
Input: studentId (UUID), subjectId (UUID), requestedQuestionCount (int)
Output: Provisioned adaptive assessment targeting identified knowledge gaps

1. Execute ComputeTopicMasteryRadar(studentId, subjectId);
2. Partition topics into weakTopics (mastery < 50%) and reinforcementTopics (mastery >= 50%);
3. If weakTopics is empty then
       # Student has mastered all current topics; invoke Challenge Mode
       return GenerateBloomsTaxonomyAssessment(subjectId, requestedQuestionCount, 
                                              bloomTier="Hard", topicFilters=[]);
   end if

4. Compute question quota allocation:
   weakCount = round(0.70 * requestedQuestionCount);
   reinforcementCount = requestedQuestionCount - weakCount;

5. Fetch document chunks tagged with weakTopics;
6. If count(weakTopics) > weakCount then
       selectedWeakTopics = sample top lowest-scoring topics from weakTopics;
   else
       selectedWeakTopics = weakTopics;
   end if

7. Trigger LangGraph generation:
   prompt = "Synthesize an adaptive test addressing persistent student misconceptions.
             Focus 70% of analytical items on: [selectedWeakTopics].
             Reinforce foundational concepts on: [reinforcementTopics].";
8. Return generated adaptive assessment.
```

#### 5.1.7 Double-Entry General Ledger Balance & Installment Algorithm
```text
Algorithm: PostDoubleEntryFeeTransaction
Input: invoiceId (UUID), studentId (UUID), paymentAmount (Decimal), channel (string)
Output: Receipt record and updated ledger balances

1. Acquire transaction lock on invoice record;
2. Query Invoice where id = invoiceId and student_id = studentId;
   if invoice.status == "PAID" then
       raise HTTP 400 ("Invoice has already been settled in full.");
   end if

3. Check grace period and overdue penalty:
   if currentTime > invoice.dueDate + 10 days and invoice.lateFeeApplied == False then
       invoice.totalAmount += 500.00; # Apply flat PKR 500 penalty
       invoice.lateFeeApplied = True;
   end if

4. Inside an atomic database transaction:
       # Double-entry posting: Debit Cash, Credit Accounts Receivable
       entryHeader = createJournalEntryHeader(date=currentTime, reference=invoiceId);
       
       debitLine = createJournalLine(account="Cash_Settlement", debit=paymentAmount, credit=0.00);
       creditLine = createJournalLine(account="Accounts_Receivable_Tuition", debit=0.00, credit=paymentAmount);
       
       # Assert the fundamental accounting invariant
       assert sum(debits) == sum(credits), "FATAL: Double-entry ledger imbalance detected!";
       
       insert entryHeader, debitLine, creditLine;
       
       invoice.paidAmount += paymentAmount;
       if invoice.paidAmount >= invoice.totalAmount then
           invoice.status = "PAID";
       else
           invoice.status = "PARTIALLY_PAID";
       end if
   end atomic transaction

5. Emit `finance.invoice.paid.v1` event to RabbitMQ;
6. Return digital electronic receipt with transaction hash.
```

#### 5.1.8 Real-Time Transit Arrival (ETA) Calculation Algorithm
```text
Algorithm: CalculateStopArrivalETAs
Input: routeId (string), currentBusCoordinates (lat, lon), currentSpeed (km/h)
Output: Ordered list of route stops with scheduled vs estimated arrival times

1. Load ordered list of stops for routeId: [Stop_1, Stop_2, ..., Stop_N];
2. Identify current traversed segment between Stop_K and Stop_K+1;
3. For each upcoming stop Stop_M (where M > K):
       baseDistanceKm = calculateRoadDistance(currentBusCoordinates, Stop_M.coordinates);
       
       if currentSpeed > 5.0 then
           effectiveSpeed = (0.7 * currentSpeed) + (0.3 * historicalSegmentSpeed);
       else
           # Heavy traffic or standstill at bus stop
           effectiveSpeed = historicalSegmentSpeed * 0.5;
       end if
       
       travelTimeMinutes = (baseDistanceKm / effectiveSpeed) * 60;
       
       # Add 2-minute average passenger boarding dwell time for intermediate stops
       intermediateStopsCount = M - K - 1;
       totalDwellMinutes = intermediateStopsCount * 2.0;
       
       calculatedETA = currentTime + travelTimeMinutes + totalDwellMinutes;
       
       Stop_M.estimatedArrivalTime = calculatedETA;
       Stop_M.delayMinutes = max(0, calculatedETA - Stop_M.scheduledArrivalTime);
   end for

4. Check for active disruption bulletins matching routeId;
   if disruption found then
       attach alertBanner with severity and diversion details;
   end if

5. Return formatted route itinerary.
```

---

### 5.2 External APIs and Libraries

#### 5.2.1 Google Gemini API & text-embedding-004
Google Gemini powers the platform's generative reasoning and vector embeddings. `gemini-2.0-flash` is leveraged for high-speed, schema-constrained question generation and step-by-step mathematical reasoning. `text-embedding-004` generates 768-dimensional dense vector embeddings of textbook chapters and course slide chunks.

#### 5.2.2 LangGraph & LangChain StateGraph
LangGraph coordinates multi-node agentic workflows as cyclical state graphs. It enforces deterministic transitions between document chunk retrieval, question drafting, distractor plausibility auditing, and Pydantic schema validation gates.

#### 5.2.3 pgvector & PostgreSQL 16
`pgvector` provides in-database vector indexing and similarity search using cosine and Euclidean distance metrics directly within PostgreSQL, eliminating the operational overhead of third-party vector databases.

#### 5.2.4 Document Extractors (pypdf, python-docx, python-pptx)
A multi-format parser pipeline that extracts text headers, structured tables, and body paragraphs from PDF syllabi, Microsoft Word documents, and PowerPoint slide decks.

#### 5.2.5 KaTeX & Mathematical Rendering
KaTeX delivers fast client-side rendering of LaTeX equations. It converts raw mathematical proof strings into accessible vector math without layout shift or external network dependencies.

#### 5.2.6 FastAPI, Pydantic v2 & SQLAlchemy 2.0
FastAPI delivers asynchronous RESTful API endpoints. Pydantic v2 enforces compile-time and runtime schema validation, and SQLAlchemy 2.0 provides an asynchronous ORM interfacing with PostgreSQL.

#### 5.2.7 PyJWT, Cryptography & Password Hashing
PyJWT signs and verifies RS256 and Ed25519 tokens. `pwdlib` implements Argon2id password hashing, and the Python `cryptography` package secures sensitive tokens and session data.

#### 5.2.8 React 19, TypeScript & Vite
The frontend client is built with React 19 and TypeScript 5.9, utilizing Vite 8 for fast hot-module replacement and optimized tree-shaken production bundles.

#### 5.2.9 Tailwind CSS & Lucide React
Tailwind CSS 4.3 provides a utility-first styling system supporting light and dark themes. Lucide React provides an accessible, consistent vector icon set.

#### 5.2.10 TanStack Query & React Hook Form
TanStack Query manages client data caching, background revalidation, and optimistic mutations. React Hook Form paired with Zod schemas manages client-side form validation.

#### Table 5.1: External APIs and Libraries used in SmartEdu

| Technology / Library | Purpose in SmartEdu | Execution Context |
| :--- | :--- | :--- |
| **Google Gemini API** (`gemini-2.0-flash`) | Structured Bloom's Taxonomy test drafting & proof solving | External Cloud API |
| **Google Embeddings** (`text-embedding-004`) | 768-dimensional dense vector generation for RAG | External Cloud API |
| **LangGraph 0.2 & LangChain 0.3** | StateGraph orchestration, distractor audit, and schema gates | Local Service (:8007) |
| **pgvector 0.3.0** | In-database cosine similarity vector index | PostgreSQL Server |
| **pypdf 5.0 & pdfplumber 0.11** | Multi-column PDF textbook and past paper text extraction | Local Service (:8007) |
| **python-docx 1.1 & python-pptx 1.0** | Word document and PowerPoint slide deck extraction | Local Service (:8007) |
| **KaTeX 0.19.1** | Real-time browser rendering of step-by-step LaTeX formulas | Client Browser |
| **FastAPI 0.115 & Pydantic v2.9** | Asynchronous REST routing, request parsing, and OpenAPI specs | Backend Services |
| **SQLAlchemy 2.0 & Alembic 1.13** | Database ORM modeling, transactions, and automated migrations | Backend Services |
| **PyJWT 2.9 & pwdlib [argon2]** | RS256 token verification, Ed25519 minting, and Argon2id hashing | Identity Service (:8001) |
| **React 19.2 & TypeScript 5.9** | Reactive component tree, typed hooks, and Single Page App | Client Browser |
| **Tailwind CSS 4.3 & Lucide React** | Design token system, responsive layout, and icon typography | Client Browser |
| **TanStack Query 5 & Zustand 5** | Server query caching, revalidation, and UI state management | Client Browser |

---

### 5.3 User Interface
The SmartEdu frontend interface features clean visual hierarchy, high information density, subtle border accents, responsive layouts, and support for both light and dark themes. The following subsections present the twelve primary screens:

#### Figure 5.1: Universal Adaptive Gateway & Main Dashboard Interface
The public landing page (`/` and `/explore`) presenting the eight core operational module cards (*Student Portal, Free Slots, Timetable, Campus Hub, Transport Service, Faculty, Sports Week, Self Assessment*), allowing instant query access without credentials.

```text
+---------------------------------------------------------------------------------------------------+
|  [Cap] COMSATS SmartEdu  [Open Campus]                     [Sun/Moon]  [Universal Sign In ->]    |
+---------------------------------------------------------------------------------------------------+
|  [Compass] Universal Adaptive Campus Gateway                                                      |
|  One Connected Campus. Every resource at your fingertips.                                         |
|  [Main Dashboard]  [Free Slots]  [Timetable]  [Campus Hub]  [Transport Service]  [Sports Week]    |
+---------------------------------------------------------------------------------------------------+
|  MAIN DASHBOARD MODULES                                                                           |
|  +--------------------+  +--------------------+  +--------------------+  +--------------------+   |
|  | [Cap]              |  | [Clock]            |  | [Calendar]         |  | [Building]         |   |
|  | Student Portal     |  | Free Slots         |  | Timetable          |  | Campus Hub         |   |
|  | Attendance & Marks |  | Block Vacancy Maps |  | Student & Faculty  |  | 6 Campus Directory |   |
|  | [Open ->]          |  | [View Slots ->]    |  | [Inspect ->]       |  | [Explore ->]       |   |
|  +--------------------+  +--------------------+  +--------------------+  +--------------------+   |
|  +--------------------+  +--------------------+  +--------------------+  +--------------------+   |
|  | [Bus]              |  | [UserCheck]        |  | [Trophy]           |  | [Sparkles]         |   |
|  | Transport Service  |  | Faculty Portal     |  | Sports Week        |  | Self Assessment    |   |
|  | City Routes & ETAs |  | Class Management   |  | Fixtures & Brackets|  | AI Study Studio    |   |
|  | [View Bus Info ->] |  | [Sign In ->]       |  | [Live Scores ->]   |  | [Launch AI ->]     |   |
|  +--------------------+  +--------------------+  +--------------------+  +--------------------+   |
+---------------------------------------------------------------------------------------------------+
```
**Figure 5.1: Universal Adaptive Gateway & Main Dashboard Interface**

#### Figure 5.2: Role-Enforced Student & Faculty Portal Authentication
Dedicated, role-guarded login interfaces (`/login/student` and `/login/faculty`) with validation of registration numbers, department designations, and Argon2id password security.

#### Figure 5.3: Student Academic Cockpit & Course Command Center Dashboard
The student landing workspace (`/app/student`) featuring upcoming lecture countdown timers, regulatory HEC attendance compliance warnings ($<75\%$), cumulative attendance dials, and enrolled course cards.

#### Figure 5.4: Subject Command Center Detail with 8 Sub-Cards
The consolidated 8-card course detail screen (`/app/student/courses/:courseId`) displaying *Assignments* (with file dropboxes), *Quizzes*, *Attendance* (with medical excuse forms), *Marks*, *Notifications*, *Resources*, *Lecture Hub* (with video player), and *Course Information*.

#### Figure 5.5: Intelligent Timetable & Schedule Engine (Student & Teacher Views)
The timetable workspace (`/app/student/timetable`) allowing users to toggle between Student view (by section, e.g., `BCS-7C` with room capacities and lecture counts) and Teacher view (e.g., `Dr. Munir Ahmad`), featuring 1-click `.ics` calendar sync.

#### Figure 5.6: Dynamic Space Finder & Free Slot Navigator with Telemetry
The space finder interface displaying vacant classrooms grouped across Block A, Block B, Block C, Block D, and Engineering Labs with "Available Right Now" toggles, equipment chips, and 90-minute study reservation holds.

#### Figure 5.7: Smart Transit & Fleet Telemetry with Stop-by-Stop Itineraries
The transit telemetry screen rendering city commuter lines (*Farid Town Point, Mall Road Express, Canal Line*) and campus shuttles, stop-by-stop arrival schedules, driver contacts, occupancy indicators, and disruption bulletins.

#### Figure 5.8: Campus Hub Directory & Interactive Vector Spatial Wayfinding
The centralized campus directory spanning Faculty & Teachers, Administrative Offices (with live queue token counters), Classrooms, Specialized Labs with equipment inventories, Library study-seat meters, and interactive SVG floor blueprints.

#### Figure 5.9: Campus Life, Marquee Events & Sports Gala Tournament Engine
The marquee events portal featuring seasonal calendar morphing (Sports Week in Spring, Tech Gala in Fall), top date pills, live match fixtures, interactive knockout elimination trees, and department trophy standings.

#### Figure 5.10: AI Self-Learning Studio with Multi-Format Material Vault
The student AI workspace (`/app/student/learning`) featuring dynamic subject creation, multi-format file ingestion (PDF, DOCX, PPTX), SHA-256 deduplication, and the live 100MB storage quota meter.

#### Figure 5.11: Interactive Test Runner with Bloom's Taxonomy & KaTeX Proofs
The interactive assessment attempt interface featuring live countdown timer, question navigator grid, multiple-choice options, and collapsible step-by-step KaTeX mathematical derivations.

#### Figure 5.12: Topic Mastery Profiler with SVG Radar Chart & Smart Regeneration
The diagnostic analytics tab displaying topic proficiencies (Strong $\ge 75\%$, Moderate $50\text{--}74\%$, Weak $<50\%$), the multi-axis SVG radar polygon, and the 1-click "Smart Regenerate" button focusing 70% of questions on identified weaknesses.

---

# Chapter 6: Testing and Evaluation

## 6 Testing and Evaluation
SmartEdu was verified across all architectural tiers, from single algorithmic functions and microservice database transactions to distributed event messaging and multi-role end-to-end browser journeys. All **1,864 backend test cases**, **41 frontend unit and contract test suites**, and **Playwright browser journeys** pass with a 100% success rate.

### 6.1 Manual Testing
Manual testing confirmed intuitive usability, visual clarity, edge-case resilience, and responsive design across desktop and mobile devices.

#### 6.1.1 System Testing
System testing validated complete operational workflows on live Docker containers and Vercel serverless staging deployments.

#### Table 6.1: Manual System Testing Matrix (ST-01 to ST-06)

| Test ID | Operational Scenario | Execution Steps | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ST-01** | **Complete Student Journey** | Register account, sign into `/login/student`, inspect attendance warnings, upload course slide PDF, generate 10-question AI test, submit attempt, and inspect KaTeX proofs. | Registration succeeds, PDF text chunks into `pgvector`, Gemini drafts 10 questions, test grades instantly, KaTeX derivations render without syntax errors. | Fully verified; score and topic radar update cleanly. | **Pass** |
| **ST-02** | **Faculty Timetable & Attendance** | Log into `/login/faculty`, view teaching timetable for `Dr. Munir Ahmad`, verify room `C-204` allocation, and execute bulk attendance marking. | Timetable lists assigned slots; attendance session opens and records `PRESENT`/`ABSENT` states in database. | Timetable and attendance persist; records lock upon finalize. | **Pass** |
| **ST-03** | **Dynamic Space Reservation** | Open Space Finder, filter by "Available Right Now" in Block C, locate Room `C-204`, and click "Reserve for Study Group". | Room card shows capacity (45 students), equipment tags, and holds 90-minute reservation with QR check-in token. | Reservation created; auto-release timer active. | **Pass** |
| **ST-04** | **Transit Fleet & Disruption Check** | Open Transport Service, inspect *Farid Town Point* morning route, verify stop arrival times, and check emergency disruption alert. | Timetable lists stop-by-stop ETAs, bus driver contact, and displays high-visibility route diversion banner. | Route timeline and emergency bulletin match backend data. | **Pass** |
| **ST-05** | **Finance Ledger & Maker-Checker** | Generate semester invoice with 25% Merit Scholarship, execute checkout settlement via 1Link adapter, and test refund dual-control guard. | Double-entry postings balance ($\sum D = \sum C$); invoice marks `PAID`; student attempting self-refund receives HTTP 403 Forbidden. | Accounting invariant verified; maker-checker blocks self-approval. | **Pass** |
| **ST-06** | **Universal Gateway Responsive Test** | Access public gateway `/explore` on mobile browser viewport (375px width), test theme toggle, and navigate to Campus Hub. | All 8 module cards stack responsively; theme switches between light and dark; directory search operates smoothly. | Zero horizontal scroll overflow; layout adapts cleanly. | **Pass** |

---

#### 6.1.2 Unit Testing
Unit tests verified cryptographic primitives, mathematical algorithms, and security invariants in isolation.

#### Table 6.2: Unit Testing Specifications & Mathematical Invariants

| No. | Test Script / Function | Test Input & Attributes | Expected Mathematical / Algorithmic Result | Result |
| :--- | :--- | :--- | :--- | :--- |
| **1** | `test_argon2id_password_hashing` | `pwd="StudentSecure2026!"`, $m=65536, t=3, p=4$ | Produces valid Argon2id hash; verifies in constant time; rejects mismatched or truncated passwords. | **Pass** |
| **2** | `test_double_entry_balance_invariant` | Credits: `[Tuition: 45000]`, Debits: `[Cash: 33750, Scholarship: 11250]` | $\sum \text{Debits} \equiv \sum \text{Credits}$; ledger invariant holds; rejects unbalanced journal entries with `AssertionError`. | **Pass** |
| **3** | `test_latex_proof_delimiter_sanitization` | Raw text with mismatched `$$` delimiters and `\DeclareMathOperator` | Sanitize routine balances delimiters and replaces unsupported macros with standard KaTeX-compatible tokens. | **Pass** |
| **4** | `test_recency_weighted_topic_mastery` | Historical attempts: `[100% (30d ago), 40% (2d ago)]` | Exponential decay penalizes older successes; weighted score reflects recent failure ($<50\%$), classifying topic as `WEAK`. | **Pass** |
| **5** | `test_sha256_document_deduplication` | Binary stream of 4MB syllabus PDF | Produces identical 64-char hex digest; prevents duplicate chunking and suppresses redundant vector embeddings. | **Pass** |

---

#### 6.1.3 Functional Testing
Functional tests verified feature compliance against the functional requirements catalog.

#### Table 6.3: Functional Testing Results & Acceptance Criteria

| No. | Test Case / Script | Target Functional Requirement | Expected System Behavior | Result |
| :--- | :--- | :--- | :--- | :--- |
| **1** | Role-Enforced Student Login | **FR-001** | Student credentials grant access to `/app/student`; access to `/app/admin` is blocked with HTTP 403. | **Pass** |
| **2** | 100MB Storage Quota Meter | **FR-002** | Uploads under 100MB succeed; an upload exceeding 100MB is rejected with HTTP 413. | **Pass** |
| **3** | Document Vector Indexing | **FR-003, FR-004** | Extracted text chunks produce 768-dimensional vectors stored in `pgvector` partitioned by `student_id`. | **Pass** |
| **4** | Bloom's Taxonomy Test Generation | **FR-005** | LangGraph outputs structured JSON assessment with questions matching requested cognitive level. | **Pass** |
| **5** | KaTeX Mathematical Derivations | **FR-006** | Quantitative questions include step-by-step LaTeX proofs renderable in the client review screen. | **Pass** |
| **6** | Instant Server-Side Evaluation | **FR-007** | Submissions are graded deterministically; score percentages and document-cited explanations are returned. | **Pass** |
| **7** | SVG Topic Radar Generation | **FR-008** | Mastery aggregates populate multi-axis SVG radar polygon classified into Strong, Moderate, and Weak tiers. | **Pass** |
| **8** | Weakness-Targeted Regeneration | **FR-009** | 1-Click Smart Regenerate dynamically allocates 70% of questions to topics classified as Weak. | **Pass** |
| **9** | Timetable `.ics` Calendar Sync | **FR-011** | Calendar export generates RFC 5545 `.ics` file containing valid VEVENT entries with room and instructor data. | **Pass** |
| **10** | Double-Entry Financial Invoicing | **FR-014** | Invoice payments update general ledger accounts idempotently; maker-checker prevents self-approved refunds. | **Pass** |

---

#### 6.1.4 Integration Testing
Integration testing validated database schema boundaries, RabbitMQ event dispatching, and REST contract compliance across microservices.

#### Table 6.4: Integration Testing Across Microservices & Database Boundaries

| No. | Integration Test Script | Subsystems Involved | Expected Inter-Service Behavior | Result |
| :--- | :--- | :--- | :--- | :--- |
| **1** | `test_student_enrollment_fee_event` | Academic Service (:8002) & Finance Service (:8011) | Emitting `academic.enrollment.created.v1` over RabbitMQ causes Finance Service to provision student ledger fee account. | **Pass** |
| **2** | `test_cross_tenant_isolation_boundary` | Learning Service (:8007) & PostgreSQL `pgvector` | Student A querying vector embeddings belonging to Student B receives empty result set; cross-tenant leakage blocked. | **Pass** |
| **3** | `test_in_process_jwks_dispatch_mock` | API Gateway (`api/index.py`) & Microservice Routers | In serverless mode, zero-network JWKS mock interceptor resolves public keys in-process without network latency. | **Pass** |
| **4** | `test_redis_idempotency_checkout_replay` | Finance Service & Redis 7.4 | Replaying identical checkout request with duplicate `Idempotency-Key` returns original cached response without re-billing. | **Pass** |
| **5** | `test_phase4_e2e_isolation_suite` | Learning Service, Gemini API & Database | Full lifecycle: Subject CRUD, material ingestion, quota guard, test generation, grading, and smart regeneration verified. | **Pass** |

---

### 6.2 Automated Testing
Automated testing is integrated into the project's continuous integration pipeline via GitHub Actions. Every pull request executes static analysis, type checking, unit tests, and browser journeys.

#### Table 6.5: Automated Testing Tools and Suite Verification Summary

| Testing Framework / Tool | Scope of Application | Executed Test Suites & Coverage | Verification Outcome |
| :--- | :--- | :--- | :--- |
| **Pytest 8.4 & Hypothesis** | Backend unit, property-based, and security tests | 1,864 test cases across 12 microservices and gateway | **100% Pass Rate** (1,864 passed) |
| **Vitest 5.0 & Testing Library** | Frontend React 19 components, hooks, and contracts | 41 test cases across 15 test suites | **100% Pass Rate** (41 passed) |
| **TypeScript Compiler (`tsc`)** | Frontend static type checking and contract assertion | Entire `apps/frontend` TypeScript codebase | **0 Errors** (`tsc -b` clean) |
| **Vite Production Bundler** | Production asset tree-shaking, chunking, and syntax checks | Full client production build | **Clean Build** (740 ms) |
| **Playwright Test Runner** | Multi-role headless browser end-to-end user journeys | Critical paths: login, cockpit, timetable, AI test, finance | **All Journeys Passing** |
| **Alembic Migration Verifier** | Database schema upgrades and downgrades | 12 microservice relational database schemas | **Zero Schema Divergence** |

#### Table 6.6: Automated Testing Execution Results & Quality Gate Audits

| Suite No. | Target Test Suite File | Component Under Test | Asserted Invariant | Result |
| :--- | :--- | :--- | :--- | :--- |
| **1** | `apps/frontend/src/features/student/student-api-contract.test.ts` | Student API client | Verifies API schema normalization and typed responses. | **Pass** |
| **2** | `apps/frontend/src/features/auth/permissions.test.ts` | Role permission engine | Asserts role-guarding logic and hierarchy resolution. | **Pass** |
| **3** | `apps/frontend/src/lib/api-client-security.test.ts` | Edge security headers | Verifies bearer token attachment and credential sanitization. | **Pass** |
| **4** | `apps/frontend/src/lib/api-client-idempotency.test.ts` | Idempotency handler | Asserts UUIDv4 idempotency key generation on mutating calls. | **Pass** |
| **5** | `tests/test_phase4_e2e_isolation.py` | Multi-tenant RAG pipeline | Asserts strict `student_id` isolation across full AI lifecycle. | **Pass** |

---

# Chapter 7: Conclusion

## 7 Conclusion
SmartEdu has been successfully designed, implemented, and verified as an enterprise-scale distributed educational platform. By integrating twelve microservices, an adaptive public campus gateway, and an autonomous AI Self-Learning Studio, the platform resolves the operational fragmentation, cognitive friction, and ungrounded AI risks that challenge modern higher education institutions.

The project demonstrates that generative artificial intelligence can be safely and productively integrated into formal academic environments when governed by strict architectural constraints:
1. **Curriculum-Grounded Intelligence**: By pairing Google Gemini (`gemini-2.0-flash` and `text-embedding-004`) with a cyclical LangGraph state machine, the platform drafts objective assessments grounded in student course materials rather than open-ended model memory.
2. **Cognitive Calibration & Mathematical Rigor**: Structuring question generation across Bloom's Taxonomy tiers guarantees rigorous assessment, while the automated generation of step-by-step KaTeX mathematical derivations provides students with transparent explanations for complex STEM problems.
3. **Closing the Learning Loop**: The Topic Mastery Profiler visualizes knowledge gaps on an intuitive SVG radar chart, and the 1-click Smart Regeneration engine actively remediates identified student weaknesses by allocating 70% of questions to weak syllabus areas.
4. **Frictionless Campus Telemetry**: The Universal Adaptive Gateway makes classroom vacancies, timetable matrices, transit arrival ETAs, and campus directories accessible without login barriers, streamlining daily university life.
5. **Architectural & Financial Resilience**: Operating across twelve isolated database schemas, RabbitMQ event buses, and a GAAP-compliant double-entry general ledger, SmartEdu achieves high security, transactional integrity, and non-repudiation.

Verified across 1,864 backend test cases, 41 frontend test suites, clean TypeScript compilation, and comprehensive end-to-end browser journeys, SmartEdu represents a complete, production-ready educational management ecosystem.

---

### 7.1 Future Work

#### 7.1.1 Mobile Push Notifications & Progressive Web App Offline Mode
Extend the React 19 frontend into a full Progressive Web App (PWA) with Service Worker caching, enabling offline viewing of timetable matrices and room inventories, complemented by Web Push notifications for match start alerts and transit disruption bulletins.

#### 7.1.2 Biometric Edge Hardware Integration for Classrooms
Interface low-cost edge IoT devices (such as ESP32 microcontrollers with optical fingerprint or RFID readers) with the Attendance Service (:8003) to automate lecture attendance logging directly at classroom entry doors.

#### 7.1.3 Multi-Campus Cross-Federation Protocol
Develop an inter-campus federation protocol enabling multi-campus university systems (such as COMSATS Islamabad, Sahiwal, Lahore, and Abbottabad) to share course catalogs, faculty exchange schedules, and centralized student transcripts securely.

#### 7.1.4 Urdu Natural Language Interface & Speech Interaction
Fine-tune bilingual LoRA adapters on Google Gemini and Whisper to support speech-to-text queries in Urdu and Roman Urdu, making transit schedules and administrative queue inquiries accessible via voice commands.

#### 7.1.5 Automated HEC Compliance & Accreditation Data Exporters
Implement automated reporting modules that compile course learning outcomes (CLOs) and program learning outcomes (PLOs) directly into Higher Education Commission (HEC) and National Computing Education Accreditation Council (NCEAC) self-assessment reports.

#### 7.1.6 GPS Hardware Transit Telemetry with LoRaWAN Tracking
Deploy vehicle-mounted GPS transponders utilizing LoRaWAN or cellular telemetry to stream sub-second geographic bus coordinates to the Transit Service, replacing estimated traffic models with live GPS map overlays.

#### 7.1.7 Advanced Predictive Early-Warning Intervention Engine
Train predictive classification models on student attendance trends, quiz attempts, and historical semester grades to identify at-risk students several weeks prior to final examinations, alerting academic batch advisors automatically.

---

# References

- [1] Higher Education Commission of Pakistan, "Policy Guidelines for Implementation of Uniform Semester System in Higher Education Institutions," HEC Quality Assurance Division, Islamabad, Pakistan, Policy Doc. 14-4, 2023.
- [2] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 33, pp. 9459–9474, 2020.
- [3] Google DeepMind, "Gemini 2.0 Flash: High-Speed Multimodal Intelligence and Structured Output Capabilities," Google Research Technical Report, Dec. 2024. [Online]. Available: https://ai.google.dev/gemini-api/docs/models/gemini.
- [4] LangChain AI, "LangGraph: Multi-Agent and Cyclical Workflow Orchestration as State Graphs," LangChain Documentation, 2024. [Online]. Available: https://langchain-ai.github.io/langgraph/.
- [5] Z. Ji, N. Lee, R. Frieske, T. Yu, D. Su, et al., "Survey of Hallucination in Natural Language Generation," *ACM Computing Surveys*, vol. 55, no. 12, pp. 1–38, Dec. 2023, doi: 10.1145/3571730.
- [6] B. S. Bloom, M. D. Engelhart, E. J. Furst, W. H. Hill, and D. R. Krathwohl, *Taxonomy of Educational Objectives: The Classification of Educational Goals. Handbook I: Cognitive Domain*, New York: David McKay Company, 1956.
- [7] S. Ramírez, "FastAPI: High-Performance Asynchronous Python Web Framework," FastAPI Documentation, 2024. [Online]. Available: https://fastapi.tiangolo.com/.
- [8] PostgreSQL Global Development Group, "PostgreSQL 16.0 Documentation and pgvector Extension Manual," PostgreSQL Documentation, Oct. 2023. [Online]. Available: https://www.postgresql.org/docs/16/.
- [9] M. Jones, J. Bradley, and N. Sakimura, "JSON Web Token (JWT)," Internet Engineering Task Force (IETF), RFC 7519, May 2015, doi: 10.17487/RFC7519.
- [10] S. Josefsson and I. Liusvaara, "Edwards-Curve Digital Signature Algorithm (EdDSA)," Internet Engineering Task Force (IETF), RFC 8032, Jan. 2017, doi: 10.17487/RFC8032.
- [11] A. Biryukov, D. Dinu, and A. Khovratovich, "Argon2: The Memory-Hard Function for Password Hashing and Proof-of-Work Applications," Internet Engineering Task Force (IETF), RFC 9106, Sep. 2021, doi: 10.17487/RFC9106.
- [12] B. Desham and C. E. Wills, "iCalendar: Internet Calendaring and Scheduling Core Object Specification," Internet Engineering Task Force (IETF), RFC 5545, Sep. 2009, doi: 10.17487/RFC5545.
- [13] React Core Team, "React 19 Documentation and Server Component Specification," Meta Open Source, 2024. [Online]. Available: https://react.dev/.
- [14] Tailwind Labs, "Tailwind CSS v4: Next-Generation CSS Framework," Tailwind Labs Documentation, 2025. [Online]. Available: https://tailwindcss.com/.
- [15] Khan Academy, "KaTeX: The Fastest Math Typesetting Library for the Web," Khan Academy Open Source, 2024. [Online]. Available: https://katex.org/.
- [16] RabbitMQ Technologies, "RabbitMQ: Reliable and Mature Messaging Broker (AMQP 0-9-1 Protocol)," VMware Tanzu, 2024. [Online]. Available: https://www.rabbitmq.com/.
- [17] Redis Ltd., "Redis 7.4 Documentation: In-Memory Data Structure Store, Keyspace Notifications and Caching," Redis Documentation, 2024. [Online]. Available: https://redis.io/docs/.
- [18] W3C, "Web Content Accessibility Guidelines (WCAG) 2.1," W3C Recommendation, Jun. 2018. [Online]. Available: https://www.w3.org/TR/WCAG21/.
- [19] K. Beck, M. Beedle, A. van Bennekum, A. Cockburn, et al., "Manifesto for Agile Software Development," Agile Alliance, 2001. [Online]. Available: https://agilemanifesto.org/.
- [20] K. Schwaber and J. Sutherland, "The Scrum Guide: The Definitive Guide to Scrum: The Rules of the Game," Scrum.org, Nov. 2020. [Online]. Available: https://scrumguides.org/.
- [21] National Institute of Standards and Technology (NIST), "Digital Identity Guidelines: Authentication and Lifecycle Management," NIST Special Publication 800-63B, Jun. 2017, doi: 10.6028/NIST.SP.800-63b.

---

# Appendix A: API Endpoint Catalog

All platform endpoints are dispatched by the API Gateway under `/api/v1` and documented automatically via OpenAPI format.

#### Table A.1: FastAPI Route and Microservice Dispatch Catalog

| HTTP Method | API Gateway Route | Backend Microservice Target | Primary Functionality | Required Auth Scope |
| :--- | :--- | :--- | :--- | :--- |
| **POST** | `/api/v1/identity/auth/register` | Identity Service (:8001) | Register user profile & credentials | Public |
| **POST** | `/api/v1/identity/auth/token` | Identity Service (:8001) | Authenticate user & issue RS256 JWT | Public |
| **POST** | `/api/v1/identity/auth/refresh` | Identity Service (:8001) | Rotate refresh cookie & re-issue token | Public (Cookie) |
| **POST** | `/api/v1/identity/auth/logout` | Identity Service (:8001) | Revoke active refresh token in database | Authenticated |
| **GET** | `/api/v1/academic/courses` | Academic Service (:8002) | List academic course catalog | Authenticated |
| **GET** | `/api/v1/academic/enrollments/student` | Academic Service (:8002) | Retrieve student enrolled course details | `student` |
| **GET** | `/api/v1/attendance/summary` | Attendance Service (:8003) | Cumulative attendance percentage & dial | `student` |
| **POST** | `/api/v1/attendance/sessions/record` | Attendance Service (:8003) | Bulk mark class lecture attendance | `teacher` |
| **GET** | `/api/v1/scheduling/timetable/student` | Scheduling Service (:8004) | Query section timetable by code (e.g. BCS-7C) | Public / Student |
| **GET** | `/api/v1/scheduling/timetable/teacher` | Scheduling Service (:8004) | Query faculty teaching timetable | Public / Teacher |
| **GET** | `/api/v1/facility/rooms/free` | Facility Service (:8006) | Query vacant rooms by day, slot, block | Public |
| **POST** | `/api/v1/facility/rooms/reserve` | Facility Service (:8006) | Reserve vacant room for 90-minute hold | `student` |
| **GET** | `/api/v1/transit/routes` | Transit Service (:8006/transit) | List city routes and shuttle lines | Public |
| **GET** | `/api/v1/transit/routes/{id}/itinerary` | Transit Service (:8006/transit) | Stop-by-stop schedule & arrival ETAs | Public |
| **GET** | `/api/v1/campushub/directory` | Platform Hub Service (:8010) | Multi-division directory & queue tokens | Public |
| **GET** | `/api/v1/events/sports/fixtures` | Platform Hub Service (:8010) | Sports Gala match fixtures & brackets | Public |
| **GET** | `/api/v1/learning/self-learning/subjects`| Learning Service (:8007) | List student custom learning subjects | `student` |
| **POST** | `/api/v1/learning/self-learning/subjects`| Learning Service (:8007) | Create new student learning subject | `student` |
| **POST** | `/api/v1/learning/self-learning/materials`| Learning Service (:8007) | Upload & index PDF/DOCX/PPTX slides | `student` |
| **POST** | `/api/v1/learning/self-learning/tests/gen`| Learning Service (:8007) | LangGraph Bloom's test generator | `student` |
| **POST** | `/api/v1/learning/self-learning/tests/sub`| Learning Service (:8007) | Submit attempt & get diagnostic grade | `student` |
| **GET** | `/api/v1/learning/self-learning/analytics`| Learning Service (:8007) | Retrieve topic mastery & radar data | `student` |
| **GET** | `/api/v1/finance/invoices/student` | Finance Service (:8011) | Query semester fee invoice & installments| `student` |
| **POST** | `/api/v1/finance/checkout/settle` | Finance Service (:8011) | Settle fee invoice via 1Link adapter | `student` |
| **POST** | `/api/v1/payroll/runs/execute` | Payroll Service (:8012) | Compute monthly faculty payroll run | `admin` |
| **POST** | `/api/v1/payroll/runs/{id}/approve` | Payroll Service (:8012) | Maker-checker dual approval of payroll | `admin` (Distinct) |
| **GET** | `/api/health` | Gateway (:18080) | Microservices health & readiness probes | Public |

---

# Appendix B: Requirement Traceability Matrix

#### Table B.1: Comprehensive Requirement Traceability Matrix

| Requirement | Functional Scope | Backend Microservice / Component | Frontend Component / View | Primary Database Entities | Verified By Test Script |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **FR-001** | Multi-Factor Authentication | `identity-service/app/services/auth.py` | `pages/StudentLoginPage.tsx` | `users`, `roles`, `refresh_tokens` | `test_security.py` |
| **FR-002** | Multi-Format Ingestion | `learning-service/app/services/document_parser.py` | `MaterialLibraryTab.tsx` | `study_materials`, `student_quotas` | `test_phase4_e2e_isolation.py` |
| **FR-003** | Asynchronous Extraction | `learning-service/app/services/document_parser.py` | `MaterialLibraryTab.tsx` | `study_materials.sha256` | `test_phase4_e2e_isolation.py` |
| **FR-004** | Vector Embedding & RAG | `learning-service/app/services/gemini_client.py` | `PracticeTestsTab.tsx` | `learning_document_chunks` | `test_phase4_e2e_isolation.py` |
| **FR-005** | Bloom's Assessment Generator | `learning-service/app/services/mcq_generator.py` | `PracticeTestsTab.tsx` | `assessments`, `questions` | `test_phase4_e2e_isolation.py` |
| **FR-006** | LaTeX Mathematical Proofs | `learning-service/app/services/mcq_generator.py` | `KaTeXViewer.tsx`, `TestRunner.tsx` | `questions.latex_proof` | `AssessmentDeadline.test.tsx` |
| **FR-007** | Diagnostic Auto-Grading | `learning-service/app/services/self_learning_service.py` | `TestReviewScreen.tsx` | `assessment_attempts` | `test_phase4_e2e_isolation.py` |
| **FR-008** | Mastery Radar Profiler | `learning-service/app/services/self_learning_service.py` | `TopicMasteryRadarChart.tsx` | `topic_mastery_profiles` | `test_phase4_e2e_isolation.py` |
| **FR-009** | Weakness Test Regeneration | `learning-service/app/services/self_learning_service.py` | `MasteryAnalyticsTab.tsx` | `assessments.generation_mode` | `test_phase4_e2e_isolation.py` |
| **FR-010** | Universal Campus Gateway | `api/index.py` (Gateway Router) | `pages/CampusExplorerPage.tsx` | Gateway Registry Objects | `CampusExplorerPage.test.tsx` |
| **FR-011** | Timetable & .ics Sync | `scheduling-service/app/services/timetable.py` | `components/timetable/TimetableHub.tsx` | `timetable_slots`, `classrooms` | `timetable-engine.test.ts` |
| **FR-012** | Dynamic Space Finder | `facility-service/app/services/facilities.py` | `DynamicSpaceFinder.tsx` | `rooms`, `room_reservations` | `space-finder.test.ts` |
| **FR-013** | Smart Transit Telemetry | `facility-service/app/services/transit.py` | `SmartTransitFleetTelemetry.tsx` | `transit_routes`, `route_stops` | `transit-telemetry.test.ts` |
| **FR-014** | Double-Entry Finance & GL | `finance-service/app/services/ledger.py` | `pages/student/StudentFinancePage.tsx` | `invoices`, `journal_entries` | `test_finance_ledger.py` |
| **FR-015** | Cryptographic Audit Log | `platform-service/app/services/audit.py` | `pages/admin/AdminPlatformPage.tsx` | `security_audit_logs` | `test_audit_security.py` |
| **NFR-001** | Performance & Latency | Unified Serverless Gateway (`api/index.py`) | Production Vite SPA | All 12 Database Schemas | Automated Benchmark Suite |
| **NFR-003** | Argon2id & RS256 Tokens | `identity-service/app/security/jwt.py` | `features/auth/AuthContext.tsx` | `users.password_hash` | `test_security.py` |
| **NFR-004** | Multi-Tenant Data Isolation | All Services (Foreign Key Scoping) | Route Guards (`ProtectedRoute.tsx`) | `student_id` Scoped Columns | `test_phase4_e2e_isolation.py` |
| **NFR-006** | Grounded AI Assertion | `learning-service/app/services/mcq_generator.py` | `TestReviewScreen.tsx` | Pydantic Output Gatekeeper | Unit & Contract Test Suite |

---

# Appendix C: Environment Configuration

#### Table C.1: Runtime Platform Environment Configuration Variables

| Environment Variable | Default Value | Secret | Architectural Purpose |
| :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | `development` | No | Specifies runtime environment (`development`, `staging`, `production`) |
| `DATABASE_URL` | `postgresql+psycopg://...` | Yes | Neon PostgreSQL connection string with PgBouncer connection pooling |
| `POSTGRES_URL` | None | Yes | Cloud provider database connection URL fallback |
| `JWT_PRIVATE_KEY_PEM` | In-Process RSA 2048-bit Key | Yes | RSA private key used by Identity Service to sign client access tokens |
| `JWT_KEY_ID` | `identity-dev-1` | No | Key identifier embedded in JWT headers (`kid`) for JWKS lookup |
| `JWT_ISSUER` | `http://localhost:8001` | No | Expected JWT issuer claim (`iss`) |
| `INTERNAL_SERVICE_PRIVATE_KEY_PEM` | In-Process Ed25519 Key | Yes | Asymmetric Ed25519 private key for inter-service cryptographic token minting |
| `INTERNAL_SERVICE_KEY_ID` | `internal-service-key-1`| No | Key identifier for internal microservice communication headers |
| `GEMINI_API_KEY` | None | Yes | Google Gemini API key powering LLM generation and vector embeddings |
| `GEMINI_MODEL` | `gemini-2.0-flash` | No | Target Large Language Model identifier |
| `GEMINI_EMBEDDING_MODEL` | `text-embedding-004` | No | Target vector embedding model identifier (768 dimensions) |
| `REDIS_URL` | `redis://localhost:56380/0` | Yes | Redis connection string for distributed rate limiting and idempotency |
| `RABBITMQ_URL` | `amqp://guest:guest@localhost:55672/` | Yes | AMQP connection string for asynchronous domain event bus |
| `MINIO_ENDPOINT` | `localhost:59000` | No | Private S3 educational object storage endpoint |
| `MINIO_ACCESS_KEY` | `minioadmin` | Yes | S3 storage access key |
| `MINIO_SECRET_KEY` | `minioadmin` | Yes | S3 storage secret key |
| `SECURITY_TOKEN_PEPPER` | `smartedu-serverless-pepper` | Yes | Cryptographic salt pepper for sensitive token hashing |
| `VITE_API_GATEWAY_URL` | `http://localhost:18080` | No | Public HTTPS URL of deployed API Gateway consumed by Vite frontend |
| `CORS_ORIGINS` | `["*"]` | No | Allowed CORS origin regex array for web client cross-origin calls |
