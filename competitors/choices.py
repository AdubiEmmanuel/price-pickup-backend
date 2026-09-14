"""
Shared choice lists for the Unilever product taxonomy, used by both the
`competitors` (price pickup) and `stock` (customer stock pickup) apps so the
two stay in sync.
"""

SKU_CATEGORY_CHOICES = [
    ('NUTRITION', 'NUTRITION'),
    ('ORAL CARE', 'ORAL CARE'),
    ('DEODORANT', 'DEODORANT'),
    ('SKIN CARE', 'SKIN CARE'),
    ('SALVORY', 'SALVORY'),
]

SKU_SIZE_CHOICES = [
    ('BULK PACK', 'BULK PACK'),
    ('MID PACK', 'MID PACK'),
    ('REGULAR PACK', 'REGULAR PACK'),
    ('SMALL PACK', 'SMALL PACK'),
    ('POWDERS', 'POWDERS'),
]

BRAND_CHOICES = [
    ('PEARS', 'PEARS'),
    ('VASELINE', 'VASELINE'),
    ('CLOSE UP', 'CLOSE UP'),
    ('PEPSODENT', 'PEPSODENT'),
    ('KNORR', 'KNORR'),
    ('ROYCO', 'ROYCO'),
    ('REXONA', 'REXONA'),
]
