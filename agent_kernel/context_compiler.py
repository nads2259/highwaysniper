"""Context compiler: not prompt concatenation."""

from __future__ import annotations

import re

from agent_kernel.state import CompiledContext

_INJECTION = re.compile(
    r"ignore (previous|all) instructions|system prompt|exfiltrate",
    re.I,
)
_SECRET = re.compile(r"(api[_-]?key|password|secret)\s*[:=]\s*\S+", re.I)
_PII = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")


def compile_context(
    *,
    trusted_instructions: list[str],
    sources: list[tuple[str, str, str]],
    token_budget: int = 4000,
) -> CompiledContext:
    """sources: (text, provenance, authority_score_str)."""
    ranked = sorted(sources, key=lambda s: s[2], reverse=True)
    untrusted: list[str] = []
    provenance: dict[str, str] = {}
    flags: list[str] = []
    why: list[str] = []
    used = 0
    seen: set[str] = set()
    for text, prov, score in ranked:
        if text in seen:
            continue
        seen.add(text)
        if _INJECTION.search(text):
            flags.append(f"injection:{prov}")
            continue
        redacted = _SECRET.sub("[REDACTED]", _PII.sub("[REDACTED]", text))
        cost = max(1, len(redacted) // 4)
        if used + cost > token_budget:
            why.append(f"overflow_skip:{prov}")
            continue
        used += cost
        untrusted.append(redacted)
        provenance[redacted[:48]] = prov
        why.append(f"included:{prov}:authority={score}")
    return CompiledContext(
        trusted_instructions=list(trusted_instructions),
        untrusted_data=untrusted,
        provenance=provenance,
        token_estimate=used,
        injection_flags=flags,
        why_included=why,
    )
