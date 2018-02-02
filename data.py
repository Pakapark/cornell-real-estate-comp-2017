renterData = {
    'Topshop': {
        'totalSqm': 2400,
        'term': 120, # month
        'isGuaranteed': False,
        'initialRent': 2000000, # in euro
        'initialRentPerSqm': 833,
        'annualIncrease': 0.025,
        'abatement': 0, # in month
        'TI': 200, # TI per sqm
        'equityMultiple': {
            'unleveraged': 2.92,
            'lenderA': 2.11,
            'lenderB':  2.52
        },
        'IRR': {
            'unleveraged': 0.51,
            'lenderA': 0.66,
            'lenderB': 0.49
        }
    },
    'Zara': {
        'totalSqm': 2400,
        'term': 144,
        'isGuaranteed': True,
        'initialRent': 1400000,
        'initialRentPerSqm':  583,
        'annualIncrease': 0.025,
        'abatement': 12,
        'TI': 600,
        'equityMultiple': {
            'unleveraged': 2.62,
            'lenderA': 1.93,
            'lenderB': 2.25
        },
        'IRR': {
            'unleveraged': 0.41,
            'lenderA': 0.53,
            'lenderB': 0.37
        }
    },
    'Decathlon' : {
        'totalSqm': 2400,
        'term': 120,
        'isGuaranteed': True,
        'initialRent': 1700000,
        'initialRentPerSqm': 708,
        'annualIncrease': 0.025,
        'abatement': 9,
        'TI': 400,
        'equityMultiple': {
            'unleveraged': 3.28,
            'lenderA': 2.32,
            'lenderB': 2.72
        },
        'IRR': {
            'unleveraged': 0.53,
            'lenderA': 0.67,
            'lenderB': 0.46
        }
    }
}

readableMap = {
    'totalSqm': 'Total Area (in sqm)',
    'term': 'Term (in months)',
    'isGuaranteed': 'Guanrantee?',
    'initialRent': 'Initial Rent',
    'initialRentPerSqm': 'Initial Rent per Sqm',
    'annualIncrease': 'Annual Increase',
    'abatement': 'Abatement',
    'TI': "Concession: TI",
    'equityMultipleunleveraged': 'Equity Multiple for unleveraged',
    'equityMultiplelenderA': 'Equity Multiple for lender A',
    'equityMultiplelenderB': 'Equity Multiple for lender B',
    'IRRunleveraged': 'IRR for unleveraged',
    'IRRlenderA': 'IRR for lender A',
    'IRRlenderB': 'IRR for lender B'
}
