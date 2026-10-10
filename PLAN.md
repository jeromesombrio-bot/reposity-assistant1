# Sprint Plan - Bayanihan College Enrollment Assistant

## User Stories
1. **Incoming Freshman**: As an incoming freshman student, I want to ask about the exact enrollment document requirements so that I can prepare all papers before visiting campus.
   - *Acceptance Criteria 1*: System lists specific required documents (e.g., Form 138, Good Moral, Birth Certificate).
   - *Acceptance Criteria 2*: System references the matching FAQ ID source under the response.
2. **Parent**: As a parent, I want to know if tuition can be paid in installments and what payment channels are accepted so that I can manage our budget.
   - *Acceptance Criteria 1*: System clearly explains the installment terms (downpayment, prelims, midterms, finals).
   - *Acceptance Criteria 2*: System lists accepted channels (Cashier, GCash, Maya, Landbank).
3. **Registrar Staff**: As a registrar staff member, I want an admin stats page to view question volume per category and user feedback ratings so that I can identify common student issues.
   - *Acceptance Criteria 1*: `/admin` updates in real-time with category counts and thumbs-up percentage.
   - *Acceptance Criteria 2*: Invalid or off-topic queries are logged without crashing the metrics.

## Task Backlog

| Task | Status |
| :--- | :--- |
| Set up GitHub Repository and Codespaces | Done |
| Define 15 realistic FAQ entries in `faq.json` | Done |
| Build POST `/api/chat` grounded RAG endpoint | Done |
| Create 50 intent questions and train ML model in `train.py` | Done |
| Build mobile UI (`/`) with loading state and feedback buttons | Done |
| Build admin stats dashboard (`/admin`) and GET `/api/stats` | Done |
| Perform safety & guardrail tests in `EVAL.md` | Done |
| Deploy app to Render and verify live URL | Done |
| Complete reflection in `REFLECTION.md` | Done |