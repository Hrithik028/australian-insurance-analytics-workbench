# Architecture guide

This guide explains how data moves through the project, why the Australian and French modules stay
separate, how the application chooses data at runtime, and how the public deployment is assembled.

## 1. System context

```mermaid
flowchart TB
    REVIEWER["Reviewer / analyst"] --> UI["Streamlit analytical workbench"]

    subgraph AU["Australian descriptive analytics"]
        APRA["APRA masked aggregate reports"] --> AP["APRA ingestion and validation"]
        AP --> APS[("Eight separate curated report tables")]
        APS --> AOUT["Portfolio, claims, development, segment and quality views"]
    end

    subgraph FR["Educational policy-level modelling"]
        FDATA["Public freMTPL2 dataset"] --> FP["Validation and policy-safe feature pipeline"]
        FP --> FSTORE[("Curated policy and model tables")]
        FSTORE --> MODELS["Frequency and severity GLMs"]
        MODELS --> FOUT["Diagnostics, risk deciles and premium simulator"]
    end

    AOUT --> UI
    FOUT --> UI
    GOV["Tests, reconciliation, source lineage and limitations"] -.-> AP
    GOV -.-> FP
    GOV -.-> UI
    APRA -. "never joined" .- FDATA
```

The APRA reports provide Australian context at an aggregate grain. freMTPL2 provides policy-level
records suitable for an educational modelling demonstration. No feature, row, metric or model is
transferred between the two modules.

## 2. APRA data engineering flow

```mermaid
flowchart LR
    ZIP["Policy and claims ZIP archives"] --> SAFE["Path-safe extraction"]
    SAFE --> DISC["Workbook and worksheet discovery"]
    DISC --> MAP["Schema inspection and column mapping"]
    MAP --> CLEAN["Type-safe cleaning"]
    CLEAN --> FLAGS["Quality and lineage flags"]
    FLAGS --> TABLES[("Eight separate Parquet tables")]
    TABLES --> DB[("DuckDB analytical layer")]
    DB --> SQL["11 analytical SQL queries"]
    SQL --> VIEWS["APRA dashboard pages and reports"]
    REC["Source to Parquet to DuckDB reconciliation"] -.-> TABLES
    REC -.-> DB
```

State, occupation, excess and limit-of-indemnity reports are overlapping alternate cuts. They are
stored and analysed separately to prevent double counting.

## 3. French modelling flow

```mermaid
flowchart TB
    SRC["Pinned freMTPL2 source revision"] --> VERIFY["Checksum, schema and join validation"]
    VERIFY --> SPLIT["Policy-disjoint 60 / 20 / 20 split"]
    SPLIT --> FREQ["Frequency model: claim count with log exposure offset"]
    SPLIT --> SEV["Severity model: positive claims with Gamma log-link GLM"]
    FREQ --> FDIAG["Dispersion, deviance and decile calibration"]
    SEV --> SDIAG["Gamma deviance, MAE and decile calibration"]
    FREQ --> COST["Estimated technical claims cost"]
    SEV --> COST
    COST --> LOAD["Transparent expense, commission, risk, profit, tax and reinsurance loadings"]
    LOAD --> SIM["Educational premium simulator"]
    FDIAG --> APP["French dashboard pages"]
    SDIAG --> APP
    SIM --> APP
```

Policy ID is used only for validated joins and split membership. It is excluded from every model
formula.

## 4. Streamlit application structure

```mermaid
flowchart LR
    ENTRY["app/app.py"] --> NAV["Grouped Streamlit navigation"]
    NAV --> HOME["Recruiter landing page"]
    NAV --> APRAUI["Eight APRA pages"]
    NAV --> FRUI["Six French pages"]
    NAV --> GOVUI["Governance page"]

    HOME --> ACCESS["app/data.py cached access"]
    APRAUI --> ACCESS
    FRUI --> ACCESS
    GOVUI --> ACCESS

    ACCESS --> MODE{"INSURANCE_DATA_MODE"}
    MODE -->|"local"| FULL[("Full local processed data")]
    MODE -->|"demo"| DEMO[("Committed compact demo data")]
    MODE -->|"auto"| CHECK{"Full local table exists?"}
    CHECK -->|"yes"| FULL
    CHECK -->|"no"| DEMO
```

`auto` is the default. It gives analysts full fidelity after running the pipelines and makes a clean
GitHub checkout immediately usable with the compact public artifacts.

## 5. Public deployment architecture

```mermaid
flowchart LR
    DEV["Local verified project"] --> BUILD["scripts/build_demo_data.py"]
    BUILD --> DERIVED[("Compact derived Parquet and audit artifacts")]
    DEV --> CODE["Application, tests, SQL and documentation"]
    DERIVED --> GITHUB["Public GitHub repository"]
    CODE --> GITHUB
    GITHUB --> CLOUD["Streamlit Community Cloud"]
    CLOUD --> INSTALL["Install app/requirements.txt"]
    INSTALL --> RUN["Run app/app.py in demo mode fallback"]
    RUN --> PUBLIC["Public read-only dashboard"]

    RAW[("Raw archives, full processed data, DuckDB and models")] -. "excluded by .gitignore" .-> GITHUB
    SECRETS["No deployment secrets required"] -.-> CLOUD
```

Only compact derived artifacts are committed. Raw archives, full processed datasets, the local
DuckDB file and fitted model binaries remain outside Git.

## 6. Repository component map

```mermaid
flowchart TB
    APP["app/ — Streamlit UI and deployment requirements"]
    SRC["src/ — reusable ingestion, validation, metrics and modelling"]
    SCRIPTS["scripts/ — executable pipeline and report commands"]
    SQL["sql/ — analytical and reconciliation queries"]
    TESTS["tests/ — unit and configuration checks"]
    DEMO["demo_data/ — deployment-safe derived artifacts"]
    DOCS["docs/ and reports/ — architecture, methodology and verified evidence"]

    SCRIPTS --> SRC
    SCRIPTS --> DEMO
    APP --> SRC
    APP --> DEMO
    SQL --> DOCS
    TESTS -. validates .-> APP
    TESTS -. validates .-> SRC
    SRC --> DOCS
```

## Diagram sources

The original Mermaid sources are stored alongside this guide:

- [`architecture-overview.mmd`](architecture-overview.mmd)
- [`apra-data-flow.mmd`](apra-data-flow.mmd)
- [`french-model-pipeline.mmd`](french-model-pipeline.mmd)
- [`application-runtime.mmd`](application-runtime.mmd)
- [`deployment-architecture.mmd`](deployment-architecture.mmd)

Run `python scripts/generate_diagrams.py` to render SVG copies when Mermaid CLI is available.
