# CLAUDE.md - import scripts

This file provides guidance to Claude Code when writing import scripts using the `xmllib` module of dsp-tools.

## What are import scripts?

TODO: describe the big picture

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
Getting started documentation: <https://docs.dasch.swiss/latest/DSP-TOOLS/xmllib-docs/overview/>
Example script: <https://github.com/dasch-swiss/daschland-scripts/blob/main/src/xmllib/xmllib_main.py>
