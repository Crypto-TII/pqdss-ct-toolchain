from mqom import MQOM2Parameters, MQOM2, Category, TradeOff, Variant
from labels import get_label

for cat in [Category.I, Category.III, Category.V]:
    for field_size in [2, 256]:
        for trade_off in [TradeOff.SHORT, TradeOff.FAST]:
            for variant in [Variant.R5, Variant.R3]:

                # Get MQOM2 instance
                params = MQOM2Parameters.get(cat, field_size, trade_off, variant)
                mqom = MQOM2(params, None)

                # Get Sizes
                pk_size = mqom.get_public_key_bytesize()
                sk_size = mqom.get_secret_key_bytesize()
                sig_size = mqom.get_signature_bytesize()

                # Print Sizes
                label = get_label(cat, field_size, trade_off, variant)
                print(f'===== {label} =====')
                print(f' - Public Key: {pk_size} B')
                print(f' - Secret Key: {sk_size} B')
                print(f' - Sig Size: {sig_size} B')
                print()
