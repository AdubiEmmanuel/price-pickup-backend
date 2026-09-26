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

# The retail channel/market a price was picked up in, or a store belongs to -
# shared so a store's own channel (stock/models.py Customer.channel) lines up
# with the same taxonomy used when picking up its prices.
MARKET_CHANNEL_CHOICES = [
    ('OPEN_MARKET', 'Open Market'),
    ('NG', 'NG Market'),
    ('SMALL_SUPERMARKET', 'Small Supermarket'),
    ('WHOLESALE', 'Wholesale'),
]
