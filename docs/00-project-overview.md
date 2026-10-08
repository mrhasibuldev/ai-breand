# NexusAI — Personal AI Health & Wellness Companion

**Product name:** NexusAI  
**Current product:** NexusAI Personal AI Health & Wellness Companion  
**Document type:** Canonical Project Overview / Phase 01 — Vision & Mission  
**Status:** Canonical direction confirmed; Phases 04–12 APPROVED; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS.  
**Last updated:** 2026-09-07

## 1. SOURCE OF TRUTH

**Canonical product identity:** `NexusAI — Personal AI Health & Wellness Companion`  
**Current product requirement:** A web-first Health & Wellness Companion MVP; the broader Personal AI Companion vision is future direction, not an expanded V1 scope.

এই project-এ product direction, architecture এবং implementation-এর জন্য নিচের document hierarchy অনুসরণ করতে হবে:

1. **Current approved Product Vision** — এই document
2. **Product Discovery** — `01-product-discovery.md`
3. **PRD** — `02-prd-nexus-ai-health-companion-mvp.md`
4. **System Architecture** — `03-system-architecture-outline.md`
5. **Architecture Review** — `04-architecture-review.md`
6. **Approved Database Design** — Phase 05 documents
7. **Approved Database Implementation Design** — Phase 06 documents
8. **Approved API Design** — Phase 07 documents
9. **Approved AI/Memory/Safety Architecture** — Phase 08 documents
10. **Approved UI/UX Architecture** — Phase 09 documents
11. **Approved Security/Privacy Architecture** — Phase 10 documents
12. **Approved Implementation Architecture** — Phase 11 documents
13. **Approved Implementation Foundation** — Phase 12 documents
14. **Current implementation gate** — `13-core-implementation-part1.md`

Phase 04 authorized only Phase 05 at that gate. Subsequent approvals are recorded in the Phase 05–12 approval records, including `12-implementation-foundation-final-review.md`, which records Phase 12 approval and explicit Phase 13 authorization. Current status is Phases 04–12 APPROVED, Phase 13 Part 1 APPROVED, and Phase 13 Part 2 AUTHORIZED / IN PROGRESS.

When documents conflict, the higher document in this hierarchy wins. A lower-level document must record the conflict and request an update; it must not silently invent a new product direction.

## 2. Vision

NexusAI-এর long-term vision হলো একটি বিশ্বস্ত Personal AI Companion তৈরি করা—যে user-এর explicit permission নিয়ে ধীরে ধীরে শিখবে, দরকারি personal context মনে রাখবে, privacy সম্মান করবে, daily life-এ সাহায্য করবে এবং সময়ের সঙ্গে একটি broader Personal AI Life Operating System-এর দিকে evolve করতে পারবে।

এই vision-এর foundation হবে:

- user control এবং explicit consent;
- gradual, transparent learning;
- minimal and useful memory;
- safe and honest AI behavior;
- privacy এবং security by design;
- explainable personalization;
- human dignity, autonomy এবং non-judgmental interaction।

## 3. Mission

আজকের MVP-র mission হলো একটি web-first Health & Wellness Companion দিয়ে users-কে স্বাস্থ্যকর habit, routine, reminder, check-in এবং progress tracking-এ বাস্তব সাহায্য করা—diagnosis বা treatment-এর দাবি না করে, এবং user-এর data/memory-এর ওপর পূর্ণ নিয়ন্ত্রণ বজায় রেখে।

## 4. Current MVP definition

**MVP:** Web-first Personal AI Health & Wellness Companion.

### MVP experience

- Guest/basic experience, যেখানে account বাধ্যতামূলক নয়।
- Account-based personalized experience।
- Secure registration, consent এবং onboarding।
- Name এবং age সংগ্রহ (প্রয়োজনীয় policy/age decision pending)।
- Optional profile/photo information।
- Wellness/health goals।
- Basic health and lifestyle information, only when necessary and consented।
- AI conversation for in-scope wellness support।
- Personalized wellness guidance।
- Daily wellness planning।
- Reminders এবং check-ins।
- Progress tracking।
- Consent-based minimal memory।
- Secure account এবং data-management controls।

## 5. Safety boundary

NexusAI V1 একটি wellness companion, doctor নয়। এটি:

- disease diagnosis দাবি করবে না;
- physician বা licensed professional-এর replacement হিসেবে নিজেকে উপস্থাপন করবে না;
- medication prescribe, dosage change, বা treatment plan দেবে না;
- emergency medical treatment বা emergency response হিসেবে কাজ করবে না;
- high-risk/emergency context-এ reviewed safety guidance এবং appropriate escalation messaging দেবে।

Persistent product copy এবং AI response policy-তে এই boundary দৃশ্যমান থাকতে হবে।

## 6. Minimal Memory in MVP

MVP-তে **Minimal Memory** ব্যবহার হবে। User-এর explicit consent ছাড়া memory তৈরি বা retrieval হবে না। অনুমোদিত memory category হতে পারে:

- name;
- age;
- wellness goals;
- preferences;
- relevant daily habits;
- previous plans;
- progress/check-in information।

প্রতিটি memory item user দেখতে, edit করতে, delete করতে এবং future memory বন্ধ করতে পারবে। Architecture-কে ভবিষ্যতের **Smart Personal Memory** এবং শেষ পর্যন্ত **Full Life Memory**-এর দিকে expand করার সুযোগ রাখতে হবে, কিন্তু MVP-তে সেই scope সক্রিয় করা যাবে না।

## 7. Platform boundary

### In scope now

- Responsive web application।
- Browser-based guest এবং account experience।

### Future, not MVP requirements

- Native mobile apps।
- Wearables এবং passive health sensors।
- Voice-first interaction।
- Robotics।
- Education, work assistant, media/creator systems।
- Broader Life OS capabilities।

## 8. AI direction

Long term, NexusAI নিজের AI/AI-brain technology গড়ে তুলতে চায়। MVP-তে proprietary foundation model ইতিমধ্যে আছে—এমন দাবি করা যাবে না।

তাই system-এর AI provider/model abstraction এমন হবে যাতে:

1. MVP experimentation-এর জন্য interchangeable provider ব্যবহার করা যায়;
2. ভবিষ্যতে proprietary NexusAI model provider বদল হিসেবে যুক্ত করা যায়;
3. business logic, safety policy, user data, memory এবং wellness workflow model provider থেকে স্বাধীন থাকে;
4. provider বদলালেও user-facing product contract অযথা ভেঙে না যায়।

## 9. Primary users

- **Wellness Builder:** এক থেকে তিনটি everyday habit তৈরি করতে চায়।
- **Routine Manager:** reminder, schedule এবং check-in-এর কাঠামো চায়।
- **Guest evaluator:** account খোলার আগে সীমিত experience পরীক্ষা করে।
- **Authorized support/admin:** সীমিত, audited operational support দেয়; private chat/memory default-এ দেখে না।

## 10. Product principles

1. Wellness, not diagnosis.
2. Consent before memory.
3. Data minimization.
4. User control and reversibility.
5. Transparent personalization.
6. Safe uncertainty and professional escalation.
7. Gentle, non-judgmental engagement.
8. Security and privacy by design.
9. Provider/model independence.
10. Documentation-first, approval-gated delivery.

## 11. Explicit non-goals for V1

- Clinical diagnosis, treatment, triage, or disease prediction।
- Emergency response বা crisis service।
- Medication prescribing/dosage management।
- Continuous passive sensing।
- Unrestricted autonomous external actions।
- Social/community features, clinician portal, insurance workflow, বা employer surveillance।
- Native mobile, voice-first, robotics, বা broader Life OS features।
- Private user data দিয়ে model training, unless a separate explicit consent and approved policy exists।

## 12. Current phase and working rule

**Current status:** Phases 04–12 APPROVED; Phase 13 Part 1 APPROVED; Phase 13 Part 2 AUTHORIZED / IN PROGRESS. Part 2 is limited to the authenticated, development-only Goals vertical slice. Later phases, production persistence, providers, public beta, and production deployment are not authorized by this status.

**HISTORICAL SNAPSHOT — NOT CURRENT PROJECT STATUS**

Phase 04 remains `APPROVED` under the explicit user approval dated 2026-09-07. Phase 05–11 approval records and the Phase 12 final review establish the subsequent approved history. Phase 12 is `APPROVED`, and Phase 13 Part 1 was explicitly authorized as a narrow implementation slice. The initial review found no BLOCKER and seven HIGH findings; the final re-review retained HIGH #1, #2 and #4. The authorized final remediation batch addresses those findings, with closure pending re-review. Phases 04–12 APPROVED; Phase 13 AUTHORIZED / IN PROGRESS; Phase 13 Part 1 BLOCKED — HIGH REMEDIATION / RE-REVIEW; Phase 13 Part 2 NOT AUTHORIZED / NOT STARTED. এই অবস্থায়:

- কেবল explicitly authorized remediation batch-এর কাজ করা যাবে;
- Phase 13 Part 1 review pass না করা পর্যন্ত phase-টি approved নয়;
- Phase 13 Part 2 শুরু করা যাবে না;
- কোনো real PostgreSQL, production authentication/AI provider, production infrastructure বা unrelated feature যোগ করা যাবে না;
- unresolved legal, privacy, safety, business এবং infrastructure decisions `TBD / Pending Decision` থাকবে।

প্রতিটি phase শেষে summary, risks, open decisions এবং user approval record করতে হবে।

## 13. Historical traceability

আগের একটি draft-এ NexusAI-কে source-grounded operations copilot হিসেবে প্রস্তাব করা হয়েছিল। সেটি বর্তমান product requirement নয় এবং **SUPERSEDED / HISTORICAL — NOT CURRENT PRODUCT REQUIREMENT** হিসেবে গণ্য হবে। বর্তমান canonical product কেবল Personal AI Health & Wellness Companion MVP।
