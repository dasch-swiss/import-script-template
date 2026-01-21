# CLAUDE.md - Data Model Generation from Raw Data

This document provides guidance to Claude Code when creating data models (ontologies) from raw research data
for the DaSCH Service Platform (DSP).

## Overview

This workflow precedes the import script creation described in the main CLAUDE.md.
The goal is to **inductively create an ontology** that abstracts the structure of customer data
into a formal data model suitable for DSP.

**Process Flow:**

```text
Raw Data → Data Model (JSON) → Import Scripts (Python) → XML → DSP
            ↑ THIS DOCUMENT    ↑ MAIN CLAUDE.md
```

## Key Principles

1. **Inductive Reasoning**: Build abstractions from concrete data, not vice versa
2. **Domain-Driven**: Let research questions and data structure guide the model
3. **Standards-Aligned**: Reference CIDOC-CRM and SDHSS where appropriate
4. **Iterative**: Expect multiple refinement cycles with the user
5. **Pragmatic**: Model what exists in the data, not theoretical completeness



## Workflow

### Step 1: Understand the Research Context

**Objective**: Grasp the domain, research questions, and scholarly goals.

**Actions**:

1. Read any provided project documentation (DMP, project descriptions, grant proposals)
2. Identify the research domain (art history, philology, archaeology, etc.)
3. Understand what questions researchers want to answer with this data
4. Note any specific terminology or concepts from the domain

**Ask the user**:

- What is the research project about?
- What are the main research questions?
- What kinds of analysis do researchers want to perform?
- Are there domain-specific standards or vocabularies to follow?

**Example** (from Healing Arts project):

- Domain: Medieval art history and medical history
- Research Question: How do art and literature intersect with pharmacological knowledge (9th-12th centuries)?
- Key Concepts: Manuscripts, herbals, plants as remedies, medical iconography



### Step 2: Data Discovery and Profiling

**Objective**: Understand what data exists and its structure.

**Actions**:

1. **List all data files** and note their formats (CSV, Excel, images, etc.)
2. **Identify file naming patterns**
3. **Read sample data** from each file to understand content
4. **Document metadata** (column headers, value types, relationships indicated by IDs/references)

**Ask the user**:

- Which files contain the core data vs. supplementary information?
- Are there data dictionaries or field descriptions available?
- Which fields are required vs. optional in practice?
- Are there known data quality issues?

**Tool Usage**:

- Use Read tool for CSV/simple formats
- For Excel: ask user to provide sample rows or convert to CSV
- Create a data profiling document

**Create**: `claude_planning/data_profile.md`

   ```markdown
   # Data Profile

   ## Files Overview
   - `Manuscripts.xlsx`: 150 rows, manuscript catalog entries
   - `List_Plants.xlsx`: 300 rows, plant names and properties
   - `Text_with_author.xlsx`: 45 rows, text metadata

   ## Field Analysis
   ### Manuscript.xlsx
   - Shelfmark (unique ID): required, text
   - Date: optional, range or century
   - Repository: required, categorical (12 values)
   - Content: optional, long text
   ...
   ```



### Step 3: Entity Identification

**Objective**: Identify the main "things" (resource classes, properties, controlled vocabularies) in the data.

**Strategy**:

1. **Primary Entities**: The main subjects of research. These will become resource classes.
   - Look for files named after entity types (`Manuscripts.xlsx` → Manuscript class)
   - Identify "noun" concepts that researchers describe independently

2. **Secondary Entities**: Supporting entities that primary entities reference. These will become properties.
   - Entities which don't exist independently, but are rather attributes of primary entities.
   - Column titles are likely candidates for properties.

3. **Media Entities**: Images, scans, documents

4. **Taxonomic Entities**: Entities that become controlled vocabularies, NOT resource classes
   - In DSP, controlled vocabularies are called "lists"
   - Lists are useful for classifications, while classes should represent concepts.
   - Substantial entities of the research domain, even if categorical, should rather be resource classes.
   - If a thing is a property of a substantial entity, it should rather be a list.

**Decision Heuristics**:

| Pattern                                                                         | Resource Class? | List? |
| ------------------------------------------------------------------------------- | --------------- | ----- |
| Has an unlimited number of unique instances that researchers study individually | YES             | NO    |
| Max. 50 categorical values, no additional properties                            | NO              | YES   |
| Has relationships to multiple other entities                                    | YES             | NO    |
| Has many descriptive properties beyond a name                                   | YES             | NO    |
| Simple enumeration (colors, languages, materials)                               | NO              | YES   |

**Ask the user**:

- Which entities do researchers want to query and analyze individually?
- Are there entities that reference each other?
- Should [ENTITY_X] be a resource class or just a controlled vocabulary?
- Can a [ENTITY_A] exist without a [ENTITY_B]?

**Create**: `claude_planning/entity_model.md`

   ```markdown
   # Entity Model

   ## Resource Classes
   1. **Manuscript**: Physical manuscript objects
      - Primary entity, has shelfmark, date, repository
      - Contains pages (ManuscriptPage)
      - References: Text (which texts appear in it), Person (authors)

   2. **Text**: Abstract texts that appear in manuscripts
      - Can appear in multiple manuscripts
      - Has: title, author, text type
      - Referenced by: ManuscriptPage

   ...

   ## Lists (Controlled Vocabularies)
   1. **language**: Latin, German, French, Greek, Old English, Old High German
   2. **texttype**: Herbal, Recipe, Poem, Prayer, Therapeutica, etc.
   ...
   ```



### Step 4: Relationship Mapping

**Objective**: Understand how entities relate to each other.

**Types of Relationships**:

1. **Reference Links** (`hasLinkTo`):
   - Object references another independent object
   - Examples: Manuscript → Person (author), Object → Text (depicts)
   - Cardinality: can be 0-1, 0-n, 1, 1-n

2. **Part-Whole** (`isPartOf`):
   - Entity is a component of another entity
   - Examples: ManuscriptPage isPartOf Manuscript
   - Always used with `seqnum` for ordering

3. **Representation** (`hasRepresentation`):
   - Non-media entity has an associated media entity
   - Example: Object hasRepresentation Photo

4. **Properties** (not links):
   - Simple descriptive attributes
   - No independent existence
   - If the values that the attribute can take are constrained by a controlled vocabulary,
     then we call the property a "list property"
   - Examples: hasDate, hasTitle, hasDescription

**Ask the user**:

- How do [ENTITY_A] and [ENTITY_B] relate?
- Is this relationship one-to-one, one-to-many, or many-to-many?
- Should pages/images be linked TO objects or should objects link TO images?

**Create**: `claude_planning/relationship_diagram.md`

   ```markdown
   # Relationship Diagram

   Person (no dependencies)
   ↑
   |linkToAuthor
   |
   Manuscript (depends on: Person)
   ↑
   |isPartOfManuscript
   |
   ManuscriptPage (depends on: Manuscript)
   ↑
   |linkToText
   |
   Text (depends on: ManuscriptPage)
   ```



### Step 5: Property Definition

**Objective**: Define all properties for each resource class.

**For Each Property, Determine**:

1. **Property Name**: Use descriptive, consistent naming
  Depending on the type of the property, specific patterns should be followed:
   - `hasXX` for text/integer/date/... values (`hasName`)
   - `isXX` for boolean values (`isPublished`)
   - `isPartOfXX` for ‘part of’ other classes values (`isPartOfBook`)
   - `linkToXX` for links to other classes (`linkToAuthor`)
   - `hasXXList` or `hasXXType` for list values (`hasTopicList`, `hasBookType`)

2. **Property Type**: Based on data type

   | Data Type in Source      | DSP Property super | DSP object   | GUI Element |
   | ------------------------ | ------------------ | ------------ | ----------- |
   | Yes/No, True/False       | hasValue           | BooleanValue | Checkbox    |
   | Hex color                | hasColor           | ColorValue   | Colorpicker |
   | Date/Date range          | hasValue           | DateValue    | Date        |
   | Decimal number           | hasValue           | DecimalValue | SimpleText  |
   | Integer                  | hasValue           | IntValue     | SimpleText  |
   | Short text (< 255 chars) | hasValue           | TextValue    | SimpleText  |
   | Long text, plain         | hasValue           | TextValue    | Textarea    |
   | Long text, formatted     | hasValue           | TextValue    | Richtext    |
   | URI/URL                  | hasValue           | UriValue     | SimpleText  |
   | Geonames.org ID          | hasValue           | GeonameValue | Geonames    |
   | Controlled vocab         | hasValue           | ListValue    | List        |
   | Reference to resource    | hasLinkTo          | :ClassName   | Searchbox   |
   | Part of resource         | isPartOf           | :ClassName   | Searchbox   |
   | Sequence number          | seqnum             | IntValue     | SimpleText  |

3. **Cardinality**: Based on data patterns

   | Pattern in Data                      | Cardinality |
   | ------------------------------------ | ----------- |
   | Always present, single value         | `1`         |
   | Sometimes missing, single value      | `0-1`       |
   | Always present, can have multiple    | `1-n`       |
   | Sometimes missing, can have multiple | `0-n`       |

   **Cardinality Decision Tips**:
      - Review actual data to see if fields are always populated
      - Ask: "Can there be multiple X per Y?"
      - Conservative approach: use `0-1` and `0-n` unless data strongly indicates required

4. **List Reference** (for ListValue properties):
   - Specify which list in `gui_attributes.hlist`
   - Example: `"hlist": "language"`

**Ask the user**:

- Is [FIELD_X] always present in the data?
- Can [ENTITY_Y] have multiple [PROPERTY_Z]?
- Should [FIELD_A] be simple text or a controlled vocabulary?
- What's the expected length of [TEXT_FIELD_B]? (determines SimpleText vs Textarea vs Richtext)

**Create**: `claude_planning/CLASS_NAME_properties.md` for each class

   ```markdown
   # Manuscript Properties

   ## Required Properties (cardinality: 1 or 1-n)
   1. **hasShelfmark** (1)
      - Type: TextValue / SimpleText
      - Source: Column "Shelfmark" in Manuscripts.xlsx
      - Example: "Basel, UB, O IV 28"

   2. **hasCopyright** (1)
      - Type: TextValue / SimpleText
      - Source: Repository standard copyright text
      - Example: "© Universitätsbibliothek Basel"

   ## Optional Properties (cardinality: 0-1 or 0-n)
   3. **hasDate** (0-n)
      - Type: DateValue / Date
      - Source: Column "Date" in Manuscripts.xlsx
      - Examples: "9th century", "ca. 850", "800-850"

   ...
   ```



### Step 6: List Creation

**Objective**: Create controlled vocabularies from categorical data.

**Process**:

1. **Identify Categorical Fields**:
   - Look for fields with repetitive values
   - Usually < 100 unique values
   - Examples: languages, materials, object types, text types

2. **Extract Unique Values**:
   - Read through all data files
   - Collect all distinct values for each categorical field
   - Note frequency to identify typos or variants

3. **Create List Structure**:
   - Flat lists: Simple enumerations (languages, materials)
   - Hierarchical lists: Natural hierarchies (location: country > city, topic > subtopic)

4. **Add Multilingual Labels**:
   - Ask user which languages to support
   - Usually at least English and the project's primary language
   - Examples: `{"en": "Latin", "de": "Latein"}`

5. **Handle Uncertainty**:
   - If data contains uncertainty markers ("Apulie ?"), create separate nodes
   - Examples: `"apulie"` and `"apulie-not-sure"` with labels "Apulie" and "Apulie ?"

**List Naming Conventions**:

- List name: lowercase-with-hyphens (e.g., `"text-type"`, `"production-center"`)
- Node name: lowercase-with-hyphens (e.g., `"old-high-german"`, `"figures-rouges"`)
- Labels: Proper capitalization in each language

**Ask the user**:

- Which language(s) should lists support?
- Should we create hierarchical structure for [LIST_X]? (e.g., Location: Country > City)
- How to handle uncertainty markers in the data?
- Are there standard controlled vocabularies we should use? (Getty AAT, etc.)

**Create**: `claude_planning/lists_definition.md`

   ```markdown
   # Lists Definition

   ## List: language
   **Purpose**: Languages in which texts are written
   **Type**: Flat list
   **Values**: 7 nodes

   | Node Name       | English Label   | German Label   | Source        |
   |-----------------|-----------------|----------------|---------------|
   | latin           | Latin           | Latein         | Most common   |
   | german          | German          | Deutsch        | Modern German |
   | old-high-german | Old High German | Althochdeutsch | Medieval      |
   | old-english     | Old English     | Altenglisch    | Medieval      |
   | french          | French          | Französisch    |               |
   | greek           | Greek           | Griechisch     | Ancient       |
   | english         | English         | Englisch       | Modern        |

   ## List: topic
   **Purpose**: Thematic categorization
   **Type**: Hierarchical (2-3 levels)
   **Values**: Multiple root nodes with children

   ### Top level node: ancient-god (Antike Gottheit / Ancient God)
   - asclepius (Asklepios / Asclepius)
   - apollo (Apollo / Apollo)
   - artemisia (Artemisia / Artemisia)
   - chiron (Chiron / Chiron)
   - hygieia (Hygieia / Hygieia)

   ### Top level node: christentum (Christentum / Christianity)
   - adam (Adam / Adam)
   - christ (Christus / Christ)
   - blessing-of-the-cross (Kreuzsegen / Blessing of the cross)
   - christus-medicus (Christus medicus / Christus medicus)
   - saints (Heilige / Saints)
   - longinus (Longinus / Longinus)
   - mary (Maria / Mary)

   ...
   ```



### Step 7: CIDOC-CRM and SDHSS Alignment

**Objective**: Align the data model with standard ontologies where appropriate.

**Strategy**:

1. **Review Standard Ontologies**:
   - CIDOC-CRM: <https://cidoc-crm.org> (for cultural heritage)
   - SDHSS: <https://ontome.net/namespace/11> (for humanities)

2. **Map Resource Classes**:
   - Manuscript → E22 Human-Made Object (CIDOC-CRM)
   - Person → E21 Person (CIDOC-CRM)
   - Text → E33 Linguistic Object (CIDOC-CRM)
   - Place → E53 Place (CIDOC-CRM)

3. **Map Properties**:
   - hasDate → P4 has time-span (CIDOC-CRM)
   - linkToAuthor → P94i was created by (CIDOC-CRM)
   - hasTitle → P102 has title (CIDOC-CRM)

4. **Document Alignments** (as comments in properties or separate documentation):

**Important**: DSP data models are pragmatic, not pure CIDOC-CRM implementations.

- Document the conceptual alignment
- Don't try to force every property into CIDOC-CRM if it doesn't fit naturally
- Use CIDOC-CRM as inspiration, not a straitjacket

**Ask the user**:

- Are there specific ontologies this project should align with?
- Is CIDOC-CRM/SDHSS alignment a priority or optional?
- Should we document these alignments in the JSON or separately?

**Create**: `claude_planning/ontology_alignment.md`

   ```markdown
   # Ontology Alignment

   ## CIDOC-CRM Mapping

   ### Resource Classes
   | DSP Class      | CIDOC-CRM Class       | Note                       |
   |----------------|-----------------------|----------------------------|
   | Manuscript     | E22 Human-Made Object | Physical manuscript object |
   | Text           | E33 Linguistic Object | Abstract textual work      |
   | Person         | E21 Person            | Historical persons         |
   | ManuscriptPage | E22 Human-Made Object | Part of manuscript         |

   ### Properties
   | DSP Property | CIDOC-CRM Property  | Note                  |
   |--------------|---------------------|-----------------------|
   | hasDate      | P4 has time-span    | Creation date         |
   | linkToAuthor | P94i was created by | Authorship            |
   | hasShelfmark | P1 is identified by | Shelf mark identifier |

   ## SDHSS Concepts
   - Consider using SDHSS C24 Text for abstract texts
   - SDHSS C18 Manuscript for physical manuscripts
   ...
   ```



### Step 8: JSON Data Model Construction

**Objective**: Assemble all pieces into valid DSP JSON project definition.

**Structure**:
```json
{
  "$schema": "https://raw.githubusercontent.com/dasch-swiss/dsp-tools/main/src/dsp_tools/resources/schema/project.json",
  "project": {
    "shortcode": "XXXX",  // Ask user or assign temporary
    "shortname": "projectname",
    "longname": "Full Project Title",
    "descriptions": {"en": "...", "de": "..."},
    "keywords": ["keyword1", "keyword2"],
    "lists": [...],
    "ontologies": [{
      "name": "ontologyname",
      "label": "Ontology Label",
      "properties": [...],
      "resources": [...]
    }]
  }
}
```

**Reference data model**: Take this examplary JSON file for syntactic reference:
<https://raw.githubusercontent.com/dasch-swiss/daschland-scripts/refs/heads/main/data/output/daschland.json>

**Workflow**:

1. **Start with project metadata**:
   - Ask user for shortcode, shortname, longname
   - Draft descriptions in required languages
   - Identify 5-10 keywords

2. **Add lists** (from Step 6):
   - Copy from `lists_definition.md`
   - Ensure correct structure (flat vs. hierarchical)

3. **Define properties** (from Step 5):
   - All properties used by any resource class
   - Include `name`, `super`, `object`, `labels`, `gui_element`
   - Add `gui_attributes` for ListValue properties

4. **Define resource classes** (from Steps 3-5):
   - Include `name`, `super`, `labels`, `comments`
   - Add all cardinalities with `propname`, `cardinality`, `gui_order`
   - How to determine the value for "super":
      - Resource: Use this for all non-multimedia classes
      - ArchiveRepresentation: zipped archives
      - AudioRepresentation: audios
      - DocumentRepresentation: PDF, MS Office, Epub
      - MovingImageRepresentation: videos
      - StillImageRepresentation: photos, scans, images
      - TextRepresentation: text files (e.g. TXT, CSV, XML, HTML, JSON)

5. **Validate**:
   - Use DSP-TOOLS schema validation: `uvx dsp-tools create project.json --validate-only`
   - Check for missing references
   - Verify all `propname` references exist

**Ask the user**:

- What shortcode should we use? (4-digit hex, e.g., "083E")
- What shortname? (lowercase, no spaces, e.g., "healingarts")
- What language(s) for descriptions and labels?
- Should we include user definitions or add those later?

**Create**: `project_datamodel.json`

**Validation Commands**:

```bash
# Validate JSON structure
uvx dsp-tools create project_datamodel.json --validate-only

# If validation passes, create on local DSP for testing
uvx dsp-tools start-stack
uvx dsp-tools create project_datamodel.json
```



### Step 9: Documentation and Review

**Objective**: Create comprehensive documentation for review and future reference.

**Documents to Create**:

1. **`claude_planning/data_model_summary.md`**: High-level overview
   - Resource classes with descriptions
   - Key relationships
   - Design decisions and rationale

2. **`claude_planning/data_model_decisions.md`**: Document key choices
   - Why certain entities became classes vs. lists
   - Cardinality justifications
   - Alternative approaches considered

3. **`claude_planning/data_model_questions.md`**: Outstanding questions
   - Ambiguities that need user clarification
   - Alternative designs for user to choose from
   - Data quality issues discovered

**Review Checklist**:

- [ ] All entities in the data are represented
- [ ] All relationships are captured
- [ ] Cardinalities match data patterns
- [ ] Lists cover all categorical values
- [ ] Property types are appropriate
- [ ] Documentation is complete



## Common Patterns from Examples

### Pattern 1: Manuscript Projects

**Typical Structure**:

- **Manuscript**: Physical object (codex, document)
  - Properties: shelfmark, date, repository, material, format
  - Links: author, texts contained
- **ManuscriptPage**: Image of a page
  - Properties: folio/page number, content description, topics
  - Links: isPartOfManuscript, texts on page, persons depicted, objects depicted
  - Sequence: hasPagenum (seqnum property)
- **Text**: Abstract text that appears in manuscripts
  - Properties: title, text type, author
  - Can appear in multiple manuscripts
- **Person**: Authors, scribes, depicted figures
  - Properties: name, dates, function, GND reference

### Pattern 2: Museum/Archaeology Projects

**Typical Structure**:

- **Object**: Primary artifact (vase, sculpture, medical box)
  - Properties: inventory number, dating, material, dimensions, technique
  - Categorical: object type, production center, discovery place
  - Links: artist, museum, depicted subjects
- **Photo**: Image of object
  - Properties: photo credit, license, date
  - Links: isPartOf Object, represents Artist
  - Sequence: hasPhotoObjectNum (if multiple views)
- **Museum**: Repository
  - Properties: name, location, URL
- **Artist**: Creator
  - Properties: name, activity period, role

### Pattern 3: Natural History/Plant Projects

**Typical Structure**:

- **Plant**: Main entity
  - Properties: Latin name, botanical name, German name, synonyms
  - Properties: healing properties, usage
  - Links: texts mentioning it, images depicting it
- **Text**: Herbal or pharmacological text
  - Links: author, plants mentioned
- **ManuscriptPage**: Herbal illustration
  - Links: plant depicted, manuscript



## Anti-Patterns to Avoid

### 1. Over-Modeling

**Problem**: Creating resource classes for every tiny concept
**Solution**: Use lists for simple categorical values
**Example**: Don't create a "Language" resource class; use a language list

### 2. Under-Modeling

**Problem**: Cramming everything into one "Object" class
**Solution**: Distinguish conceptual entities (Text) from physical objects (Manuscript)
**Example**: Separate "Text" (abstract work) from "Manuscript" (physical copy)

### 3. List Explosion

**Problem**: Creating hundreds of list nodes from raw data typos and variants
**Solution**: Clean and normalize values; use hierarchies to manage complexity
**Example**: Normalize "München", "Munich", "Munchen" → single node "munich"

### 4. Property Proliferation

**Problem**: Creating separate properties for minor variations (hasGermanName, hasFrenchName, hasEnglishName...)
**Solution**: Use single multilingual property
**Example**: One "hasName" property that can have multiple values, or use comments/description for alternative names

### 5. Circular Dependencies

**Problem**: Class A links to Class B which links back to Class A
**Solution**: Carefully design link directions; use bidirectional links sparingly
**Example**: Manuscript → Text is sufficient; don't also require Text → Manuscript



## Practical Tips

### Working with Users

1. **Use Visual Aids**:
   - Create simple diagrams showing entities and relationships
   - Use examples from their actual data
   - Show before/after comparisons for design decisions

2. **Iterate**:
   - Start with core entities and expand
   - Get feedback early and often
   - Be prepared to revise

3. **Explain Trade-offs**:
   - "We can model this as a resource class (more flexible, more complex) or a list (simpler, less flexible)"
   - Present options with pros/cons

4. **Manage Scope**:
   - Focus on what's in the data now
   - Note future extensions in documentation
   - Don't model hypothetical future data

### Data Quality Issues

When you encounter data problems:

1. **Document, Don't Fix**:
   - Note issues in `data_quality_issues.md`
   - Don't silently correct data
   - Alert user to problems

2. **Common Issues**:
   - Inconsistent spelling/naming
   - Missing required fields
   - Inconsistent date formats
   - Mixed languages in same field
   - Ambiguous references

3. **Handle Gracefully**:
   - Use optional cardinalities (0-1, 0-n) when data is spotty
   - Suggest data cleaning steps



## Deliverables Checklist

When data modeling is complete, you should have:

- [ ] `project_datamodel.json` - The JSON data model file
- [ ] `claude_planning/data_model_summary.md` - High-level overview
- [ ] `claude_planning/data_profile.md` - Source data analysis
- [ ] `claude_planning/entity_model.md` - Resource classes and relationships
- [ ] `claude_planning/relationship_diagram.md` - Dependencies between the classes
- [ ] `claude_planning/lists_definition.md` - All controlled vocabularies
- [ ] `claude_planning/CLASS_NAME_properties.md` - For each resource class
- [ ] `claude_planning/data_model_decisions.md` - Design rationale
- [ ] `claude_planning/ontology_alignment.md` - CIDOC-CRM/SDHSS mapping (if applicable)
- [ ] `claude_planning/data_quality_issues.md` - Known problems in source data



## Example: Full Workflow for a New Project

**Scenario**: Researcher has data about medieval illuminated manuscripts.

**Step-by-step**:

1. **Context**: Read project description → understand it's about iconography in religious manuscripts

2. **Data Discovery**:
   - `Manuscripts.xlsx`: 120 manuscripts with shelfmarks, dates, repositories
   - `Illuminations.csv`: 450 illumination descriptions with folio numbers
   - `Saints.csv`: 80 saints depicted in illuminations
   - Images folder: 450 JPEG files named by manuscript_folio

3. **Entities**:
   - Resource Classes: Manuscript, Illumination (as StillImageRepresentation), Saint
   - Lists: Repository (25 libraries), IconographyType (20 categories), Century (9th-15th)

4. **Relationships**:
   - Illumination isPartOf Manuscript
   - Illumination linkToSaint (depicted saint)

5. **Properties**:
   - Manuscript: hasShelfmark (1), hasRepository (1-list), hasCentury (0-1-list), hasDescription (0-1)
   - Illumination: hasFolio (1), hasIconographyType (1-n-list), hasDescription (0-1), linkToSaint (0-n)
   - Saint: hasName (1), hasFeastDay (0-1-date), hasDescription (0-1)

6. **Lists**:
   - repository: flat list, 25 nodes
   - iconography-type: hierarchical (Religious > Old Testament > specific scenes)
   - century: flat list, 9th through 15th

7. **JSON**: Build project_datamodel.json with all above

8. **Validate**: Run dsp-tools validation

9. **Review**: Present to researcher, iterate on feedback

10. **Approve**: Create on local DSP, test with sample data



---



## Quick Reference: Decision Trees

### Is this a Resource Class or a List?

```
Does it have multiple descriptive properties beyond a name?
├─ YES → Resource Class
└─ NO
    └─ Do you need to query/analyze individual instances?
        ├─ YES → Resource Class (e.g., Person, even if simple)
        └─ NO → List (e.g., Language, Material)
```

### What's the cardinality?

```
Is this property always present in the data?
├─ YES
│   └─ Can there be multiple values?
│       ├─ YES → 1-n
│       └─ NO → 1
└─ NO (sometimes missing)
    └─ Can there be multiple values?
        ├─ YES → 0-n
        └─ NO → 0-1
```

### What property type?

```
Is it a reference to another resource class?
├─ YES → hasLinkTo (or isPartOf/hasRepresentation)
└─ NO
    └─ Is it from a controlled vocabulary?
        ├─ YES → ListValue
        └─ NO
            └─ What's the data type?
                ├─ Date/Date Range → DateValue
                ├─ Number (integer) → IntValue
                ├─ Number (decimal) → DecimalValue
                ├─ URL → UriValue
                ├─ Short text → TextValue + SimpleText
                ├─ Long text (plain) → TextValue + Textarea
                └─ Long text (formatted) → TextValue + Richtext
```

---

**Remember**: This is an iterative, collaborative process.
Use the TodoWrite tool to track progress through these steps,
and use AskUserQuestion frequently to ensure the model matches the research needs.
