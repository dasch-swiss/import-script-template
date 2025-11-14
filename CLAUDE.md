# CLAUDE.md - import scripts

This file provides guidance to Claude Code when writing import scripts using the `xmllib` module of dsp-tools.

## Big Picture

We at DaSCH operate DSP (DaSCH Service Platform),
a VRE (Virtual Research Environment) for research data from the (Digital) Humanities.
When researchers deliver their data to us (DaSCH), we

- define a project structure with a data model (a JSON file)
- write Python scripts (using the `xmllib` module of dsp-tools) to transform their data into our DSP XML format.

The data model defines resource classes, properties, and lists.
The XML file defines single resources which must conform to the data model of the JSON file.

This project heavily relies on DSP-TOOLS for data model creation and upload workflows.
DSP-TOOLS is the command-line interface for the DSP.

## Key DSP-TOOLS Commands Used

- **Create JSON project definition**: `dsp-tools excel2json` converts Excel files into a JSON file.
  This is a pure restructuring, the information stays the same.
- **Start local DSP server**: `dsp-tools start-stack --no-prune` spins up a local DSP server,
  for local testing of the JSON and the XML file.
- **Data Model Creation**: `dsp-tools create <project.json>` establishes the data model from the JSON file on the local DSP server.
- **XSD Schema Check**: `dsp-tools xmlupload --validate-only <data.xml>` checks XML schema compliance without uploading.
- **Validation**: `dsp-tools validate-data <data.xml>` validates the XML data against the data model on the local server.
- **Data Upload**: `dsp-tools xmlupload <data.xml>` populates the project with resources and metadata defined in the XML file.

## xmllib

The `xmllib` module is the public API library for programmatic creation of DSP XML files.
It provides a type-safe, validated approach to generating XML data that conforms to DSP (DaSCH Service Platform)
requirements.
Please carefully read the following documentations, they are crucial in order to understand the xmllib:

- Documentation of xmllib (see also the subpages): <https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/overview/>
- Documentation of the JSON file format:
    - <https://docs.dasch.swiss/latest/DSP-TOOLS/data-model/json-project/overview/>
    - <https://docs.dasch.swiss/latest/DSP-TOOLS/data-model/json-project/ontologies/>
    - <https://docs.dasch.swiss/latest/DSP-TOOLS/data-model/json-project/caveats/>
- Documentation of the XML file format: <https://docs.dasch.swiss/latest/DSP-TOOLS/data-file/xml-data-file/>

If you cannot retrieve these documentations, alert me. Without reading these, there's no point in continuing.

The `xmllib` validates a lot of the input automatically. The diagnostic results are saved in `xmllib_warnings.csv`.
**There is no need to duplicate these validations in your import scripts.**

**What xmllib validates automatically:**

1. **Data Type Validation** - Checks if values match expected types and emits warnings if type mismatches occur:
    - **Boolean**: Converts various formats (yes/no, ja/nein, oui/non, true/false, 1/0) and warns if invalid
    - **Color**: Validates hex color format (e.g., `#FF0000`)
    - **Date**: Validates DSP date format (`CALENDAR:ERA:DATE` or `ERA:DATE` or `DATE`)
    - **Decimal**: Checks for valid floating point numbers
    - **Geoname**: Validates geoname IDs
    - **Integer**: Checks for valid integers
    - **Link**: Validates xsd:ID or DSP resource IRI format
    - **List**: Validates list name and node name are non-empty
    - **Timestamp**: Validates timestamp format
    - **URI**: Checks for valid URI format

2. **Empty/None Value Detection** - Automatically detects and handles:
    - `None`, `pd.NA`, empty strings, whitespace-only strings
    - Empty collections (lists, tuples, sets, dictionaries)

3. **Resource ID Validation**:
    - Checks if resource IDs conform to xsd:ID format (must start with letter or underscore, contain only valid characters)
    - **Warns about duplicate resource IDs** across all resources

4. **Richtext Syntax Validation** - Validates that richtext:
    - Is well-formed XML
    - Has proper standoff markup (links, formatting tags)
    - Reserved characters (`<`, `>`, `&`) are properly escaped when not part of markup

5. **File Path Validation** - Validates file paths and IIIF URIs

All validation warnings are saved to `xmllib_warnings.csv` in the project root directory with severity levels (INFO, WARNING, ERROR).

## Project Structure

```
.
├── data/
│   ├── input/           # Original data files (CSV, Excel, etc.)
│   └── output/          # Generated XML files
├── claude_planning/     # Planning documents for each class
│   └── <class_name>_plan.md
├── src/
│   ├── utils/
│   │   ├── some_util.py  # Shared functions across multiple import scripts
│   │   └── resource_ids.py  # Shared functions that creates resource ids
│   └── import_scripts/
│       ├── main.py       # Main entry point that calls all import functions
│       └── import_<class_name>.py  # xmllib code for each resource class
└── xmllib_warnings.csv  # Generated warnings from xmllib (created in project root)
```

## Reference Examples

A repository of demonstration import scripts is available at: <https://github.com/dasch-swiss/daschland-scripts/>

**Important Guidelines:**

1. **Use as reference only** - These examples show real-world implementations but **vary in structure**
2. **CLAUDE.md is authoritative** - When there's a conflict between examples and this document, **always follow this CLAUDE.md**
3. **Examples may be outdated** - Some scripts may use older patterns or project-specific approaches
4. **Structure variations** - Not all examples follow the exact structure defined in "Project Structure" above

**When to consult the examples:**

- **Data transformation patterns** - See how complex data cleaning is handled (e.g., date parsing, string normalization)
- **Edge case handling** - Learn how others dealt with missing values, malformed data, or special characters
- **List lookups** - See practical examples of mapping source data to list nodes
- **Link resolution** - Understand how to handle references between resources across different classes
- **File handling** - See how file paths and IIIF URIs are processed in practice

**When NOT to follow the examples:**

- If an example uses a different folder structure than defined above
- If an example doesn't use the `ListLookup` class (older approach)
- If an example manually validates data that xmllib now validates automatically
- If an example modifies source data files (violates our directives)

**Best practice:** Use examples to understand **data handling logic**, 
but implement using the **patterns and structure defined in this CLAUDE.md**.

## Workflow

**Important Directives:**

- Never change the input data files.
- Never "fix" the input data programmatically.
- Data corrections must be done manually by the user in the source files.
- Always use the TodoWrite tool to track progress throughout the workflow.

### Step 1: Read Documentation

After reading this CLAUDE.md file, fetch and read all the xmllib documentation URLs listed above.

### Step 2: Analyze Data Model and Determine Import Order

Analyze the JSON data model to determine the correct order for importing resource classes:

1. **Identify all resource classes** in the JSON project file
2. **Identify link dependencies** for each class:
    - A class has a dependency if it has a cardinality with a property that has `hasLinkTo`, `hasRepresentation`, or `isPartOf` as super-property
    - Note which class(es) it links to (the `object` field of the property)
3. **Create dependency graph**: Class A must be imported before Class B if B links to A
4. **Perform topological sort** to determine valid import order:
    - Start with classes that have zero dependencies (no outgoing links)
    - Then classes that only link to previously processed classes
    - Continue until all classes are ordered
5. **Check for circular dependencies**: If found, alert the user immediately
6. **Save Order**: Save the order at `claude_planning/class_todo_list.md`

**Example:**

```
Import Order:
1. Person (no dependencies)
2. Organization (no dependencies)
3. Document (links to: Person, Organization)
4. Page (links to: Document, has isPartOf)
```

### Step 3: Gather Information for Each Class

For each class in the import order, use the AskUserQuestion tool to gather information about each property:

**Questions to ask per property (cardinality):**

1. **Data source**: Where does the data for this property come from?
    - File name
    - API endpoint or database query
2. **Data location**: If tabular format, what is the column name or cell reference?
3. **Data cleaning**: Is there any cleaning, transformation, or mapping necessary?
    - Empty value handling
    - Format conversions
    - Value mappings (e.g., "Yes" → True, "Red" → "#FF0000")
4. **Special cases**: Are there any edge cases or exceptions to handle?

### Step 4: Create Planning Document

Create a detailed planning document at `claude_planning/<class_name>_plan.md` that includes:

1. **Class overview**: Name, super class, description
2. **Data source mapping**: File paths and formats
3. **Property mapping table**:
   ```markdown
   | Property Name | Cardinality | Data Source | Column/Field | Cleaning Required | Notes |
   |---------------|-------------|-------------|--------------|-------------------|-------|
   | :hasTitle     | 1           | data.csv    | Title        | Strip whitespace  | -     |
   ```
4. **Data cleaning operations**: Detailed steps for each transformation
5. **Link dependencies**: Which resources this class links to and how to resolve IDs
6. **Python code structure**: Include the template from "Python Code Set-Up"
7. **Test cases**: Sample data rows and expected output

### Step 5: Implement the Import Script

Write the import script following the "Python Code Set-Up" section below.

**During implementation:**

- Use TodoWrite to track subtasks (reading data, creating resources, adding properties, etc.)
- Mark each task as in_progress before starting, and as completed immediately after finishing

### Step 6: Monitor xmllib Warnings

The xmllib module saves warnings to `xmllib_warnings.csv` in the project root directory.

**Warning severity levels:**

- **INFO**: Informational messages, no action required
- **WARNING**: Issues that will cause problems later (e.g., invalid references, format issues)
- **ERROR**: Critical issues that prevent the code from continuing

**Action required:**

- After running your import script, check `xmllib_warnings.csv`
- If you find **WARNING** or **ERROR** severity issues:
    - Analyze the warnings and their causes
    - Alert the user with a summary of the issues
    - Wait for user guidance before proceeding
    - Do NOT attempt to fix data issues by modifying source files

### Step 7: Validate Each Resource Class

After completing implementation for one resource class, validate it through the following steps **in sequence**:

1. **XSD Schema Validation**:
   ```bash
   dsp-tools xmlupload --validate-only data/output/data_<project-shortname>.xml
   ```
    - Checks XML is well-formed and conforms to XSD schema
    - If errors occur: analyze, alert user, wait for guidance

2. **Start Local DSP Server** (if not already running):
   ```bash
   dsp-tools start-stack --no-prune
   ```
    - Spins up local DSP instance for testing
    - Only needs to be done once per session

3. **Create Project with Data Model**:
   ```bash
   dsp-tools create <project.json>
   ```
    - Establishes the data model on the local server
    - If errors occur: check JSON data model, alert user

4. **Validate XML Against Data Model**:
   ```bash
   dsp-tools validate-data data/output/data_<project-shortname>.xml
   ```
    - Validates that XML resources conform to the data model
    - Checks cardinalities, property types, link targets, etc.
    - If errors occur: analyze errors, check property mappings, alert user

**If all validation steps pass:**

- Mark the class as completed in your todo list `claude_planning/class_todo_list.md`
- Proceed to the next resource class in the import order
- Update the main.py to include the new class

**If any validation fails:**

- Do NOT proceed to the next class
- Provide detailed error analysis to the user
- Wait for user guidance on how to fix the issues

## Python Code Set-Up

### Initial Setup (First Class)

Create: `src/import_scripts/main.py`

```python
from dsp_tools import xmllib


def main() -> None:
    # Create the root element
    root = xmllib.XMLRoot.create_new(
        shortcode="0854",  # Update with actual project shortcode
        default_ontology="daschland"  # Update with actual ontology name
    )
    
    # create a list lookup that can be used for all resources
    # Ask user which language to use for labels (e.g., "en", "de", "fr")
    list_lookup = xmllib.ListLookup.create_new("project_json.json", language_of_label="en", default_ontology="daschland")
    # Import all resources (will be added as classes are implemented)
    # Write the root to an XML file
    root.write_file("data/output/data_<project-shortname>.xml")


if __name__ == "__main__":
    main()
```

Create: `src.utils.resource_ids.py`

```python
from dsp_tools import xmllib

def make_<class_name>_id(input_id) -> str:
    # some transformations
    new_id = f"<class_name>_{input_id}"
    return xmllib.make_xsd_compatible_id(new_id)
```

### For Each New Class

**1. Create new file:** `src/import_scripts/import_<class_name>.py`

```python
from dsp_tools import xmllib


def main(list_lookup: xmllib.ListLookup) -> list[xmllib.Resource]:
    """
    Import <ClassName> resources from <data source>.

    Returns:
        List of Resource objects for <ClassName>
    """
    all_resources: list[xmllib.Resource] = []

    # TODO: Load data from source
    # TODO: Process each data item
    # TODO: Create Resource objects with xmllib
    # TODO: Add values based on cardinalities
    # TODO: Append to all_resources

    return all_resources


if __name__ == "__main__":
    # For standalone testing
    list_lookup = xmllib.ListLookup.create_new("project_json.json", language_of_label="en", default_ontology="daschland")
    resources = main(list_lookup)
    print(f"Created {len(resources)} resources")
```

**2. Update:** `src/import_scripts/main.py`

```python
from dsp_tools import xmllib
from src.import_scripts import import_<class_name>


def main() -> None:
    # Create the root element
    root = xmllib.XMLRoot.create_new(
        shortcode="0854",
        default_ontology="daschland"
    )
    # create a list lookup that can be used for all resources
    # Ask user which language to use for labels (e.g., "en", "de", "fr")
    list_lookup = xmllib.ListLookup.create_new("project_json.json", language_of_label="en", default_ontology="daschland")
    # Import all resources
    all_<class_name> = import_<class_name>.main(list_lookup)
    root.add_resource_multiple(all_<class_name>)

    # Write the root to an XML file
    root.write_file("data/output/data_<project-shortname>.xml")


if __name__ == "__main__":
    main()
```

## Task Management with TodoWrite

Always use the TodoWrite tool to manage your workflow:

**For the overall project:**

```python
# Example todo structure
todos = [
    {"content": "Analyze data model and determine import order", "status": "completed",
     "activeForm": "Analyzing data model"},
    {"content": "Import Person class", "status": "completed", "activeForm": "Importing Person class"},
    {"content": "Import Organization class", "status": "in_progress", "activeForm": "Importing Organization class"},
    {"content": "Import Document class", "status": "pending", "activeForm": "Importing Document class"},
]
```

**For each class implementation:**

```python
# Break down into subtasks
todos = [
    {"content": "Gather requirements for Organization class", "status": "completed",
     "activeForm": "Gathering requirements"},
    {"content": "Create planning document", "status": "completed", "activeForm": "Creating planning document"},
    {"content": "Load and clean data", "status": "completed", "activeForm": "Loading and cleaning data"},
    {"content": "Create Resource objects", "status": "in_progress", "activeForm": "Creating Resource objects"},
    {"content": "Validate XSD schema", "status": "pending", "activeForm": "Validating XSD schema"},
    {"content": "Validate against data model", "status": "pending", "activeForm": "Validating against data model"},
]
```

**Important:**

- Mark tasks as completed immediately after finishing them
- Keep only ONE task in_progress at a time
- Update todos throughout the process to keep the user informed

---

# Mapping from Data Model JSON to xmllib

This document provides comprehensive guidance on how to translate
a DSP project JSON definition into xmllib code for creating XML import files.

## Setting Up the XMLRoot

**From JSON:**

```json
{
    "project": {
        "shortcode": "0003",
        ...
        "ontologies": [
            {
                "name": "onto",
                ...
            }
        ]
    }
}
```

**To xmllib:**

```python
# Extract values from JSON
shortcode = project_json["project"]["shortcode"]
default_onto = project_json["project"]["ontologies"][0]["name"]

# Create root
root = xmllib.XMLRoot.create_new(
    shortcode=shortcode,
    default_ontology=default_onto
)
```

**Note:** The `default_ontology` is typically the first ontology in the list.
Properties from this ontology can be referenced with `:propName`.
Properties from other ontologies need the full prefix, e.g. `second-onto:propName`.

## Creating Resources

**From JSON:**

```json
{
    "ontologies": [
        {
            "name": "onto",
            "resources": [
                {
                    "name": "ClassWithEverything",
                    "super": "Resource",
                    "labels": {
                        "en": "Resource with every property"
                    },
                    "cardinalities": [
                        ...
                    ]
                }
            ]
        }
    ]
}
```

**To xmllib:**

```python
# Get resource class definition from JSON
resource_class = ontology["resources"][0]  # "ClassWithEverything"

# Create resource instance
resource = xmllib.Resource.create_new(
    res_id="unique_resource_id",  # From your data, must be unique
    restype=":" + resource_class["name"],  # ":ClassWithEverything"
    label="Title in the DSP-APP"  # From your data
)
```

**Important:**

- `res_id`: Must be a unique identifier for this resource (from your data)
- `restype`: `:` + resource class name (from JSON `resource["name"]`)
- `label`: The display label for the resource (from your data)

### Resource ID Generation Strategies

The `res_id` parameter must be a **unique identifier** for each resource.
- Ask the user how these should be constructed
- Always create a util function in `src.utils.resource_ids.py` so that it will be used consistently
- Internal references (e.g., when one resource links to another)
- xmllib tracks the resource IDs and warns if duplicates are created you do not need to do that manually
- Debugging and tracking during import

**Common strategies:**

1. **Use existing IDs from source data** (recommended when available):
   ```python
   res_id = f"person_{row['PersonID']}"  # e.g., "person_12345"
   ```
   - Most reliable approach
   - Maintains traceability to source data
   - Easier debugging

2. **Generate from unique natural keys**:
   ```python
   # Combine multiple fields to create unique identifier
   res_id = f"book_{author_slug}_{year}_{title_slug}"
   ```
   - Useful when no single ID field exists
   - Must ensure combination is truly unique
   - Validate uniqueness before using

3. **Use UUIDs** (when no natural key exists):
   ```python
   res_id = xmllib.make_xsd_compatible_id_with_uuid("book_id")
   ```

4. **Sequential numbering**:
   ```python
   res_id = f"document_{index:05d}"  # e.g., "document_00001"
   ```
   - Simple and predictable
   - Order-dependent (fragile if source data changes)
   - Only use for resources that have inherent ordering

**Best practices:**

- **Always include a prefix** that identifies the resource class: `person_123`, not just `123`
- **Handle special characters**: `xmllib.make_xsd_compatible_id()`
- **Document your strategy**: Add comments explaining how IDs are generated
- **Be consistent**: Create a function that constructs the ID so that it will be done consistently.

**Example implementation:**

```python
from src.utils.resource_ids import make_person_id

def create_person_resources(data: list[dict]) -> list[xmllib.Resource]:
    all_resources = []
    for row in data:
        # Generate ID from source data
        original_id = row['PersonID']
        res_id = make_person_id(original_id)

        # Create resource
        resource = xmllib.Resource.create_new(
            res_id=res_id,
            restype=":Person",
            label=row['FullName']
        )
        all_resources.append(resource)
    return all_resources
```

## Property-Type to xmllib Method Mapping

This table shows how JSON property definitions map to xmllib methods:

| JSON `super`        | JSON `object`                    | JSON `gui_element`     | xmllib Method       | 
|---------------------|----------------------------------|------------------------|---------------------|
| `hasValue`          | `BooleanValue`                   | `Checkbox`             | `.add_bool()`       | 
| `hasColor`          | `ColorValue`                     | `Colorpicker`          | `.add_color()`      | 
| `hasValue`          | `DateValue`                      | `Date`                 | `.add_date()`       | 
| `hasValue`          | `DecimalValue`                   | `Spinbox`/`SimpleText` | `.add_decimal()`    | 
| `hasValue`          | `GeonameValue`                   | `Geonames`             | `.add_geoname()`    | 
| `hasValue`          | `IntValue`                       | `Spinbox`/`SimpleText` | `.add_integer()`    | 
| `hasValue`          | `ListValue`                      | `List`                 | `.add_list()`       | 
| `hasValue`          | `TextValue`                      | `SimpleText`           | `.add_simpletext()` | 
| `hasValue`          | `TextValue`                      | `Textarea`             | `.add_textarea()`   | 
| `hasValue`          | `TextValue`                      | `Richtext`             | `.add_richtext()`   | 
| `hasComment`        | `TextValue`                      | `Richtext`             | `.add_richtext()`   | 
| `hasValue`          | `TimeValue`                      | `TimeStamp`            | `.add_time()`       | 
| `hasValue`          | `UriValue`                       | `SimpleText`           | `.add_uri()`        | 
| `hasLinkTo`         | `:ClassName` or `Resource`       | `Searchbox`            | `.add_link()`       | 
| `hasRepresentation` | `:ClassName` or `Representation` | `Searchbox`            | `.add_link()`       | 
| `isPartOf`          | `:ClassName`                     | `Searchbox`            | `.add_link()`       | 
| `seqnum`            | `IntValue`                       | `Spinbox`/`SimpleText` | `.add_integer()`    | 

### Example: Adding Different Value Types

**From JSON property definition:**

```json
{
    "name": "testBoolean",
    "super": [
        "hasValue"
    ],
    "object": "BooleanValue",
    "labels": {
        "en": "Test Boolean"
    },
    "gui_element": "Checkbox"
}
```

**To xmllib:**

```python
# Look up the property type from JSON -> use .add_bool()
resource = resource.add_bool(
    prop_name=":testBoolean",  # From JSON property["name"]
    value=True  # From your data
)
```

**More examples:** → see Documentation: <https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/resource/>

## Cardinality Mapping

JSON cardinalities determine which xmllib method variant to use:

| JSON Cardinality | Meaning      | xmllib Method       | When to Use                  |
|------------------|--------------|---------------------|------------------------------|
| `1`              | Exactly one  | `.add_*()`          | Mandatory single value       |
| `0-1`            | Zero or one  | `.add_*_optional()` | Optional single value        |
| `1-n`            | One or more  | `.add_*_multiple()` | Mandatory, can have multiple |
| `0-n`            | Zero or more | `.add_*_multiple()` | Optional, can have multiple  |

### Example: Using Cardinality

**From JSON:**

```json
{
    "cardinalities": [
        {
            "propname": ":testBoolean",
            "cardinality": "0-1"
        },
        {
            "propname": ":testSimpleText",
            "cardinality": "0-n"
        },
        {
            "propname": ":testGeoname",
            "cardinality": "1-n"
        }
    ]
}
```

**To xmllib:**

```python
# 0-1: Optional single value
resource = resource.add_bool_optional(
    prop_name=":testBoolean",
    value=your_data.get("boolean_field")  # Can be None
)

# 0-n: Optional multiple values
if your_data.get("text_values"):
    resource = resource.add_simpletext_multiple(
        prop_name=":testSimpleText",
        values=your_data["text_values"]  # List of strings
    )

# 1-n: Mandatory multiple values
resource = resource.add_geoname_multiple(
    prop_name=":testGeoname",
    values=your_data["geoname_ids"]  # List must have at least one item
)
```

**Key Points:**

- `_optional()` methods check if value is empty and only add if not
- `_multiple()` methods take a list of values: `values=[...]` (note the plural)
- Regular methods take a single value: `value=...` (singular)
- Both `1-n` and `0-n` use `_multiple()` methods

## Working with Lists

Lists are controlled vocabularies defined in the JSON project. 
They provide predefined options for properties with `ListValue` as their object type.

**From JSON list definition:**

```json
{
    "lists": [
        {
            "name": "colors",
            "labels": {
                "en": "Color Options"
            },
            "nodes": [
                {
                    "name": "red",
                    "labels": {"en": "Red"}
                },
                {
                    "name": "green",
                    "labels": {"en": "Green"}
                },
                {
                    "name": "blue",
                    "labels": {"en": "Blue"}
                }
            ]
        }
    ]
}
```

**Property using this list:**

```json
{
    "name": "hasColor",
    "super": ["hasValue"],
    "object": "ListValue",
    "labels": {"en": "Color"},
    "gui_element": "List",
    "gui_attributes": {
        "hlist": "colors"
    }
}
```

**To xmllib:**

The xmllib provides a `ListLookup` class that translates list node names or labels to their IRI representations.

```python
# Create the list lookup (ask user which language to use)
list_lookup = xmllib.ListLookup.create_new(
    "project_json.json",
    language_of_label="en",  # Language for label matching
    default_ontology="daschland"
)

# Look up by node label
color_node = list_lookup.get_node_via_list_name(
    list_name="colors",
    node_label="Red"  # Label in the specified language (capitalisation is not relevant)
)

# Add to resource
resource = resource.add_list(
    prop_name=":hasColor",
    list_name="colors",
    value=color_node
)
```

**Key Points:**

- Always create the `ListLookup` once and pass it to all import functions
- Use `get_node_via_list_name()` to look up nodes by their label in the specified language
- The lookup returns a node name string that can be used in `add_list()` or `add_list_multiple()`
- When using `add_list()` or `add_list_multiple()`, you must provide both `list_name` and `value` parameters

**More details:** https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/general-functions/#xmllib.general_functions.ListLookup


## Working with Multiple Ontologies

When your project has multiple ontologies, properties may need prefixes.

**From JSON:**

```json
{
    "ontologies": [
        {
            "name": "onto",
            "properties": [
                {
                    "name": "testSimpleText",
                    ...
                }
            ]
        },
        {
            "name": "second-onto",
            "properties": [
                {
                    "name": "testBoolean",
                    ...
                }
            ],
            "resources": [
                {
                    "name": "SecondOntoClass",
                    "cardinalities": [
                        {
                            "propname": ":testBoolean",
                            "cardinality": "0-1"
                        },
                        {
                            "propname": "onto:testSimpleText",
                            "cardinality": "0-n"
                        }
                    ]
                }
            ]
        }
    ]
}
```

**Note:** In the example above:
- `:testBoolean` is a property from the same ontology (second-onto)
- `onto:testSimpleText` is a property from a different ontology (onto)

**To xmllib:**

```python
# Create root with first ontology as default
root = xmllib.XMLRoot.create_new(
    shortcode="0003",
    default_ontology="onto"  # First ontology
)

# Resource from second ontology
resource = xmllib.Resource.create_new(
    res_id="resource_1",
    restype="second-onto:SecondOntoClass",  # Full prefix for non-default
    label="Resource from second ontology"
)

# Property from same ontology (second-onto)
resource = resource.add_bool(
    prop_name=":testBoolean",  # Colon prefix (same as default)
    value=True
)

# Property from different ontology (onto)
resource = resource.add_simpletext(
    prop_name="onto:testSimpleText",  # Full ontology prefix
    value="Text value"
)
```

**Rules:**

- Default ontology properties: use `:propName`
- Other ontology properties: use `ontologyName:propName` as specified in JSON
- Resource types from non-default ontologies: use full prefix

## Resources with Files

Resources with file super classes can have multimedia files attached.

**From JSON:**

```json
{
    "name": "TestStillImageRepresentation",
    "super": "StillImageRepresentation",
    "labels": {
        "en": "Image Resource"
    }
}
```

**Available file super classes:**

- `StillImageRepresentation` - Images (JPEG, PNG, TIFF)
- `DocumentRepresentation` - PDFs, documents
- `AudioRepresentation` - Audio files
- `MovingImageRepresentation` - Videos
- `ArchiveRepresentation` - ZIP archives
- `TextRepresentation` - Text files

**To xmllib:**

see: https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/resource/#xmllib.Resource.add_file
and https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/resource/#xmllib.Resource.add_iiif_uri


## Special Cases

### isPartOf

Indicates that a resource is part of another resource (e.g., a page is part of a book, a chapter is part of a document).

**When to use seqnum with isPartOf:**
- If the child resources have a specific order (e.g., pages in a book), you **must** also use a `seqnum` property
- If the child resources have no inherent order (e.g., images attached to an article), `seqnum` is not required

**From JSON:**

```json
{
    "name": "testIsPartOf",
    "super": [
        "isPartOf"
    ],
    "object": ":TestStillImageRepresentation",
    "gui_element": "Searchbox"
}
```

**To xmllib:**

```python
resource = resource.add_link(
    prop_name=":testIsPartOf",
    value="parent_resource_id"  # res_id of the parent resource
)
```

**Important:** All link properties use `.add_link()` regardless of their super property.

### seqnum (Sequence Numbers)

Used to define the order of resources that are part of another resource.
Typically used **together with `isPartOf`** to establish sequence (e.g., page 1, page 2, page 3 of a book).

**Important:**
- `seqnum` values should be integers (1, 2, 3, ...)
- Each child resource of the same parent should have a unique sequence number
- Sequence numbers define the order for display and navigation in DSP-APP

**From JSON:**

```json
{
    "name": "testSeqnum",
    "super": [
        "seqnum"
    ],
    "object": "IntValue",
    "gui_element": "SimpleText"
}
```

**To xmllib:**

```python
# Page 1 of a book
page_1 = xmllib.Resource.create_new(
    res_id="page_1",
    restype=":PageResource",
    label="Page 1"
)
page_1 = page_1.add_link(prop_name=":isPartOf", value="book_1")
page_1 = page_1.add_integer(prop_name=":testSeqnum", value=1)

# Page 2 of the same book
page_2 = xmllib.Resource.create_new(
    res_id="page_2",
    restype=":PageResource",
    label="Page 2"
)
page_2 = page_2.add_link(prop_name=":isPartOf", value="book_1")
page_2 = page_2.add_integer(prop_name=":testSeqnum", value=2)
```

### Built-in Properties: isPartOf and seqnum

DSP has built-in `isPartOf` and `seqnum` properties in `knora-api`.
Your ontology can define sub-properties of these.

**From JSON:**

```json
{
    "cardinalities": [
        {
            "propname": "isPartOf",
            "cardinality": "0-n"
        },
        {
            "propname": "seqnum",
            "cardinality": "0-1"
        }
    ]
}
```

**Note:** Both `isPartOf` and `seqnum` are built-in properties with no prefix needed.

**To xmllib:**

```python
# Using built-in properties (no prefix needed in prop_name)
resource = resource.add_link(
    prop_name="isPartOf",  # No colon prefix!
    value="parent_id"
)
resource = resource.add_integer(
    prop_name="seqnum",  # No colon prefix!
    value=1
)
```

### Resources Inheriting from Other Resources

**From JSON:**

```json
{
    "resources": [
        {
            "name": "ResourceNoGuiOrder",
            "super": "Resource",
            "cardinalities": [
                {
                    "propname": ":testBoolean",
                    "cardinality": "0-1"
                }
            ]
        },
        {
            "name": "SubClassOfResourceNoGuiOrder",
            "super": ":ResourceNoGuiOrder",
            "cardinalities": [
                {
                    "propname": ":testSimpleText",
                    "cardinality": "0-n"
                }
            ]
        }
    ]
}
```

**Note:** `SubClassOfResourceNoGuiOrder` inherits from the custom class `ResourceNoGuiOrder` and will inherit all its cardinalities.

**To xmllib:**

```python
# Subclass inherits all cardinalities from parent
resource = xmllib.Resource.create_new(
    res_id="sub_resource_1",
    restype=":SubClassOfResourceNoGuiOrder",
    label="Subclass resource"
)

# Can use properties from parent class
resource = resource.add_bool_optional(
    prop_name=":testBoolean",
    value=True
)

# And properties from own class
resource = resource.add_simpletext(
    prop_name=":testSimpleText",
    value="Text value"
)
```
