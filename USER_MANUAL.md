# SmartEdu Platform — Comprehensive User Manual
## Step-by-Step Functional Guide for Administrators, Faculty, and Students

---

## 1. Getting Started & Logging In

The Smart Education Platform provides a unified web portal accessible at **[http://localhost:5173](http://localhost:5173)**. Access is secured using role-based permissions and JSON Web Tokens stored securely in browser memory, with rotating HttpOnly refresh cookies.

### Seeded Demo Accounts

| Role | Email Address | Password | Primary Workspace Route |
| :--- | :--- | :--- | :--- |
| **Institutional Admin** | `admin@demo.example.edu` | `Demo!UCxagNDHeToFSZXHcdxlRiie7aZ` | `/app/admin` |
| **Faculty / Teacher** | `teacher@demo.example.edu` | `Q7!Oa8xZ24L2aX0dEnj8TuSWGEoDgN-vY8KxEVrnts6cbAaZ` | `/app/teacher` |
| **Student** | `student@demo.example.edu` | `Q7!vEpzlshyGXIddiaOLN7GT73b1cUc71pLVJ1ybXGm5dUaZ` | `/app/student` |

---

## 2. Institutional Administrator Guide

The Administrator workspace (`/app/admin`) provides full oversight of academic catalog lifecycle, institutional finance, human resources payroll, system governance, and audit trails.

### 2.1 Academic Catalog Management
- **Departments & Programs**: Define departments (e.g., Computer Science, Electrical Engineering) and assign multi-semester degree programs.
- **Courses & Sections**: Create courses with credit hour definitions, syllabi, prerequisites, and configure active semester sections.
- **Student Enrollment**: Assign students to sections; enrollment automatically emits `academic.enrollment.created.v1` events to provision student fee accounts.

### 2.2 Institutional Finance & Fee Management
Navigate to **Finance** in the Admin sidebar (`/app/admin/finance`):
1. **Fee Structures**: Configure versioned fee structures by academic program and admission batch with individual line item components (Tuition Fee, Lab Charges, Library Fund, Exam Fees).
2. **Scholarships & Concessions**: Define institutional concessions (e.g., Merit Scholarships, Need-Based Aid). Set percentage discounts (e.g., 25% Merit Discount) that automatically apply to eligible invoices.
3. **Invoice Generation & Installments**: Invoices can be generated as a lump sum or split into multi-part installment plans with independent due dates.
4. **Overdue Fee Processing**: Configure the overdue policy (Default: **10-day grace period** and **flat PKR 500.00 late fee penalty**). The automated background scheduler applies penalties idempotently without duplicate charges.
5. **General Ledger (GL) & Trial Balance**:
   - Inspect the standard Chart of Accounts (Cash, Accounts Receivable, Tuition Revenue, Concession Expense, Deferred Revenue).
   - Review immutable double-entry journal postings.
   - Verify that the Trial Balance satisfies the accounting invariant:
     $$\sum \text{Debits} = \sum \text{Credits}$$
6. **Refund Management & Maker-Checker Dual Control**:
   - Review student refund requests.
   - **Dual Control Enforcement**: A user who created a refund request cannot approve it. A separate administrator/checker must approve or reject the refund to prevent financial misappropriation.

### 2.3 Institutional Payroll & HR
Navigate to **Payroll** in the Admin sidebar (`/app/admin/payroll`):
1. **Employee Profiles**: Review faculty and staff payroll profiles with designations, base salaries, and designated disbursement bank details (e.g., Meezan Bank). Note: Ordinary student identities are strictly blocked from payroll profile provisioning.
2. **Monthly Payroll Runs**:
   - Create a payroll run for an active monthly period.
   - The Gross-to-Net Calculation Engine automatically calculates base salary, allowances (Medical, Housing), and statutory deductions (Income Tax, Provident Fund).
3. **Maker-Checker Run Approval**:
   - The creator of the payroll run cannot approve the run.
   - A distinct authorized officer reviews the gross-to-net summary and approves the run for disbursement.
4. **Simulated Payouts, Failure Handling & Retries**:
   - Execute batch disbursements to the simulated 1Link banking network.
   - If a disbursement encounters an simulated communication failure or returns `UNCERTAIN`:
     - The transaction is locked against accidental immediate double-retry.
     - The administrator runs **Batch Reconciliation** to confirm the final banking outcome.
     - Individual failed disbursements can be retried cleanly.

### 2.4 Governance, Audit Trails & Platform Operations
Navigate to **Platform & Governance** (`/app/admin/platform`):
- **Security Audit Logs**: Search auditable user activities with actor IDs, source services, IP addresses, and request correlation IDs. Tokens and sensitive passwords are automatically redacted.
- **Versioned Feature Flags**: Toggle platform features with percentage-based deterministic rollout to subsets of users.
- **Data Operations & CSV Imports**: Perform bulk user or catalog imports with validation-only dry-run verification and atomic transactional rollbacks.

---

## 3. Faculty / Teacher Guide

The Teacher workspace (`/app/teacher`) provides classroom management, student assessment, attendance tracking, and personal compensation tools.

### 3.1 Class Timetable & Schedule
- View your weekly teaching timetable (`/app/teacher/timetable`) with room allocations, course codes, and scheduled class hours.

### 3.2 Attendance Marking
Navigate to **Attendance** (`/app/teacher/attendance`):
1. Select your active course section and date.
2. Open the attendance session.
3. Rapidly mark student records as `PRESENT`, `ABSENT`, or `EXCUSED` using the bulk-mark interface.
4. Finalize the session to lock records against accidental modification.

### 3.3 Assessment Creation & Grading
Navigate to **Assessments** (`/app/teacher/assessments`):
1. **Create Quizzes**: Define quiz titles, instructions, total points, and active time limits.
2. **Question Banks**: Add multiple-choice and short-answer questions with randomized choices.
3. **Automated Grading**: Multiple-choice submissions are automatically graded upon submission.
4. **Timer Expiration**: Assessments configured with a countdown timer are finalized automatically by background workers when the allotted time expires, even if the student disconnects.
5. **Grade Review**: Review class score distributions and apply manual grade adjustments if required.

### 3.4 Personal Compensation & Payslips
Navigate to **Payroll** (`/app/teacher/payroll`):
- View your monthly salary slips with clear breakdowns of Gross Earnings, Allowances, Deductions, and Net Take-Home Pay.
- Download PDF/printable copies of approved payslips.
- Payslip data is isolated: teachers can only access their own payroll records.

---

## 4. Student Guide

The Student workspace (`/app/student`) empowers students to manage their academic journey, track attendance, take quizzes, and manage fee payments.

### 4.1 Academic Dashboard & Schedule
- View your enrolled courses, current semester GPA progress, and upcoming classes on the interactive weekly calendar (`/app/student/timetable`).

### 4.2 AI-Powered Self-Directed Learning Hub & Subject Management
Navigate to **Learning** in the Student sidebar (`/app/student/learning`):
- **Subject Workspace & Switcher**:
  - Switch dynamically between custom enrolled subjects using the header dropdown.
  - Create new subjects across academic departments (Computer Science, Software Engineering, Law, Health Sciences, Mathematics, Business, etc.) via the **+ Add Subject** modal.
  - Customize each subject with dedicated color palettes and visual badge icons for rapid identification.

### 4.3 Study Material Library, Ingestion & 100MB Storage Quota
Under the **Study Materials** tab:
1. **Multi-Format Ingestion**: Drag-and-drop course slides, notes, or textbooks in `.pdf`, `.docx`, `.pptx`, and `.txt` formats.
2. **SHA-256 Deduplication & Security**: Files are validated by MIME type and cryptographically deduplicated to prevent wasted storage.
3. **Automated Topic & Syllabus Discovery**: Google Gemini automatically scans newly ingested files, discovering chapter units and topic tags.
4. **Storage Quota Meter**: A live progress gauge monitors student storage usage against the **100MB per-student quota**.
5. **Document Inventory**: View file sizes, upload timestamps, extracted topics, and remove outdated materials with 1-click deletion.

### 4.4 LangGraph & Gemini MCQ Assessment Engine
Under the **Practice Tests** tab:
1. **Customized Assessment Generation**: Click **Generate New Assessment** to configure:
   - **Question Count**: 5 to 30 questions.
   - **Bloom's Taxonomy Calibration**:
     - *Basic*: Factual recall and foundational definitions.
     - *Medium*: Applied conceptual scenarios and standard problem-solving.
     - *Hard*: Analytical synthesis, edge cases, and multi-step reasoning.
     - *Mixed*: Balanced distribution across all cognitive tiers.
   - **Topic Targeting**: Select specific extracted topics or leave empty to assess the entire course syllabus.
2. **Interactive Test Runner**:
   - Live countdown timer automatically calibrated to test length.
   - Question navigator grid allowing students to jump between questions and track answered status.
   - Submission confirmation dialog to prevent accidental early submission.

### 4.5 Real-Time Diagnostic Evaluation, LaTeX Solutions & Feedback
Upon test completion or review:
1. **Instant Grading**: Immediate score calculation, overall percentage, and pass/fail determination.
2. **Pedagogical Rationale**: Detailed "Why is this correct?" rationale citing the specific source document concepts.
3. **Collapsible "View Solution" for Quantitative Questions**:
   - Step-by-step arithmetic and algebraic proofs rendered with KaTeX.
   - Exact mathematical formulas rendered dynamically:
     $$A = \text{softmax}\left(\frac{QK^T}{\sqrt{d_k}}\right)V$$
4. **Question Diffs**: Color-coded cards contrasting the student's selected choice with the correct answer.

### 4.6 Topic Mastery Profiler & 1-Click Smart Remediation
Under the **Mastery & Analytics** tab and Review Screen:
1. **Cognitive Tier Classification**:
   - **Strong Topics** ($\ge 75\%$ accuracy): Mastery consolidated.
   - **Moderate Topics** ($50\text{--}74\%$ accuracy): Recommended for light review.
   - **Weak Topics** ($< 50\%$ accuracy): Flagged as high-priority remediation targets.
2. **Historical Score Progression**: Visual bar chart tracking scores across all completed practice tests.
3. **1-Click Smart Test Regeneration**:
   - Automatically analyzes past performance and drafts a fresh test heavily weighted on weak areas (**70% weak focus / 30% reinforcement**).
   - Alternatively choose **Balanced** or **Challenge** modes.

### 4.7 Institutional Course Resources & Activity Log
Under the **Institutional Resources** tab:
- Access instructor-published slides, recommended resources based on curriculum section, and view historical download activity.

### 4.8 Online Assessments & Quizzes
Navigate to **Assessments** (`/app/student/assessments`):
1. View active, upcoming, and completed formal university examinations and quizzes.
2. Click **Start Attempt** to begin an official timed exam.
3. Submissions are synchronized with instructor gradebooks.

### 4.9 Student Fee Portal & Online Payments
Navigate to **Finance** (`/app/student/finance`):
1. **Invoice Overview**: Inspect current semester tuition fees, due dates, and installment schedules.
2. **Concessions & Discounts**: View applied merit scholarships or financial aid deductions.
3. **Payment Checkout**:
   - Click **Pay Now** on an unpaid invoice or installment.
   - In the payment modal, select your preferred payment method:
     - **JazzCash Mobile Wallet**
     - **EasyPaisa Mobile Wallet**
     - **Online Bank Transfer / 1Link**
   - Click **Confirm Payment**.
   - The platform completes a simulated settlement callback and generates an official electronic payment receipt.
   - The invoice status updates immediately to `PAID`, and the outstanding student balance drops to zero.

---

## 5. Universal Campus Gateway & Client Modules Guide

The platform integrates 8 dedicated operational modules accessible both from the public gateway (`/` or `/explore`) and from protected role-specific workspaces.

### 5.1 Module 1: Main Dashboard (Universal Campus Gateway)
- **Accessible at**: `/` and `/explore`
- **8 Core Action Cards**:
  1. **Student Portal**: Direct sign-in for students (`/login/student`) with department and registration number validation.
  2. **Free Slots**: Live discovery of empty classrooms for study sessions.
  3. **Timetable**: Master section and teacher timetable engine.
  4. **Campus Hub**: Centralized university directory across 6 campus divisions.
  5. **Transport Service**: City bus networks and intra-campus shuttle telemetries.
  6. **Faculty**: Dedicated faculty portal sign-in (`/login/faculty`).
  7. **Sports Week**: Tournament brackets, fixtures, and department standings.
  8. **Self Assessment**: Autonomous AI diagnostic assessment engine.

### 5.2 Module 2: Student Academic Cockpit & Course Command Centers
- **Accessible at**: `/app/student` and `/app/student/courses/:courseId`
- **Regulatory Attendance Guard**: Alerts when attendance dips below the mandatory 75% HEC threshold with calculation of required consecutive lectures.
- **8 Subject Detail Sub-Cards**:
  1. *Assignments*: View pending tasks with file upload dropbox.
  2. *Quizzes*: Multiple-choice and timed quizzes.
  3. *Attendance*: Class-by-class attendance ledger and leave excuse submission.
  4. *Marks*: Weightage breakdowns and aggregate GPA projections.
  5. *Notifications*: Course announcements and notices from instructors.
  6. *Resources*: Syllabus, lecture slides, and supplementary reading files.
  7. *Lecture Hub*: Recorded lecture videos with playback controls.
  8. *Course Information*: Instructor details, office hours, and course outlines.

### 5.3 Module 3: Intelligent Timetable & Schedule Engine
- **Accessible at**: `/app/student/timetable`, `/app/teacher/timetable`, and Gateway Tab
- **Student View**: Filter by section (e.g. `BCS-7C`, `BCS-7A`, `BSE-5A`) with daily lecture count summaries and enrolled student capacities.
- **Teacher View**: Filter by faculty member (e.g. `Sir Munir (Dr. Munir Ahmad)`) with assigned slots and halls.
- **1-Click Sync**: Export schedule to `.ics` for Google Calendar, Apple Calendar, and Outlook.

### 5.4 Module 4: Dynamic Space Finder & Free Slot Navigator
- **Accessible at**: `/app/student/facilities` and Gateway Tab
- **Available Right Now**: 1-click filter for instantly free rooms.
- **Block-Wise Navigation**: Block A, Block B, Block C, Block D, and Engineering Labs.
- **Room Telemetry**: Seating capacity, projector, Wi-Fi, power sockets, and "Free Until" indicators.
- **Weekly Matrix**: Comprehensive day and slot grid of all available study spaces.

### 5.5 Module 5: Smart Transit & Fleet Telemetry
- **Accessible at**: `/app/student/transit` and Gateway Tab
- **City Route Networks**: Inbound and outbound routes (e.g., *Farid Town Point*, *Mall Road Express*, *Canal Line*).
- **Stop-by-Stop Itineraries**: Scheduled times vs estimated actual arrivals (ETAs), bus numbers, driver contacts, and occupancy status.
- **Disruption Bulletins**: Live alerts for route diversions, maintenance, or weather delays.

### 5.6 Module 6: Campus Hub, Directory & Spatial Wayfinding
- **Accessible at**: `/app/student/hub` and Gateway Tab
- **6 Specialized Directories**:
  1. *Faculty & Teachers Directory*: Search by department, title, office hours, and consultation booking.
  2. *Office Directory*: Registrar, Accounts, Examination, Career Placement, and Medical Center with working hours and live queue token trackers.
  3. *Lab Directory*: Specialized hardware, robotics, and computer labs with equipment inventories.
  4. *Classrooms*: Lecture halls categorized by floor and block with seating capacity.
  5. *Library Intelligence*: Live seat availability, catalog search, and borrowing limits.
  6. *Campus Statistics*: High-level summary of campus assets.
- **Interactive Floor Blueprints**: Visual vector room maps highlighting selected rooms.

### 5.7 Module 7: Campus Life, Marquee Events & Sports Gala Portal
- **Accessible at**: `/app/student/events` and Gateway Tab
- **Calendar-Aware Morphing**: Sports Gala (Spring), Tech Hackathon (Fall), Career Fair (Winter).
- **Tournament Engine**: Live fixtures grouped by day with day selector pills, knockout elimination brackets, and department points table.

### 5.8 Module 8: AI Self-Learning & Adaptive Assessment Studio
- **Accessible at**: `/app/student/learning` and Gateway Card
- **Bloom's Taxonomy Generator**: Configurable question difficulty, counts, and topic filters.
- **KaTeX Step-by-Step Proofs**: High-resolution mathematical formula derivations.
- **Topic Mastery Radar Chart**: Visual SVG radar diagram classifying topics into Strong ($\ge 75\%$), Moderate ($50\text{--}74\%$), and Weak ($<50\%$).
- **Smart Test Regeneration**: Automatic weakness remediation targeting identified knowledge gaps.

---

## 6. Security & Privacy Safeguards

- **Multi-Tenant Account Isolation**: Students and teachers can never access other users' private financial, academic, or payroll records.
- **Strict Role Boundaries**: Accessing an administrative or teacher URL with a student account immediately triggers a `403 Forbidden` response.
- **No Real Money Transfers**: In development and sandbox modes, all payment gateways and payroll disbursements are entirely simulated. No real credit card or bank account will be charged.

