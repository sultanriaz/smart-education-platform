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

### 4.2 Learning Materials & Notes
- Access course syllabi, lecture notes, and downloadable supplementary files uploaded by faculty (`/app/student/learning`).

### 4.3 Online Assessments & Quizzes
Navigate to **Assessments** (`/app/student/assessments`):
1. View active, upcoming, and completed quizzes.
2. Click **Start Attempt** to begin a quiz.
3. Answer questions before the on-screen countdown timer expires.
4. Click **Submit** to finalize the attempt.
5. Review your score and question feedback once results are published.

### 4.4 Student Fee Portal & Online Payments
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

## 5. Security & Privacy Safeguards

- **Multi-Tenant Account Isolation**: Students and teachers can never access other users' private financial, academic, or payroll records.
- **Strict Role Boundaries**: Accessing an administrative or teacher URL with a student account immediately triggers a `403 Forbidden` response.
- **No Real Money Transfers**: In development and sandbox modes, all payment gateways and payroll disbursements are entirely simulated. No real credit card or bank account will be charged.

