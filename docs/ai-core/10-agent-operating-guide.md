# Agent Operating Guide

**Last Updated**: 2026-10-26  
**Purpose**: Mandatory instructions for future AI coding agents working on NexusAI AI Core

---

## MANDATORY PRE-WORK

### Step 1: Read Documentation Index

**MANDATORY**: Before investigating or changing the AI Core, you MUST read:

**File**: `docs/ai-core/README.md`

**Purpose**: Understand the AI Core documentation structure and current status.

**Verification**: Confirm you have read the documentation index before proceeding.

---

### Step 2: Review Known Issues

**MANDATORY**: Review the issue register to understand existing problems.

**File**: `docs/ai-core/07-known-issues.md`

**Purpose**: Understand which issues are already known, their severity, and authorization status.

**Action**: Check if your task relates to any existing issue IDs.

**Verification**: Note any relevant issue IDs in your work.

---

### Step 3: Review Audit History

**MANDATORY**: Review previous audits to avoid repeating work.

**File**: `docs/ai-core/08-audit-history.md`

**Purpose**: Understand what has already been investigated and verified.

**Action**: Check if your task has been completed before.

**Verification**: Do not repeat work that has already been done.

---

## MANDATORY RULES

### Rule 1: Inspect Actual Code

**MANDATORY**: Do NOT trust historical reports without verification.

**Action**: 
- Inspect actual source code before making changes
- Verify file paths exist before referencing them
- Verify function signatures before calling them
- Verify configuration before relying on it

**Rationale**: Previous audits may be outdated or incorrect (e.g., previous audits claimed "no AI implementation exists" which was incorrect).

---

### Rule 2: Distinguish Evidence Types

**MANDATORY**: Always distinguish between verification types.

**Evidence Types**:
- **VERIFIED**: Runtime-tested or direct file inspection confirmed
- **SOURCE-INSPECTED**: Code inspected but not runtime tested
- **UNKNOWN**: No evidence available
- **ESTIMATED**: Calculated but not measured
- **SUSPECTED**: Hypothesized but not proven

**Action**: Always mark findings with the appropriate evidence type.

---

### Rule 3: Investigate Before Fixing

**MANDATORY**: Investigate the root cause before implementing fixes.

**Action**:
- Trace the problem through the code
- Identify the actual cause
- Understand dependencies
- Consider side effects

**Rationale**: Blind fixes may break other things or not address the root cause.

---

### Rule 4: Request Authorization

**MANDATORY**: Request authorization before making changes outside the current scope.

**Action**:
- If a task is not in the authorized scope, ask for authorization
- Clearly explain what you want to do and why
- Wait for explicit approval before proceeding

**Current Authorization**: DOCUMENTATION ONLY (no code changes authorized)

---

### Rule 5: Never Train Without Authorization

**MANDATORY**: Never train or fine-tune a model unless explicitly authorized.

**Prohibited Actions**:
- Running training scripts
- Fine-tuning existing models
- Generating new checkpoints
- Modifying training data without authorization

**Rationale**: Training is resource-intensive and may overwrite existing work.

---

### Rule 6: Never Modify Checkpoints

**MANDATORY**: Never create, overwrite, delete, or modify checkpoint files.

**Prohibited Actions**:
- Modifying `.pt` files
- Deleting checkpoint directories
- Regenerating checkpoints
- Modifying checkpoint metadata

**Rationale**: Checkpoints represent training effort and should be preserved.

---

### Rule 7: Never Modify Datasets Without Authorization

**MANDATORY**: Never modify training datasets unless explicitly authorized.

**Prohibited Actions**:
- Modifying `train_cleaned.json`
- Modifying `train_v2.json`
- Adding new dataset files
- Deleting dataset files
- Modifying dataset format

**Rationale**: Datasets are critical for model training and should be preserved.

---

### Rule 8: Never Modify Database Schemas

**MANDATORY**: Never modify database schemas or perform database writes without explicit authorization.

**Prohibited Actions**:
- Running migrations
- Modifying migration files
- Creating new tables
- Dropping tables
- Writing to database
- Modifying database records

**Rationale**: Database changes can break the application and cause data loss.

---

### Rule 9: Preserve User Changes

**MANDATORY**: Never modify, restore, stage, or delete pre-existing user changes.

**Known User Change**: `cookies.txt` is modified (pre-existing)

**Action**: 
- Always check Git status before making changes
- Preserve all pre-existing modifications
- Do not "clean up" unrelated files

**Rationale**: User changes must be preserved.

---

### Rule 10: Never Commit or Push Without Authorization

**MANDATORY**: Never commit, push, pull, reset, or stash Git changes unless explicitly authorized.

**Prohibited Actions**:
- `git commit`
- `git push`
- `git pull` (unless authorized)
- `git reset`
- `git stash`
- Modifying Git history

**Rationale**: Git operations should be controlled and intentional.

---

### Rule 11: Update Documentation

**MANDATORY**: After each authorized task, update the relevant documentation.

**Required Updates**:
- Update `08-audit-history.md` with new audit entry
- Update `07-known-issues.md` if issues are resolved or discovered
- Update relevant architecture documentation if changes were made
- Record exact files changed
- Record verification commands executed

**Action**: Documentation is part of task completion.

---

### Rule 12: Record Truthful Test Results

**MANDATORY**: Never claim tests passed unless they were actually run and results inspected.

**Action**:
- Only report test results you actually observed
- Include actual output or logs
- Mark tests as NOT TESTED if they were not executed
- Do not fabricate test results

**Rationale**: False test reports mislead future work.

---

## FORBIDDEN ACTIONS

### Absolutely Forbidden

These actions are NEVER authorized unless explicitly stated otherwise:

1. **Modifying application source code** (React, Next.js, TypeScript)
2. **Modifying Python model code** (neural/, tokenizer/, training/, inference/)
3. **Modifying training scripts** (train_medium_model.py, etc.)
4. **Modifying ML service code** (main.py, server.py) unless for documentation
5. **Modifying datasets** (data/*.json)
6. **Modifying tokenizer behavior** (tokenizer/tokenizer.py)
7. **Training or fine-tuning any model**
8. **Creating, overwriting, or deleting checkpoints**
9. **Modifying database schemas or records**
10. **Installing or removing dependencies** (package.json, requirements.txt)
11. **Changing environment variables or configuration**
12. **Running destructive commands** (rm -rf, etc.)
13. **Deleting existing documentation or user files**
14. **Committing or pushing to GitHub**
15. **Modifying unrelated files**

### Conditionally Forbidden

These actions may be authorized for specific tasks:

1. **Starting services** (ML service, backend) — Only for runtime verification
2. **Stopping services** — Only if you personally started them
3. **Reading files** — Always allowed
4. **Inspecting Git status** — Always allowed
5. **Creating documentation** — Always allowed (current task)
6. **Updating documentation** — Always allowed

---

## INVESTIGATION PROCESS

### Step 1: Define Scope

**Action**: Clearly define what you are investigating or changing.

**Verification**: Confirm the scope is within the authorized tasks.

---

### Step 2: Check Documentation

**Action**: Read relevant documentation files.

**Files to Check**:
- `docs/ai-core/README.md` (always)
- `docs/ai-core/07-known-issues.md` (if relevant)
- `docs/ai-core/08-audit-history.md` (if relevant)
- Specific architecture documentation (if relevant)

---

### Step 3: Inspect Code

**Action**: Inspect the actual source code related to your task.

**Verification**: Use file paths from documentation to find the correct files.

---

### Step 4: Verify Findings

**Action**: Verify your findings with actual code inspection or runtime testing.

**Evidence**: Always provide file paths, line numbers, or runtime output.

---

### Step 5: Document Findings

**Action**: Document your findings in the appropriate documentation file.

**Location**: 
- New findings: Update relevant documentation file
- New issues: Add to `07-known-issues.md`
- Completed audit: Add entry to `08-audit-history.md`

---

## VERIFICATION REQUIREMENTS

### Before Starting Work

1. Read `docs/ai-core/README.md`
2. Check Git status: `git status --short --branch`
3. Review `docs/ai-core/07-known-issues.md`
4. Review `docs/ai-core/08-audit-history.md`

### After Completing Work

1. Verify Git status: `git status --short --branch`
2. Confirm no unintended changes occurred
3. Update relevant documentation
4. Add entry to `08-audit-history.md` if you performed an audit
5. Update `07-known-issues.md` if you resolved or discovered issues

---

## GIT SAFETY

### Pre-Work Git Status

**MANDATORY**: Always check Git status before starting work.

**Command**:
```bash
git status --short --branch
```

**Expected Output**: Should show only pre-existing modifications (e.g., `M cookies.txt`)

**Action**: If unexpected changes exist, STOP and report them.

---

### Post-Work Git Status

**MANDATORY**: Always check Git status after completing work.

**Command**:
```bash
git status --short --branch
```

**Expected Output**: Should match pre-work status (no new changes)

**Action**: If changes occurred, report them and do not commit.

---

### Pre-Existing Modifications

**Known Modification**: `cookies.txt` is modified

**Action**: Do NOT stage, commit, or delete this file.

**Rationale**: This is a user change that must be preserved.

---

## ERROR HANDLING

### If You Encounter an Error

1. **Stop** the current action
2. **Investigate** the error cause
3. **Report** the error with context
4. **Do not** proceed without understanding the error

### If Git Status Shows Unexpected Changes

1. **Stop** all work
2. **Report** the unexpected changes
3. **Do not** attempt to fix without authorization
4. **Wait** for guidance

### If You Cannot Find a File

1. **Verify** the file path from documentation
2. **Search** for the file using find or grep
3. **Report** if the file does not exist
4. **Do not** create the file without authorization

---

## TASK TYPES

### Documentation Tasks

**Authorization**: ALWAYS AUTHORIZED

**Requirements**:
- Read existing documentation first
- Do not duplicate existing documentation
- Cross-reference related documents
- Update index if adding new documents
- Validate all links

**Git Status**: Should remain unchanged (no code changes)

---

### Investigation Tasks

**Authorization**: Typically AUTHORIZED for read-only investigation

**Requirements**:
- Read documentation first
- Inspect actual code
- Distinguish evidence types
- Document findings
- Do not make changes

**Git Status**: Should remain unchanged (read-only)

---

### Implementation Tasks

**Authorization**: NOT AUTHORIZED (current phase)

**Requirements**:
- Not applicable in current documentation-only phase

**Git Status**: N/A

---

## COMMUNICATION

### When to Ask for Clarification

Ask for clarification if:
- The task description is unclear
- You cannot find a referenced file
- Documentation contradicts source code
- You encounter unexpected Git status
- You are unsure about authorization

### When to Report Issues

Report issues if:
- You encounter an error you cannot resolve
- Git status shows unexpected changes
- You cannot proceed due to a blocker
- Documentation is incorrect or misleading

---

## QUALITY STANDARDS

### Documentation Quality

All documentation must:
- Use actual file paths from the repository
- Include line numbers when referencing code
- Distinguish verified from unverified information
- Be accurate and up-to-date
- Not contain secrets, passwords, or tokens
- Be linked from the documentation index

### Investigation Quality

All investigations must:
- Be evidence-based
- Distinguish source-code from runtime evidence
- Mark unknowns explicitly
- Not make unsupported assumptions
- Document file paths and line numbers

---

## CURRENT AUTHORIZATION

**Phase**: DOCUMENTATION ONLY

**Authorized Actions**:
- ✅ Reading source code
- ✅ Inspecting Git status
- ✅ Creating documentation
- ✅ Updating documentation
- ✅ Investigating code (read-only)

**Prohibited Actions**:
- ❌ Modifying application code
- ❌ Modifying Python model code
- ❌ Modifying training scripts
- ❌ Modifying datasets
- ❌ Training or fine-tuning models
- ❌ Modifying checkpoints
- ❌ Modifying database schemas or records
- ❌ Installing or removing dependencies
- ❌ Committing or pushing to Git
- ❌ Modifying unrelated files

---

## REFERENCES

### Essential Documentation

- **Documentation Index**: `docs/ai-core/README.md`
- **Known Issues**: `docs/ai-core/07-known-issues.md`
- **Audit History**: `docs/ai-core/08-audit-history.md`
- **System Architecture**: `docs/ai-core/01-system-architecture.md`
- **Model Inventory**: `docs/ai-core/02-model-inventory.md`
- **Chat Pipeline**: `docs/ai-core/03-chat-pipeline.md`
- **Training Pipeline**: `docs/ai-core/04-training-pipeline.md`
- **Dataset Audit**: `docs/ai-core/05-dataset-audit.md`
- **Memory and Retrieval**: `docs/ai-core/06-memory-and-retrieval.md`
- **Future Roadmap**: `docs/ai-core/09-future-roadmap.md`

### Root Documentation

- **Main README**: `README.md`
- **Main Docs Index**: `docs/README.md`

---

## FINAL CHECKLIST

Before submitting your work:

- [ ] Read `docs/ai-core/README.md`
- [ ] Reviewed `docs/ai-core/07-known-issues.md`
- [ ] Reviewed `docs/ai-core/08-audit-history.md`
- [ ] Inspected actual source code
- [ ] Distinguished evidence types (VERIFIED, SOURCE-INSPECTED, UNKNOWN)
- [ ] Did not make unauthorized code changes
- [ ] Did not train or modify models
- [ ] Did not modify datasets or checkpoints
- [ ] Did not modify database schemas or records
- [ ] Preserved `cookies.txt` modification
- [ ] Checked Git status before work
- [ ] Checked Git status after work
- [ ] Updated relevant documentation
- [ ] Added entry to audit history if applicable
- [ ] Updated known issues if applicable
- [ ] Validated all documentation links

---

## VIOLATIONS

If you violate these rules:

1. **STOP** immediately
2. **REPORT** what happened
3. **DO NOT** attempt to fix violations without guidance

Violations can cause:
- Loss of user data
- Corruption of model checkpoints
- Breakage of application functionality
- Loss of work

---

## Updates

This guide should be updated when:
- New authorization is granted
- New mandatory rules are established
- Process changes are made
- New documentation is added

**Last Updated**: 2026-10-26  
**Next Review**: After next major phase
