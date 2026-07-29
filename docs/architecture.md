# Architecture

The project deliberately contains two separate pipelines. APRA masked aggregate reports support
Australian descriptive portfolio analytics. The public French freMTPL2 dataset supports
educational policy-level modelling. No row, feature, metric or model crosses between them.

## Overview

```mermaid
flowchart LR
    APRA["APRA aggregate pipeline"] --> APP["Unified Streamlit application"]
    FRENCH["French modelling pipeline"] --> APP
    QA["Testing, reconciliation and governance"] -.-> APRA
    QA -.-> FRENCH
```

The full diagrams are stored as Mermaid source files in this directory. Run
`python scripts/generate_diagrams.py` to render SVG files when Mermaid CLI is available.

