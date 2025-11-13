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
- **Start local DSP server**: `dsp-tools start-stack --no prune` spins up a local DSP server,
  for local testing of the JSON and the XML file.
- **Data Model Creation**: `dsp-tools create` establishes the data model from the JSON file on the DSP server.
- **Validation**: `dsp-tools validate-data` validates the XML data against the data model on the server.
- **Data Upload**: `dsp-tools xmlupload` populates the project with resources and metadata defined in the XML file.

## xmllib

The `xmllib` module is the public API library for programmatic creation of DSP XML files.
It provides a type-safe, validated approach to generating XML data that conforms to DSP (DaSCH Service Platform)
requirements.
Please carefully read the following documentations, they are crucial in order to understand the xmllib:

- Documentation of xmllib (see also the subpages): <https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/overview/>
- Example scripts - this is the entrypoint:
  <https://github.com/dasch-swiss/daschland-scripts/blob/main/src/xmllib/xmllib_main.py>
- Documentation of the JSON file format:
    - <https://docs.dasch.swiss/latest/DSP-TOOLS/data-model/json-project/overview/>
    - <https://docs.dasch.swiss/latest/DSP-TOOLS/data-model/json-project/ontologies/>
    - <https://docs.dasch.swiss/latest/DSP-TOOLS/data-model/json-project/caveats/>
- Documentation of the XML file format: <https://docs.dasch.swiss/latest/DSP-TOOLS/data-file/xml-data-file/>

If you cannot retrieve these documentations, alert me. Without reading these, there's no point in continuing.

## Broad Code Organisation

```
.
├── data
├── src
│     ├── utils
│     │     └── some_util.py  # here are functions that can be shared accross multiple import scripts
│     └── import-scripts
│            ├── main_import.py  # from here the individual functions are called from
│            └── import_<class_name>.py  # here is where the xmllib code lives
```

## Workflow

**Important Directive:**

- Never change the input data.
- Never "fix" the input data.
- This must be done manually by the user.


1. After reading the claude.md file
2. Analyse the data model and choose the first class to work on
    - Resource classes may link to other classes.
    - A link to another class means: A class has a cardinality of a property that has `hasLinkTo` or `isPartOf` as
      super-property.
    - Make an ordered list of classes: First the ones without links, then the ones that link to classes already in the
      list.
    - A class may only link to preceding classes.
3. Ask the user per class and per property (cardinality)
    - Where to I get the data from?
    - If it is a tabular format, what column name?
    - Is there cleaning necessary?
4. Create a new claude.md file where you put the plan for this first class. Write down all the answers and compile a
   detailed plan.
    - When writing a new class always include in claude.md see ## Python Code Set-Up
5. The xmllib saves warnings, i.e. if it finds problems with the input in this file: xmllib_warnings.csv
    - Some of the warnings there are simply information for example: These will be "Severity = INFO"
    - The important ones that will cause problems in the future are "Severity = WARNING"
    - If there are problems which will mean that the code cannot continue you will get "Severity = ERROR"
    - If you encounter WARNING or ERROR, then alert the user. You cannot continue alone.
6. Always when 1 resource class is finished
    - first check XSD schema compliancy with `dsp-tools xmlupload --validate-only <data.xml>`,
    - then start a local stack with `dsp-tools start-stack --no-prune`,
    - then create the project with the data model with `dsp-tools create <project.json>`,
    - then validate the XML with `dsp-tools validate-data <data.xml>`.
    - If everything is fine, proceed with the next resource class.

## Python Code Set-Up

If you have not created any classes before:

Create: `src/import-scripts/main.py`

```python

def main() -> None:
    # create the root element dsp-tools
    root = XMLRoot.create_new(shortcode="0854", default_ontology="daschland")

    # import all resources

    # write the root to a xml file
    root.write_file("data/output/data_<project-shortname>.xml")


if __name__=="__main__":
    main()
```

For each new class:

1. New file: `src/import-scripts/import_<class_name>.py`

```python
def main() -> list[Resource]:
    all_resources: list[Resource] = []
    ...

    return all_resources


if __name__=="__main__":
    main()
```

2. Add to `src/import-scripts/main.py`

```python
from src.import_scripts import import_ < class_name >


def main() -> None:
    # create the root element dsp-tools
    root = XMLRoot.create_new(shortcode="0854", default_ontology="daschland")

    # import all resources
    all_ < class_name > = import_ < class_name >.main()
    root.add_resource_multiple(all_ < class_name >)

    # write the root to a xml file
    root.write_file("data/output/data_<project-shortname>.xml")


if __name__=="__main__":
    main()
```

# Mapping from Data Model JSON to xmllib

This document provides comprehensive guidance on how to translate
a DSP project JSON definition into xmllib code for creating XML import files.

## Table of Contents

1. [Overview & Workflow](#overview--workflow)
2. [Setting Up the XMLRoot](#setting-up-the-xmlroot)
3. [Creating Resources](#creating-resources)
4. [Property-Type to xmllib Method Mapping](#property-type-to-xmllib-method-mapping)
5. [Cardinality Mapping](#cardinality-mapping)
6. [Working with Lists](#working-with-lists)
7. [Working with Multiple Ontologies](#working-with-multiple-ontologies)
8. [Link Properties](#link-properties)
9. [Resources with Files](#resources-with-files)
10. [Special Cases](#special-cases)
11. [Complete Example](#complete-example)
12. [Best Practices](#best-practices)

## Overview & Workflow

The general workflow for converting JSON project data to XML is:

1. **Read the JSON project file** to understand the data model
2. **Import xmllib** and create the XMLRoot with project shortcode
3. **For each resource in your data**:
    - Create a Resource instance with the appropriate restype
    - Add values to the resource based on the properties defined in cardinalities
    - Add the resource to the root
4. **Write the XML file**

```python
from dsp_tools import xmllib

# Step 1: Load and parse your project JSON
with open("project.json") as f:
    project_json = json.load(f)

# Step 2: Create XMLRoot
root = xmllib.XMLRoot.create_new(
    shortcode=project_json["project"]["shortcode"],
    default_ontology=project_json["project"]["ontologies"][0]["name"]
)

# Step 3: Create resources and add values (detailed below)

# Step 4: Write the file
root.write_file("data.xml")
```

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
Properties from other ontologies need the full prefix.

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

## Property-Type to xmllib Method Mapping

This table shows how JSON property definitions map to xmllib methods:

| JSON `super`        | JSON `object`                    | JSON `gui_element`     | xmllib Method       | Example Value                    |
|---------------------|----------------------------------|------------------------|---------------------|----------------------------------|
| `hasValue`          | `BooleanValue`                   | `Checkbox`             | `.add_bool()`       | `True` or `False`                |
| `hasColor`          | `ColorValue`                     | `Colorpicker`          | `.add_color()`      | `"#FF0000"`                      |
| `hasValue`          | `DateValue`                      | `Date`                 | `.add_date()`       | `"GREGORIAN:CE:2024-01-15"`      |
| `hasValue`          | `DecimalValue`                   | `Spinbox`/`SimpleText` | `.add_decimal()`    | `3.14`                           |
| `hasValue`          | `GeonameValue`                   | `Geonames`             | `.add_geoname()`    | `"2661604"` (geonames.org ID)    |
| `hasValue`          | `IntValue`                       | `Spinbox`/`SimpleText` | `.add_integer()`    | `42`                             |
| `hasValue`          | `ListValue`                      | `List`                 | `.add_list()`       | `"node_name"`                    |
| `hasValue`          | `TextValue`                      | `SimpleText`           | `.add_simpletext()` | `"Plain text"`                   |
| `hasValue`          | `TextValue`                      | `Textarea`             | `.add_textarea()`   | `"Multi\nline\ntext"`            |
| `hasValue`          | `TextValue`                      | `Richtext`             | `.add_richtext()`   | `"<p>Formatted text</p>"`        |
| `hasComment`        | `TextValue`                      | `Richtext`             | `.add_richtext()`   | `"<p>Comment text</p>"`          |
| `hasValue`          | `TimeValue`                      | `TimeStamp`            | `.add_time()`       | `"2019-10-23T13:45:12.01-14:00"` |
| `hasValue`          | `UriValue`                       | `SimpleText`           | `.add_uri()`        | `"https://example.com"`          |
| `hasLinkTo`         | `:ClassName` or `Resource`       | `Searchbox`            | `.add_link()`       | `"target_resource_id"`           |
| `hasRepresentation` | `:ClassName` or `Representation` | `Searchbox`            | `.add_link()`       | `"image_resource_id"`            |
| `isPartOf`          | `:ClassName`                     | `Searchbox`            | `.add_link()`       | `"target_resource_id"`           |
| `seqnum`            | `IntValue`                       | `Spinbox`/`SimpleText` | `.add_integer()`    | `1`                              |

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

**More examples:** -> see Documentation: <https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/resource/>

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

**From JSON:**

```json
{
    "project": {
        "lists": [
            {
                "name": "firstList",
                "labels": {
                    "en": "List 1"
                },
                "nodes": [
                    {
                        "name": "l1_n1",
                        "labels": {
                            "en": "Node 1"
                        }
                    },
                    {
                        "name": "l1_n2",
                        "labels": {
                            "en": "Node 2"
                        }
                    }
                ]
            }
        ]
    },
    "ontologies": [
        {
            "properties": [
                {
                    "name": "testListProp",
                    "super": [
                        "hasValue"
                    ],
                    "object": "ListValue",
                    "gui_element": "List",
                    "gui_attributes": {
                        "hlist": "firstList"
                        #
                        References
                        the
                        list
                    }
                }
            ]
        }
    ]
}
```

**To xmllib:**

```python
# Method 1: Add single list value
resource = resource.add_list(
    prop_name=":testListProp",
    list_name="firstList",  # From gui_attributes["hlist"]
    value="l1_n1"  # Node name from your data
)

# Method 2: Add multiple list values
resource = resource.add_list_multiple(
    prop_name=":testListProp",
    list_name="firstList",
    values=["l1_n1", "l1_n2"]  # Multiple node names
)

# Method 3: Optional list value
resource = resource.add_list_optional(
    prop_name=":testListProp",
    list_name="firstList",
    value=your_data.get("list_selection")  # Can be None
)
```

**Important:**

- `list_name` comes from JSON `gui_attributes["hlist"]`
- `value` must be a node `name` (e.g., `"l1_n1"`), not the label
- For nested nodes, use the node name at any level (e.g., `"l1_n1_1"`)

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
                            #
                            Property
                            from
                            same
                            ontology
                            "cardinality": "0-1"
                        },
                        {
                            "propname": "onto:testSimpleText",
                            #
                            Property
                            from
                            other
                            ontology
                            "cardinality": "0-n"
                        }
                    ]
                }
            ]
        }
    ]
}
```

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

## Link Properties

Link properties connect resources to each other.

### hasLinkTo

Links to any resource or specific resource class.

**From JSON:**

```json
{
    "name": "testHasLinkTo",
    "super": [
        "hasLinkTo"
    ],
    "object": "Resource",
    // or ":SpecificClassName"
    "gui_element": "Searchbox"
}
```

**To xmllib:**

```python
resource = resource.add_link(
    prop_name=":testHasLinkTo",
    value="target_resource_id"  # res_id of the target resource
)

# Multiple links
resource = resource.add_link_multiple(
    prop_name=":testHasLinkTo",
    values=["resource_1", "resource_2", "resource_3"]
)
```

### hasRepresentation

Links to a resource with a file (image, video, etc.).

**From JSON:**

```json
{
    "name": "testHasRepresentation",
    "super": [
        "hasRepresentation"
    ],
    "object": "Representation",
    "gui_element": "Searchbox"
}
```

**To xmllib:**

```python
resource = resource.add_link(
    prop_name=":testHasRepresentation",
    value="image_resource_id"  # res_id of a representation resource
)
```

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

```python
# Create resource with file super class
image_resource = xmllib.Resource.create_new(
    res_id="image_1",
    restype=":TestStillImageRepresentation",
    label="Photo of a cat"
)

# Add file with required metadata
image_resource = image_resource.add_file(
    filename="images/cat.jpg",  # Path relative to XML file
    license=xmllib.LicenseRecommended.CC.BY_4_0,
    copyright_holder="John Doe",
    authorship=["Jane Smith", "John Doe"]
)

# Add properties to the image resource
image_resource = image_resource.add_simpletext(
    prop_name=":hasDescription",
    value="A cute cat photo"
)

root = root.add_resource(image_resource)
```

**Alternative: IIIF-URI**

Instead of uploading a file, you can reference an external IIIF image:

```python
image_resource = image_resource.add_iiif_uri(
    iiif_uri="https://iiif.example.org/image/abc123/full/max/0/default.jpg",
    license=xmllib.LicenseRecommended.CC.BY_4_0,
    copyright_holder="Museum XYZ",
    authorship=["Photographer Name"]
)
```

## Special Cases

### isPartOf

Indicates that a resource is part of another resource.
It requires a seqnum property as well

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
Requires isPartOf

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
            // Built-in, no prefix
            "cardinality": "0-n"
        },
        {
            "propname": "seqnum",
            // Built-in, no prefix
            "cardinality": "0-1"
        }
    ]
}
```

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
            // Inherits from custom class
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

## Complete Example

Here's a complete script that reads a JSON project and creates XML data:

```python
import json
from dsp_tools import xmllib

# 1. Load project JSON
with open("testdata/json-project/create-project-0003.json") as f:
    project_json = json.load(f)

# 2. Create XMLRoot
shortcode = project_json["project"]["shortcode"]
default_onto = project_json["project"]["ontologies"][0]["name"]

root = xmllib.XMLRoot.create_new(
    shortcode=shortcode,
    default_ontology=default_onto
)

# 3. Get resource class definition
onto = project_json["project"]["ontologies"][0]
resource_class = next(r for r in onto["resources"] if r["name"]=="ClassWithEverything")

# 4. Create a resource with data
resource = xmllib.Resource.create_new(
    res_id="resource_with_everything_1",
    restype=":" + resource_class["name"],
    label="Example resource with all property types"
)

# 5. Add values based on cardinalities
# Find the cardinality for each property and add appropriate values

# Boolean (0-1 cardinality)
resource = resource.add_bool_optional(
    prop_name=":testBoolean",
    value=True
)

# Color (0-n cardinality)
resource = resource.add_color_multiple(
    prop_name=":testColor",
    values=["#FF0000", "#00FF00", "#0000FF"]
)

# Date (0-n cardinality)
date_value = xmllib.value_converters.reformat_date(
    date="15.01.2024",
    date_precision_separator=".",
    date_range_separator="-",
    date_format=xmllib.DateFormat.DD_MM_YYYY
)
resource = resource.add_date_multiple(
    prop_name=":testDate",
    values=[date_value]
)

# Integer (0-n cardinality)
resource = resource.add_integer_multiple(
    prop_name=":testIntegerSpinbox",
    values=[1, 2, 3]
)

# List (0-n cardinality)
# Find list name from property definition
list_prop = next(p for p in onto["properties"] if p["name"]=="testListProp")
list_name = list_prop["gui_attributes"]["hlist"]

resource = resource.add_list_multiple(
    prop_name=":testListProp",
    list_name=list_name,
    values=["l1_n1", "l1_n2"]
)

# SimpleText (0-n cardinality)
resource = resource.add_simpletext_multiple(
    prop_name=":testSimpleText",
    values=["First text", "Second text"]
)

# Richtext (0-n cardinality)
resource = resource.add_richtext(
    prop_name=":testRichtext",
    value="<p>This is <strong>formatted</strong> text.</p>"
)

# URI (0-n cardinality)
resource = resource.add_uri(
    prop_name=":testUriValue",
    value="https://www.example.com"
)

# Link (0-n cardinality) - need another resource first
linked_resource = xmllib.Resource.create_new(
    res_id="linked_resource_1",
    restype=":ClassMixedCard",
    label="Linked resource"
)
# Add mandatory property for ClassMixedCard (cardinality 1)
linked_resource = linked_resource.add_bool(
    prop_name=":testBoolean",
    value=False
)
# Add mandatory multiple property (cardinality 1-n)
linked_resource = linked_resource.add_geoname_multiple(
    prop_name=":testGeoname",
    values=["2661604"]  # At least one required
)
root = root.add_resource(linked_resource)

# Now add the link
resource = resource.add_link(
    prop_name=":testHasLinkTo",
    value="linked_resource_1"
)

# 6. Add resource to root
root = root.add_resource(resource)

# 7. Create a resource with a file
image_resource = xmllib.Resource.create_new(
    res_id="image_1",
    restype=":TestStillImageRepresentation",
    label="Example image"
)
image_resource = image_resource.add_file(
    filename="images/example.jpg",
    license=xmllib.LicenseRecommended.CC.BY_4_0,
    copyright_holder="Jane Doe",
    authorship=["Jane Doe"]
)
root = root.add_resource(image_resource)

# 8. Write XML file
root.write_file("output_data.xml")
print("XML file created successfully!")
```

## Best Practices

### 1. Data Validation

Always validate and clean your data before adding it to resources:

```python
from dsp_tools import xmllib

# Clean whitespace
label = xmllib.clean_whitespaces_from_string(raw_label)

# Make IDs XSD-compatible
res_id = xmllib.make_xsd_compatible_id(raw_id)

# Check if value is not empty
if xmllib.is_nonempty_value(value):
    resource = resource.add_simpletext(prop_name=":prop", value=value)
```

### 2. Handle Missing Data

Use optional methods for properties that might not have data:

```python
# Instead of checking manually
if data.get("optional_field"):
    resource = resource.add_simpletext(
        prop_name=":optionalProp",
        value=data["optional_field"]
    )

# Use the _optional variant
resource = resource.add_simpletext_optional(
    prop_name=":optionalProp",
    value=data.get("optional_field")
)
```

### 3. Process Data in Batches

When converting tabular data (CSV, Excel) to XML:

```python
import pandas as pd
from dsp_tools import xmllib

# Load data
df = pd.read_csv("data.csv")

# Create root
root = xmllib.XMLRoot.create_new(shortcode="0003", default_ontology="onto")

# Process each row
for idx, row in df.iterrows():
    resource = xmllib.Resource.create_new(
        res_id=xmllib.make_xsd_compatible_id(row["id"]),
        restype=":ResourceType",
        label=xmllib.clean_whitespaces_from_string(row["title"])
    )

    # Add values from columns
    resource = resource.add_simpletext_optional(
        prop_name=":hasName",
        value=row.get("name")
    )

    resource = resource.add_integer_optional(
        prop_name=":hasAge",
        value=row.get("age")
    )

    root = root.add_resource(resource)

root.write_file("output.xml")
```

### 4. Use Helper Functions for Dates

Always use the date formatting helper:

```python
# DON'T do manual date formatting
# resource.add_date(prop_name=":date", value="2024-01-15")  # Wrong format!

# DO use the helper function
formatted_date = xmllib.value_converters.reformat_date(
    date="15.01.2024",
    date_precision_separator=".",
    date_range_separator="-",
    date_format=xmllib.DateFormat.DD_MM_YYYY
)
resource = resource.add_date(prop_name=":date", value=formatted_date)
```

### 5. Keep Track of List Names

Store the mapping of properties to list names:

```python
# Build a lookup dictionary from JSON
property_to_list = {}
for prop in onto["properties"]:
    if prop.get("gui_attributes", {}).get("hlist"):
        property_to_list[prop["name"]] = prop["gui_attributes"]["hlist"]

# Use it when adding list values
resource = resource.add_list(
    prop_name=":testListProp",
    list_name=property_to_list["testListProp"],
    value=node_name
)
```

### 6. Comments and Permissions

Add comments and custom permissions when needed:

```python
# Add a comment to a value
resource = resource.add_simpletext(
    prop_name=":hasRemark",
    value="Some text",
    comment="This comment explains the text value"
)

# Set custom permissions for sensitive data
resource = resource.add_simpletext(
    prop_name=":confidentialInfo",
    value="Sensitive information",
    permissions=xmllib.Permissions.PRIVATE
)
```

### 8. Organize Your Code

Structure your conversion script clearly:

```python
# 1. Configuration and setup
def load_project_json(filepath):
    """Load and return project JSON"""
    pass


# 2. Helper functions
def get_property_list_name(property_name, onto):
    """Get list name for a property"""
    pass


def create_resource_from_row(row, resource_class):
    """Create a resource from a data row"""
    pass


# 3. Main conversion
def main():
    # Load JSON
    project_json = load_project_json("project.json")

    # Setup root
    root = setup_root(project_json)

    # Process data
    for data_row in load_data():
        resource = create_resource_from_row(data_row, resource_class)
        root = root.add_resource(resource)

    # Write output
    root.write_file("output.xml")


if __name__=="__main__":
    main()
```

### 9. Reference the JSON Structure

Keep your project JSON accessible while writing the conversion script:

```python
"""
This script converts data to XML based on:
- JSON project: testdata/json-project/create-project-0003.json
- Ontology: "onto"
- Resource class: "ClassWithEverything"

Cardinalities reference:
- :testBoolean: 0-1 (optional single)
- :testColor: 0-n (optional multiple)
- :testListProp: 0-n (optional multiple, list: "firstList")
...
"""
```
