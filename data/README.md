# Data Generation

This directory contains Python scripts to generate tax reform impact data for the OBBBA Scatter visualization.

## Quick Start

From the project root directory:

```bash
make data
```

This will generate all data files and copy them to the `/static` directory.

## Requirements

- Python 3.8+
- Required packages: `numpy pandas policyengine_us`

Install with:
```bash
pip install numpy pandas policyengine_us
```

## Scripts

- `generate_data.py` - Main script that generates both formats
- `analysis.py` - Original wide format analysis functions
- `analysis_optimized.py` - Optimized format analysis functions
- `reforms.py` - Tax reform definitions

## Output Files

The script generates 6 files:

### Optimized Format (smaller, faster loading)
- `households_tcja_expiration.csv` - Core household data for TCJA expiration scenario
- `provisions_tcja_expiration.csv` - Non-zero provision impacts for TCJA expiration
- `households_tcja_extension.csv` - Core household data for TCJA extension scenario
- `provisions_tcja_extension.csv` - Non-zero provision impacts for TCJA extension

### Original Format (backward compatibility)
- `household_tax_income_changes_current_law_baseline.csv` - Wide format for TCJA expiration
- `household_tax_income_changes_tcja_baseline.csv` - Wide format for TCJA extension

## Data Format

The optimized format splits the data into two files per scenario:

1. **Households file**: Contains demographic data and total impacts
   - Household ID, state, weights
   - Income metrics
   - Total tax/benefit changes
   - Family composition

2. **Provisions file**: Contains non-zero provision impacts in long format
   - Household ID
   - Provision name
   - Net income change
   - Tax change
   - Benefit change

This reduces file size by ~70-80% by eliminating zero values and using a more efficient structure.