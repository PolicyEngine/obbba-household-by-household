// Provision-level breakdown for the household profile.
//
// Sign convention: the exported data records tax columns as changes in tax
// liability and benefit columns as changes in benefit value, and the net-income
// column satisfies
//
//   change in net income = -(federal tax change + state tax change) + benefits change
//
// (verified against the Microcosm Build P export). Everything this module
// returns as `taxChange` is therefore already flipped into the household's
// frame, so a tax cut reads as a gain and lines up with the headline number.

// Components smaller than this are treated as absent. Matches the rounding of
// the dollar amounts the profile renders.
export const SPLIT_THRESHOLD = 0.5;

// The first PARTICIPATION_START entries are the modeled tax provisions; the
// remainder are the reduced-form participation scenarios.
export const PARTICIPATION_START = 18;

export const BENEFIT_DISCLOSURE =
  'Includes Medicaid, CHIP, or marketplace credit values that respond to the tax change.';

export const SIGN_CONVENTION_NOTE =
  'Taxes and benefits are shown as their effect on household resources, so a tax cut is positive.';

// Forward stacking order used by the paper and the exported Microcosm data.
export const PROVISIONS = [
  {
    name: 'Tax rates',
    keys: ['Change in net income after Tax Rate Reform'],
    description:
      'Continues the TCJA individual income tax rates instead of allowing them to expire.'
  },
  {
    name: 'Standard deduction',
    keys: ['Change in net income after Standard Deduction Reform'],
    description:
      "Continues the larger TCJA standard deduction and applies the Act's additional increase."
  },
  {
    name: 'Personal exemption (continued suspension)',
    keys: ['Change in net income after Exemption Reform'],
    description: 'Continues the TCJA suspension of personal exemptions instead of restoring them.'
  },
  {
    name: 'CTC SSN requirement',
    keys: [
      'Change in net income after CTC SSN Requirement',
      'Change in net income after Child tax credit social security number requirement'
    ],
    description: "Applies the Act's Social Security number requirements to the child tax credit."
  },
  {
    name: 'CTC expansion',
    keys: [
      'Change in net income after CTC Expansion',
      'Change in net income after Child tax credit expansion'
    ],
    description:
      'Raises and indexes the child tax credit while continuing the TCJA credit structure.'
  },
  {
    name: 'CDCC expansion',
    keys: [
      'Change in net income after CDCC Reform',
      'Change in net income after Child and dependent care credit reform'
    ],
    description: 'Expands the child and dependent care credit rate for eligible expenses.'
  },
  {
    name: 'QBI deduction',
    keys: [
      'Change in net income after QBI Deduction Reform',
      'Change in net income after Qualified business interest deduction reform'
    ],
    description: 'Continues and modifies the deduction for qualified pass-through business income.'
  },
  {
    name: 'AMT',
    keys: [
      'Change in net income after AMT Reform',
      'Change in net income after Alternative minimum tax reform'
    ],
    description:
      'Continues and modifies the higher alternative minimum tax exemption and phaseout thresholds.'
  },
  {
    name: 'Miscellaneous deductions',
    keys: [
      'Change in net income after Miscellaneous Reform',
      'Change in net income after Miscellaneous deduction reform'
    ],
    description:
      'Continues the suspension of miscellaneous itemized deductions subject to the 2% AGI floor.'
  },
  {
    name: 'Casualty loss deduction repeal',
    keys: ['Change in net income after Casualty loss deduction repeal'],
    description: 'Continues limits on personal casualty-loss deductions.'
  },
  {
    name: 'Other itemized deductions',
    keys: [
      'Change in net income after Other Itemized Deductions Reform',
      'Change in net income after Charitable deductions reform'
    ],
    description: "Applies the Act's rules for charitable and mortgage-interest deductions."
  },
  {
    name: 'Itemized deduction limitation',
    keys: [
      'Change in net income after Limitation on Itemized Deductions Reform',
      'Change in net income after Limitation on itemized deductions reform'
    ],
    description:
      'Limits the value of itemized deductions for taxpayers in the top income-tax bracket.'
  },
  {
    name: 'Estate tax',
    keys: [
      'Change in net income after Estate Tax Reform',
      'Change in net income after Estate tax reform'
    ],
    description:
      'Raises and indexes the estate and gift tax exemption. Survey records contain no decedents, so this is a structural zero here.'
  },
  {
    name: 'SALT cap',
    keys: [
      'Change in net income after SALT Cap Reform',
      'Change in net income after Cap on state and local tax deduction'
    ],
    description: 'Raises the cap on state and local tax deductions, with an income-based phaseout.'
  },
  {
    name: 'Tip exemption',
    keys: [
      'Change in net income after Tip Income Exemption',
      'Change in net income after Tip exemption'
    ],
    description: 'Creates a temporary deduction for qualifying tip income.'
  },
  {
    name: 'Overtime exemption',
    keys: [
      'Change in net income after Overtime Exemption',
      'Change in net income after Overtime exemption'
    ],
    description: 'Creates a temporary deduction for qualifying overtime premium pay.'
  },
  {
    name: 'Senior deduction',
    keys: [
      'Change in net income after Senior Deduction',
      'Change in net income after New senior deduction'
    ],
    description:
      'Creates a temporary additional deduction for taxpayers age 65 and older, subject to an income phaseout.'
  },
  {
    name: 'Auto loan interest deduction',
    keys: [
      'Change in net income after Auto Loan Interest',
      'Change in net income after Auto loan interest deduction'
    ],
    description: 'Creates a temporary deduction for interest on qualifying vehicle loans.'
  },
  {
    name: 'SNAP participation',
    keys: [
      'Change in net income after SNAP Takeup Reform',
      'Change in net income after SNAP reform'
    ],
    description:
      'A seeded, reduced-form scenario lowers SNAP participation to reflect projected enrollment effects; it does not identify specific eligibility losses.'
  },
  {
    name: 'ACA participation',
    keys: [
      'Change in net income after ACA Takeup Reform',
      'Change in net income after Extension of ACA enhanced subsidies'
    ],
    description:
      'A seeded, reduced-form scenario lowers marketplace participation and removes enrollee-assigned premium tax credits at program cost.'
  },
  {
    name: 'Medicaid participation',
    keys: [
      'Change in net income after Medicaid Takeup Reform',
      'Change in net income after Medicaid reform'
    ],
    description:
      "A seeded, reduced-form scenario lowers Medicaid participation toward the paper's state-level ceiling; it does not identify specific eligibility losses."
  }
];

// Reads a numeric column, tolerating the two column vocabularies in the data:
// the national Microcosm export writes "tax liability", the district files
// write "tax".
function readNumber(household, keys) {
  for (const key of keys) {
    const raw = household[key];
    if (raw === undefined || raw === null || raw === '') continue;
    const value = Number(raw);
    if (Number.isFinite(value)) return value;
  }
  return 0;
}

function isPresent(value) {
  return Math.abs(value) > SPLIT_THRESHOLD;
}

/**
 * Per-provision rows for the profile, in the paper's forward stacking order,
 * with the tax and benefit components of each net-income change.
 */
export function getProvisionBreakdown(household) {
  if (!household) return [];

  return PROVISIONS.map((provision, index) => {
    // Find the first matching key that exists in household data
    const matchingKey = provision.keys.find(
      (key) => household[key] !== undefined && household[key] !== 0
    );
    // The 200- and 2,000-row preview parses leave every field a string
    // (dataLoader.js parses those with dynamicTyping off), so coerce here.
    const value = matchingKey ? Number(household[matchingKey]) : 0;

    // Extract the provision suffix from the matching key
    const suffix = matchingKey ? matchingKey.replace('Change in net income after ', '') : '';

    const federalChange = readNumber(household, [
      `Change in federal tax after ${suffix}`,
      `Change in federal tax liability after ${suffix}`
    ]);
    const stateChange = readNumber(household, [
      `Change in state tax after ${suffix}`,
      `Change in state tax liability after ${suffix}`
    ]);
    const benefitsChange = readNumber(household, [`Change in benefits after ${suffix}`]);

    // Flip into the household's frame: lower tax liability is a gain.
    const taxChange = -(federalChange + stateChange);
    const isTaxProvision = index < PARTICIPATION_START;

    return {
      name: provision.name,
      value: value,
      index: index,
      description: provision.description,
      federalChange,
      stateChange,
      benefitsChange,
      taxChange,
      isTaxProvision,
      // The headline already says everything when only one component moves.
      showSplit: isPresent(taxChange) && isPresent(benefitsChange),
      // Tax provisions that move benefits need saying so out loud.
      showBenefitDisclosure: isTaxProvision && isPresent(benefitsChange)
    };
  }).filter((p) => Math.abs(p.value) > 0.01);
}

/**
 * Household-level totals in the same frame as the provision rows.
 */
export function getTotalsSplit(household) {
  if (!household) {
    return { federalChange: 0, stateChange: 0, taxChange: 0, benefitsChange: 0, showSplit: false };
  }

  // Key order matches what the component read before this module existed.
  const federalChange = readNumber(household, [
    'Total change in federal tax liability',
    'Total change in federal tax'
  ]);
  const stateChange = readNumber(household, [
    'Total change in state tax liability',
    'Total change in state tax'
  ]);
  const benefitsChange = readNumber(household, ['Total change in benefits']);
  const taxChange = -(federalChange + stateChange);

  return {
    federalChange,
    stateChange,
    taxChange,
    benefitsChange,
    // Shown whenever either side of the split carries information.
    showSplit: isPresent(taxChange) || isPresent(benefitsChange)
  };
}
