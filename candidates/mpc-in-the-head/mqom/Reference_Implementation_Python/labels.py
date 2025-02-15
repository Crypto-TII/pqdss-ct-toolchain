from mqom import MQOM2Parameters, Category, TradeOff, Variant

LABEL_CAT = {
    Category.I:   'L1',
    Category.III: 'L3',
    Category.V:   'L5',
}

LABEL_FIELD = {
    2:   'gf2',
    256: 'gf256',
}

LABEL_TRADEOFF = {
    TradeOff.SHORT: 'short',
    TradeOff.FAST:  'fast',
}

LABEL_VARIANT = {
    Variant.R5: 'R5',
    Variant.R3: 'R3',
}

def gey_key_of(d, searched_value):
    for key, value in d.items():
        if value == searched_value:
            return key

def get_label(cat, field_size, trade_off, variant):
    label = f'MQOM2-{LABEL_CAT[cat]}-{LABEL_FIELD[field_size]}'
    label += f'-{LABEL_TRADEOFF[trade_off]}-{LABEL_VARIANT[variant]}'
    return label

def get_instance_from_label(label):
    scheme, label_cat, label_field, label_tradeoff, label_variant = label.split('-')
    assert scheme == 'MQOM2'
    cat = gey_key_of(LABEL_CAT, label_cat)
    field_size = gey_key_of(LABEL_FIELD, label_field)
    trade_off = gey_key_of(LABEL_TRADEOFF, label_tradeoff)
    variant = gey_key_of(LABEL_VARIANT, label_variant)
    return MQOM2Parameters.get(cat, field_size, trade_off, variant)
