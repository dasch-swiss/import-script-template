# CLAUDE.md - import scripts

This file provides guidance to Claude Code when writing import scripts using the `xmllib` module of dsp-tools.

## What are import scripts?

### Big Picture

DSP-TOOLS is the command-line interface for the DSP (DaSCH Service Platform).
DSP is a VRE (Virtual Research Environment) for research data from the (Digital) Humanities.
When researchers deliver their data to us (DaSCH),
we write Python scripts (using the `xmllib` module of dsp-tools) to transform their data into our DSP XML format.

This project heavily relies on DSP-TOOLS for data model creation and upload workflows.


### Key DSP-TOOLS Commands Used

1. **Create JSON project definition**: `dsp-tools excel2json` converts Excel files into a JSON file.
  This is a pure restructuring, the information stays the same.
2. **Data Model Creation**: `dsp-tools create` establishes the data model from the JSON file on the DSP server.
3. **Validation**: `dsp-tools validate-data` validates the XML data against the data model on the server.
4. **Data Upload**: `dsp-tools xmlupload` populates the project with resources and metadata defined in the XML file.



- Always use the type defined in the data model, which is a .json file
- Leverage dataclass models for structured data
- Use validation functions before creating values
- If values do not comply with the data type, create a file `datatype_mismatches.csv`
  which lists the name of the excel file, the respective cell, the expected data type, and the actual value.

### Steps

- Analyse the data model first, it is a .json file
- Proceed always one resource class only, when it is tested and can be uploaded, proceed to the next
- Always when 1 resource class is finished,
  first check XSD schema compliancy with `dsp-tools xmlupload --validate-only <data.xml>`,
  then start a local stack with `dsp-tools start-stack --no-prune`,
  then create the project with the data model with `dsp-tools create <project.json>`,
  then validate the XML with `dsp-tools validate-data <data.xml>`.
  If everything is fine, proceed with the next resource class.
- choose those resource classes first that have no links to other resource classes (no linkTo property)
  and are not part of another resource class (no isPartOf property)


## xmllib

The `xmllib` module is the public API library for programmatic creation of DSP XML files.
It provides a type-safe, validated approach to generating XML data that conforms to DSP (DaSCH Service Platform) requirements.
Please carefully read the following resources, they are crucial in order to understand the xmllib:

- Documentation (see also the subpages): <https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/overview/>
- Example scripts - this is the entrypoint:
  <https://github.com/dasch-swiss/daschland-scripts/blob/main/src/xmllib/xmllib_main.py>
