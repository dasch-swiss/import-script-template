# Import Script Template - Workflow Dispatcher

This repository supports a **two-phase sequential workflow**
for transforming raw research data into the DaSCH Service Platform (DSP) format:

Phase 1: Raw Data → Data Model (JSON project definition file)
Phase 2: Data Model + Raw Data → Import Scripts (Python) → DSP XML

---

## Phase 1: Data Modeling

**Goal**: Inductively create a data model (ontology) from raw research data

**When to use**: You have raw research data (CSV, Excel, etc.) but no formal data model yet

**Output**: `project.json` - A JSON file defining the data model structure

**Instructions**: `CLAUDE_01_DATA_MODELING.md`

---

## Phase 2: Import Scripts

**Goal**: Write Python scripts to transform raw data into DSP XML format

**When to use**: You have a completed data model (`project.json`) and need to transform the raw data

**Output**: Python scripts in `src/import_scripts/` that generate XML files

**Instructions**: `CLAUDE_02_IMPORT_SCRIPTS.md`

---

## Instructions for Claude

1. **Ask the user** which phase they're working on
2. **Use the Read tool** to read the corresponding detailed instruction file:
   - Data Modeling → Read [CLAUDE_01_DATA_MODELING.md](CLAUDE_01_DATA_MODELING.md)
   - Import Scripts → Read [CLAUDE_02_IMPORT_SCRIPTS.md](CLAUDE_02_IMPORT_SCRIPTS.md)
3. **Follow those instructions precisely** for the duration of the session
