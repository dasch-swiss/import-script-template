# DSP Import Script Template

This template repository provides a structured foundation for creating import scripts that transform research data into
DSP (DaSCH Service Platform) XML format using the `xmllib` module from dsp-tools.

## What is this?

This template helps you create Python scripts that:

- Transform your research data (CSV, Excel, JSON, etc.) into DSP XML format
- Validate data against your DSP data model (JSON project definition)
- Generate XML files ready for upload to DSP

The template includes a comprehensive `CLAUDE.md` file that guides **Claude Code** through the entire import script
development process, from analyzing your data model to implementing and validating each resource class.

## Prerequisites

Before you begin, ensure you have:

1. **Your DSP project files:**
    - JSON project definition file (data model)
    - Source data files (CSV, Excel, JSON, or other formats)

2. **System requirements:**
    - [uv](https://astral.sh/uv) - Python package manager
    - [just](https://github.com/casey/just) - Command runner (optional but recommended)
    - Claude Code CLI

## Getting Started

### 1. Create Your Project from This Template

Click "Use this template" on GitHub or clone this repository:

```bash
git clone <your-new-project-repo>
cd <your-new-project>
```

### 2. Set Up Your Environment

Install dependencies and set up the development environment:

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate

# Install pre-commit hooks for code quality
pre-commit install

# Install just (command runner) - macOS
brew install just

# Configure xmllib warnings output path
echo XMLLIB_WARNINGS_CSV_SAVEPATH="xmllib_warnings.csv" >> .env
```

### 3. Add Your Project Files

Place your files in the appropriate directories:

## Project Structure

```
.
├── CLAUDE.md                # Comprehensive instructions for Claude Code
├── data/
│   ├── input/              # Your source data files (CSV, Excel, JSON, etc.)
│   └── output/             # Generated XML files (created by scripts)
├── claude_planning/        # Planning documents for each resource class (required by Claude)
│   ├── class_todo_list.md  # Import order and progress tracking
│   └── <class_name>_plan.md  # Detailed plans for each class
├── src/
│   ├── utils/
│   │   ├── resource_ids.py # ID generation functions (shared)
│   │   └── ...             # Other utility functions
│   └── import_scripts/
│       ├── main.py         # Main entry point
│       └── import_<class>.py  # Import script for each resource class
└── xmllib_warnings.csv     # Validation warnings from xmllib (generated)
```

## Working with Claude Code

This template is designed to work seamlessly with **Claude Code**. The `CLAUDE.md` file contains comprehensive
instructions that guide Claude through the entire import script development workflow.

### Workflow Overview

1. **Initial Setup**
   ```bash
   claude
   ```
   Start Claude Code in your project directory.

2. **Start the Import Process**

   Tell Claude what you want to accomplish:
   ```
   "Help me create import scripts for my DSP project. My JSON data model is in <project.json>
   and my source data is in <data/input/>"
   ```

3. **Claude's Automated Workflow**

   Claude Code will automatically:
    - Read the `CLAUDE.md` instructions
    - Analyze your JSON data model to determine the correct import order
    - Ask you questions about each resource class and property
    - Create detailed planning documents in `claude_planning/`
    - Implement import scripts in `src/import_scripts/`
    - Run validations and report any issues
    - Track progress using todo lists

4. **What Claude Will Ask You**

   For each resource class, Claude will ask about:
    - **Data sources**: Which file contains the data?
    - **Column mappings**: Which columns map to which properties?
    - **Data transformations**: Any cleaning or formatting needed?
    - **ID generation**: How should resource IDs be constructed?

5. **Validation**

   After each class implementation, Claude will:
    - Check XML schema compliance
    - Validate against your data model
    - Report any warnings from `xmllib_warnings.csv`
    - Wait for your approval before continuing

### Example Interaction

```
You: "Create import scripts for my project. Start with analyzing the data model."

Claude: "I'll analyze your data model and create import scripts. Let me start by reading
the JSON project definition and determining the import order..."

[Claude analyzes the data model]

Claude: "I've identified 4 resource classes in this order:
1. Person (no dependencies)
2. Organization (no dependencies)
3. Document (links to: Person, Organization)
4. Page (links to: Document)

Let me start with the Person class. I need to gather some information..."

[Claude asks questions via AskUserQuestion tool]

Claude: "For the Person class, where does the data for ':hasFirstName' come from?"
- Option 1: data/input/persons.csv, column "FirstName"
- Option 2: data/input/people.xlsx, column "first_name"
- Other...

[You select an option or provide custom input]

[Claude creates planning document and implements the import script]

Claude: "I've implemented the Person import script. Running validation now..."

[Claude runs validations and reports results]
```

### Tips for Working with Claude Code

**Be specific about your requirements:**

- Provide clear information about data formats and structures
- Mention any special business rules or data constraints
- Share examples of edge cases you're aware of

**Review generated code:**

- Check the planning documents in `claude_planning/` to verify Claude understood correctly
- Review `xmllib_warnings.csv` after each run
- Test with a small subset of data first

**Iterate incrementally:**

- Claude validates each resource class before moving to the next
- Fix any issues in your source data (not in the scripts)
- You can ask Claude to regenerate specific parts if needed

**Manual intervention when needed:**

- As a safety measure, Claude does not have the permission to change the source data
- If the data must be changed this should be done separately
- You can always ask Claude to adjust the import logic
- Review and modify generated scripts as needed

## Manual Development (Without Claude Code)

If you prefer to write import scripts manually, you can:

1. Study the `CLAUDE.md` file for guidance on structure and best practices
2. Follow the workflow outlined in CLAUDE.md manually
3. Create planning documents for each class in `claude_planning/`
4. Implement import scripts following the code structure in CLAUDE.md
5. Run validations after each class

The template structure and `CLAUDE.md` documentation are useful references even when working manually.

## Development Workflow

### Code Quality Checks

Check your type hints:

```bash
just type-check
```

Auto-format your code:

```bash
just format
```

Check if there are linting errors:

```bash
just lint
```

Run the tests:

```bash
pytest
```

## Troubleshooting

If something doesn't work, check the following:

- Run `pwd` to check if you are at the root of the repository.
  If you're in a subfolder, your terminal commands might fail.
- Activate the virtual environment with `source .venv/bin/activate`
- Reinstall the virtual environment with `rm -rf .venv; uv sync; source .venv/bin/activate`