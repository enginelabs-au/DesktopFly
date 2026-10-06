"""Presynaptic sign rule for MaleCNS consensus_nt labels.

A neuron is included only when every resolved label agrees on one sign.
Modulatory labels, conflicting labels, and unclear labels exclude the neuron.
Glutamate as inhibitory is a model assumption (GluCl), recorded in the evidence.
"""

from __future__ import annotations

NT_SIGN = {"acetylcholine": 1, "gaba": -1, "glutamate": -1}
MODULATORY_NT = ("dopamine", "serotonin", "octopamine", "histamine")
SIGN_RULE = (
    "consensus_nt: acetylcholine +1; gaba -1; glutamate -1 (assumption); "
    "modulatory, conflicting, or unclear excluded"
)


def agreed_sign_map(bodies: list[int], labels: list[str]) -> dict[int, int]:
    seen: dict[int, set[int]] = {}
    blocked: set[int] = set()
    for body, label in zip(bodies, labels, strict=True):
        text = str(label).lower()
        if any(token in text for token in MODULATORY_NT):
            blocked.add(int(body))
            continue
        sign = NT_SIGN.get(text)
        if sign is None:
            continue
        seen.setdefault(int(body), set()).add(sign)
    return {
        body: next(iter(signs))
        for body, signs in seen.items()
        if len(signs) == 1 and body not in blocked
    }
