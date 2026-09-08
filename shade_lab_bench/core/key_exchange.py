"""Diffie-Hellman exchange and unauthenticated MITM demonstrations."""

import warnings

from cryptography.hazmat.primitives.asymmetric import dh


def diffie_hellman_exchange(key_size: int = 512) -> dict:
    """Perform the original two-party finite-field DH exchange."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        parameters = dh.generate_parameters(generator=2, key_size=key_size)
    sender_private = parameters.generate_private_key()
    receiver_private = parameters.generate_private_key()
    sender_shared = sender_private.exchange(receiver_private.public_key())
    receiver_shared = receiver_private.exchange(sender_private.public_key())
    numbers = parameters.parameter_numbers()
    return {
        "sender_shared": sender_shared,
        "receiver_shared": receiver_shared,
        "shared_secret": sender_shared,
        "match": sender_shared == receiver_shared,
        "generator": numbers.g,
        "modulus_bits": numbers.p.bit_length(),
    }


def simulate_dh_mitm(key_size: int = 512) -> dict:
    """Reproduce the original Mallory public-key substitution attack."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        parameters = dh.generate_parameters(generator=2, key_size=key_size)
    sender = parameters.generate_private_key()
    receiver = parameters.generate_private_key()
    mallory = parameters.generate_private_key()
    mallory_public = mallory.public_key()
    mallory_with_sender = mallory.exchange(sender.public_key())
    mallory_with_receiver = mallory.exchange(receiver.public_key())
    sender_shared = sender.exchange(mallory_public)
    receiver_shared = receiver.exchange(mallory_public)
    succeeded = (
        sender_shared == mallory_with_sender
        and receiver_shared == mallory_with_receiver
        and sender_shared != receiver_shared
    )
    return {
        "sender_shared": sender_shared,
        "receiver_shared": receiver_shared,
        "mallory_with_sender": mallory_with_sender,
        "mallory_with_receiver": mallory_with_receiver,
        "attack_succeeded": succeeded,
    }
