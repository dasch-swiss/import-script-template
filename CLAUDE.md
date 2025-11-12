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
It provides a type-safe, validated approach to generating XML data that conforms to DSP (DaSCH Service Platform) requirements.
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

## Steps how to write the import scripts

- Analyse the data model in the JSON file.
- Resource classes may link to other classes.
  A link to another class means: A class has a cardinality of a property that has `hasLinkTo` or `isPartOf` as super-property.
  Make an ordered list of classes: First the ones without links, then the ones that link to classes already in the list.
  A class may only link to preceding classes.
- Start with the first class in the list. Create a python file that creates the resources of only that class.
- Always when 1 resource class is finished,
  - first check XSD schema compliancy with `dsp-tools xmlupload --validate-only <data.xml>`,
  - then start a local stack with `dsp-tools start-stack --no-prune`,
  - then create the project with the data model with `dsp-tools create <project.json>`,
  - then validate the XML with `dsp-tools validate-data <data.xml>`.
  - If everything is fine, proceed with the next resource class.
- All python scripts should append to the same XML file.
- The types defined in the JSON file are crucial:
  - If a resource is e.g. a `AudioRepresentation`, there must be exactly 1 mp3 file attached to it, no other file formats
  - If a property's `object` is `IntValue`, but in the customer data you encounter `ca. 6`,
    this is a type mismatch which must be handled by me.
  - If you encounter type mismatches, create a file `datatype_mismatches.csv`
    which lists the name of the excel file, the respective cell, the expected data type, and the actual value.
  - Don't be flexible in this regard - this must be followed pedantically!
