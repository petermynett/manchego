# Environment Setup

## Dependencies

Start with core requirements, add as needed:

### Core Requirements
- **Python**: 3.12+
- **CLI Framework**: typer (for CLI commands)
- **OpenAI**: openai client (for receipt parsing)
- **Data Processing**: pandas (for CSV/data manipulation)
- **Jupyter**: JupyterLab for visualization and analysis
- **Google APIs**: google-api-python-client, google-auth (for Sheets integration)
- **Testing**: pytest + pytest plugins

### Conda Environment

```yaml
name: manchego
channels:
  - conda-forge
dependencies:
  - python=3.12
  - typer>=0.12
  - pandas
  - jupyter
  - jupyterlab
  - pytest
  - pip
  - pip:
    - openai>=1.40,<2
    - google-api-python-client>=2.0
    - google-auth>=2.0
```

### Environment File Location

Create: `env/environment.yml`

### Migration Steps (Before Setup)

If you have an existing `manchego` environment and project folder:

1. **Rename existing conda environment**:
   ```bash
   conda rename -n manchego manchego-v1
   ```

2. **Rename existing project folder** (from parent directory):
   ```bash
   # From parent directory of manchego folder
   mv manchego manchego-v1
   ```

This frees up the names `manchego` for both the new environment and new project folder.

### Setup Steps

1. Create new conda environment (with name `manchego`):
   ```bash
   mamba env create -f env/environment.yml
   conda activate manchego
   ```

   The environment.yml already specifies `name: manchego`, so it will create with the correct name.

3. Install package in development mode:
   ```bash
   pip install -e .
   ```

4. Verify installation:
   ```bash
   manchego --help
   pytest tests/ -v
   ```

### Adding Dependencies

**CRITICAL**: Always check before using pip. Pip should never be used without specific authorization.

When you need a new library:
1. Check if it's available on conda-forge first
2. Run `mamba install -c conda-forge --dry-run <package>` to check conflicts
3. If conda-forge has it, add to environment.yml and update: `mamba env update -f env/environment.yml`
4. If pip is required, **ask for authorization first**, then add to pip section of environment.yml

### Environment Variables

Set in shell or `.env` file:
- `MANCHEGO_DB_MODE`: `dev`, `stage`, or `prod` (default: `dev`)
- `OPENAI_API_KEY`: For receipt parsing
- Google service account JSON: `.secrets/google/service_account.json`

