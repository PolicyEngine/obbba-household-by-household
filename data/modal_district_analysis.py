"""
Modal script for parallel district-level OBBBA analysis.
Runs all states in parallel, each container handles BOTH baselines sequentially.

Usage:
    modal run modal_district_analysis.py
    modal run modal_district_analysis.py --states "AL,AK,AZ"
"""

import modal

app = modal.App("obbba-district-analysis")

# Image with PolicyEngine pinned for reproducible district-level analysis.
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install(
        "policyengine[us]==4.4.4",
        "pandas",
        "numpy",
    )
    .add_local_python_source("reforms")
    .add_local_python_source("obbba_reforms")
    .add_local_python_source("district_analysis")
)

# All US states and DC
ALL_STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "DC", "FL",
    "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME",
    "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH",
    "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
    "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
]

# Modal volume for saving intermediate results
volume = modal.Volume.from_name("district-analysis-results", create_if_missing=True)


def run_single_baseline(state_code: str, baseline_type: str, year: int = 2026):
    """Run analysis for a single state and single baseline. Returns DataFrame."""
    import pandas as pd
    import numpy as np
    from policyengine_us import Microsimulation
    from reforms import obbba_reversal_reform, tcja_reform
    from obbba_reforms import get_obbba_provisions
    from district_analysis import fix_at_large_geoid, get_state_dataset_path

    dataset_path = get_state_dataset_path(state_code)
    reforms = get_obbba_provisions()

    # Set baseline based on type
    if baseline_type == "tcja-extension":
        baseline_reform = (obbba_reversal_reform(), tcja_reform())
    else:  # tcja-expiration
        baseline_reform = obbba_reversal_reform()

    # Calculate baseline values
    print(f"  [{state_code}] [{baseline_type}] Calculating baseline...")
    baseline = Microsimulation(reform=baseline_reform, dataset=dataset_path)

    # Get household-level baseline values
    baseline_income_tax = baseline.calculate("income_tax", map_to="household", period=year).values
    baseline_state_income_tax = baseline.calculate("state_income_tax", map_to="household", period=year).values
    baseline_net_income = baseline.calculate("household_net_income_including_health_benefits", map_to="household", period=year).values
    baseline_benefits = baseline.calculate("household_benefits", map_to="household", period=year).values
    baseline_medicaid = baseline.calculate("medicaid", map_to="household", period=year).values
    baseline_aca_ptc = baseline.calculate("aca_ptc", map_to="household", period=year).values
    baseline_chip = baseline.calculate("chip", map_to="household", period=year).values
    baseline_total_benefits = baseline_benefits + baseline_medicaid + baseline_aca_ptc + baseline_chip

    # Get household characteristics
    household_id = baseline.calculate("household_id", map_to="household", period=year).values
    state = baseline.calculate("state_code", map_to="household", period=year).values
    congressional_district = baseline.calculate("congressional_district_geoid", map_to="household", period=year).values
    household_weight = baseline.calculate("household_weight", map_to="household", period=year).values
    household_size = baseline.calculate("household_size", map_to="household", period=year).values
    employment_income = baseline.calculate("irs_employment_income", map_to="household", period=year).values
    agi = baseline.calculate("adjusted_gross_income", map_to="household", period=year).values
    num_dependents = baseline.calculate("tax_unit_dependents", map_to="household", period=year).values

    # SSN data
    ssn_card_type = baseline.calculate("ssn_card_type", map_to="person", period=year).values
    person_household_id = baseline.calculate("household_id", map_to="person", period=year).values

    person_df = pd.DataFrame({"household_id": person_household_id, "ssn_card_type": ssn_card_type})
    ssn_valid = person_df[person_df["ssn_card_type"].isin(["CITIZEN", "NON_CITIZEN_VALID_EAD"])].groupby("household_id").size()
    ssn_invalid = person_df[person_df["ssn_card_type"].isin(["OTHER_NON_CITIZEN", "NONE"])].groupby("household_id").size()
    ssn_valid_count = ssn_valid.reindex(household_id, fill_value=0).values
    ssn_invalid_count = ssn_invalid.reindex(household_id, fill_value=0).values

    # Fix at-large GEOIDs
    congressional_district_fixed = np.array([
        fix_at_large_geoid(int(geoid), sc) for geoid, sc in zip(congressional_district, state)
    ])

    # Initialize results
    results = {
        "Household ID": household_id,
        "State": state,
        "Congressional District": congressional_district_fixed,
        "Household Weight": household_weight,
        "Household Size": household_size,
        "Number of Dependents": num_dependents,
        "Employment Income": employment_income,
        "Adjusted Gross Income": agi,
        "Num with Valid SSN": ssn_valid_count,
        "Num without Valid SSN": ssn_invalid_count,
        "Baseline Federal Tax Liability": baseline_income_tax,
        "Baseline State Tax Liability": baseline_state_income_tax,
        "Baseline Net Income": baseline_net_income,
        "Baseline Benefits": baseline_benefits,
        "Baseline Medicaid": baseline_medicaid,
        "Baseline ACA PTC": baseline_aca_ptc,
        "Baseline CHIP": baseline_chip,
        "Baseline Total Benefits": baseline_total_benefits,
    }

    # Track cumulative values
    cumulative_reform = baseline_reform
    previous_income_tax = baseline_income_tax.copy()
    previous_state_income_tax = baseline_state_income_tax.copy()
    previous_net_income = baseline_net_income.copy()
    previous_total_benefits = baseline_total_benefits.copy()

    # Apply each reform sequentially
    for i, (reform_name, reform) in enumerate(reforms.items()):
        print(f"  [{state_code}] [{baseline_type}] Processing {reform_name} ({i+1}/{len(reforms)})...")

        cumulative_reform = (cumulative_reform, reform)
        reformed = Microsimulation(reform=cumulative_reform, dataset=dataset_path)

        reformed_income_tax = reformed.calculate("income_tax", map_to="household", period=year).values
        reformed_state_income_tax = reformed.calculate("state_income_tax", map_to="household", period=year).values
        reformed_net_income = reformed.calculate("household_net_income_including_health_benefits", map_to="household", period=year).values
        reformed_benefits = reformed.calculate("household_benefits", map_to="household", period=year).values
        reformed_medicaid = reformed.calculate("medicaid", map_to="household", period=year).values
        reformed_aca_ptc = reformed.calculate("aca_ptc", map_to="household", period=year).values
        reformed_chip = reformed.calculate("chip", map_to="household", period=year).values
        reformed_total_benefits = reformed_benefits + reformed_medicaid + reformed_aca_ptc + reformed_chip

        # Incremental changes
        results[f"Change in federal tax after {reform_name}"] = reformed_income_tax - previous_income_tax
        results[f"Change in state tax after {reform_name}"] = reformed_state_income_tax - previous_state_income_tax
        results[f"Change in net income after {reform_name}"] = reformed_net_income - previous_net_income
        results[f"Change in benefits after {reform_name}"] = reformed_total_benefits - previous_total_benefits

        previous_income_tax = reformed_income_tax.copy()
        previous_state_income_tax = reformed_state_income_tax.copy()
        previous_net_income = reformed_net_income.copy()
        previous_total_benefits = reformed_total_benefits.copy()

    # Final totals
    results["Final Federal Tax Liability"] = previous_income_tax
    results["Final State Tax Liability"] = previous_state_income_tax
    results["Final Net Income"] = previous_net_income
    results["Final Total Benefits"] = previous_total_benefits
    results["Total change in federal tax"] = previous_income_tax - baseline_income_tax
    results["Total change in state tax"] = previous_state_income_tax - baseline_state_income_tax
    results["Total change in net income"] = previous_net_income - baseline_net_income
    results["Total change in benefits"] = previous_total_benefits - baseline_total_benefits

    # Percentage changes
    pct_tax_change = np.zeros_like(baseline_income_tax)
    mask = baseline_income_tax != 0
    pct_tax_change[mask] = (results["Total change in federal tax"][mask] / np.abs(baseline_income_tax[mask])) * 100
    results["Percentage change in federal tax"] = pct_tax_change

    pct_state_tax_change = np.zeros_like(baseline_state_income_tax)
    mask = baseline_state_income_tax != 0
    pct_state_tax_change[mask] = (results["Total change in state tax"][mask] / np.abs(baseline_state_income_tax[mask])) * 100
    results["Percentage change in state tax"] = pct_state_tax_change

    pct_net_income_change = np.zeros_like(baseline_net_income)
    mask = baseline_net_income != 0
    pct_net_income_change[mask] = (results["Total change in net income"][mask] / np.abs(baseline_net_income[mask])) * 100
    results["Percentage change in net income"] = pct_net_income_change

    pct_benefits_change = np.zeros_like(baseline_total_benefits)
    mask = baseline_total_benefits != 0
    pct_benefits_change[mask] = (results["Total change in benefits"][mask] / np.abs(baseline_total_benefits[mask])) * 100
    results["Percentage change in benefits"] = pct_benefits_change

    results["State Code"] = [state_code] * len(household_id)

    # Convert numpy arrays to lists and create DataFrame
    df = pd.DataFrame({k: v.tolist() if hasattr(v, 'tolist') else v for k, v in results.items()})
    return df


@app.function(
    image=image,
    timeout=7200,  # 2 hours - running both baselines
    memory=8192,
    volumes={"/results": volume},
)
def analyze_state_both_baselines(state_code: str, year: int = 2026) -> dict:
    """
    Analyze a single state for BOTH baselines sequentially.
    Saves each result to volume immediately.
    Returns dict with status and paths or error info.
    """
    import traceback

    print(f"Starting analysis for {state_code} (both baselines)...")

    saved_paths = []

    try:
        for baseline_type in ["tcja-extension", "tcja-expiration"]:
            print(f"\n  [{state_code}] === Starting {baseline_type} ===")

            df = run_single_baseline(state_code, baseline_type, year)

            # Save to volume immediately
            output_path = f"/results/{baseline_type}_{state_code}.csv"
            df.to_csv(output_path, index=False)
            volume.commit()

            print(f"  [{state_code}] [{baseline_type}] Saved {len(df):,} households to {output_path}")
            saved_paths.append(output_path)

        print(f"\n  [{state_code}] DONE - both baselines complete!")
        return {"status": "success", "state": state_code, "paths": saved_paths}

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        print(f"\n  [{state_code}] FAILED: {error_msg}")
        print(traceback.format_exc())
        return {"status": "failed", "state": state_code, "error": error_msg, "paths": saved_paths}


@app.local_entrypoint()
def main(states: str = None):
    """
    Run district analysis for all states in parallel.
    Each state runs BOTH baselines sequentially in one container.

    Args:
        states: Comma-separated list of state codes (optional, defaults to all)
    """
    # Parse states argument
    if states:
        state_list = [s.strip().upper() for s in states.split(",")]
    else:
        state_list = ALL_STATES

    print(f"Running district analysis for {len(state_list)} states")
    print(f"States: {state_list}")
    print(f"Each state runs BOTH baselines (tcja-extension, tcja-expiration)")
    print("-" * 60)

    # Run all states in parallel - each handles both baselines
    results = list(analyze_state_both_baselines.map(state_list))

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    successes = [r for r in results if r["status"] == "success"]
    failures = [r for r in results if r["status"] == "failed"]

    print(f"\nSuccessful: {len(successes)}/{len(results)} states")
    for r in successes:
        print(f"  ✓ {r['state']}")

    if failures:
        print(f"\nFailed: {len(failures)}/{len(results)} states")
        for r in failures:
            print(f"  ✗ {r['state']}: {r['error']}")
        print(f"\nTo retry failed states:")
        failed_codes = ",".join([r["state"] for r in failures])
        print(f"  modal run modal_district_analysis.py --states \"{failed_codes}\"")

    print("\nResults saved to Modal volume 'district-analysis-results'")
    print("\nTo download results:")
    print("  modal volume get district-analysis-results . --force  # get all")


if __name__ == "__main__":
    main()
