from mqom import MQOM2Parameters, MQOM2, Category, TradeOff, Variant
from labels import get_label
import time

def random_bytes(n):
    import random
    return bytes([random.randint(0,255) for _ in range(n)])

def run_scheme(params):
    mqom = MQOM2(params, random_bytes)
    msg = random_bytes(16)

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

    # Key Generation
    start = time.time()
    (pk, sk) = mqom.generate_keys()
    timing = time.time() - start
    assert sk_size == len(sk)
    assert pk_size == len(pk)
    print(f'KeyGen Timing: {timing}')

    # Signing Algorithm
    start = time.time()
    sig = mqom.sign(sk, msg)
    timing = time.time() - start
    assert sig_size == len(sig)
    print(f'Signing Timing: {timing}')

    # Signing Algorithm
    start = time.time()
    ret = mqom.verify(pk, msg, sig)
    timing = time.time() - start
    assert ret is True
    print(f'Verif. Timing: {timing}')
    print()

import argparse
parser = argparse.ArgumentParser()
parser.add_argument('instance_labels',
    nargs='*',
    help="Instance to execute"
)
arguments = parser.parse_args()
instance_labels = arguments.instance_labels

if len(instance_labels) == 0:
    for cat in [Category.I, Category.III, Category.V]:
        for field_size in [2, 256]:
            for trade_off in [TradeOff.SHORT, TradeOff.FAST]:
                for variant in [Variant.R5, Variant.R3]:

                    # Get MQOM2 instance
                    params = MQOM2Parameters.get(cat, field_size, trade_off, variant)
                    run_scheme(params)

else:
    from labels import get_instance_from_label
    for label in instance_labels:
        params = get_instance_from_label(label)
        run_scheme(params)
