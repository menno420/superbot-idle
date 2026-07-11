"""Pure render layer: engine state + theme pack -> embed-shaped payloads.

This is the seam superbot-next's plugin renders through. Every function
here is PURE presentation: plain dicts shaped like Discord embeds
(``title``, ``description``, ``color`` int, ``fields`` of
``{name, value, inline}``) — no chat-platform SDK imports, no I/O, no
wall clock (callers pass ``now`` in). Same state + same theme -> the
identical payload, byte for byte.

CORE/SKIN contract: every player-visible noun (names, flavor, emoji,
embed color) comes from the theme pack. The only literals this module
contributes are neutral scaffolding — digits, separators, arrows,
status marks, and the short generic label ``Lv``. Packs may override
that scaffolding through the OPTIONAL schema-v1 ``labels`` block
(docs/theme-schema.md § labels): an offline-return flavor template
(with the one substitution token ``{gains}``), status/shop title,
shop description, level label, and prestige progress label. Every
slot is optional — an unset slot falls back to the neutral default,
so pre-labels packs render byte-identically.

Budget enforcement (PLATFORM-LIMITS.md / docs/theme-schema.md): title
<= 256, field name <= 256, field value <= 1024, description <= 4096,
<= 25 fields. Two tiers, one validator:

- Values that embed FORMATTED NUMBERS are clamped at composition time
  with an ellipsis — a quintillion-digit balance is a display problem,
  not an error.
- THEME-SOURCED text is never truncated: the theme-gate already bounds
  it, so a slot it overflows means a broken pack or an engine bug —
  :func:`validate_embed` (run on every payload) raises
  :class:`RenderBudgetError` instead of silently mangling themed text.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from idle_engine.engine import offline_progress, production_per_second
from idle_engine.prestige import prestige_award, prestige_eligible
from idle_engine.upgrades import upgrade_cost

if TYPE_CHECKING:  # imported for type checking only: keeps runtime stdlib-only
    from idle_engine.state import GameState
    from idle_engine.theme import Theme

# Embed caps — the verbatim platform walls this layer guarantees.
TITLE_LIMIT = 256
FIELD_NAME_LIMIT = 256
FIELD_VALUE_LIMIT = 1024
DESCRIPTION_LIMIT = 4096
MAX_FIELDS = 25

_ELLIPSIS = "…"
_HEX_COLOR = re.compile(r"#[0-9A-Fa-f]{6}\Z")

# The one substitution token themed label templates may carry. Kept as a
# local literal (mirroring idle_engine.theme.GAINS_PLACEHOLDER) because
# this module must stay runtime-stdlib-only and never import the
# yaml-loading theme module.
_GAINS_PLACEHOLDER = "{gains}"

# Neutral scaffolding fallback for the shop level label.
_NEUTRAL_LEVEL_LABEL = "Lv"


class RenderBudgetError(ValueError):
    """A theme-sourced string overflowed an embed budget (engine/pack bug)."""


def embed_color_int(hex_color: str) -> int:
    """Parse a theme's ``#RRGGBB`` accent color to the wire's decimal RGB."""
    if not isinstance(hex_color, str) or not _HEX_COLOR.match(hex_color):
        raise ValueError(f"embed color must be #RRGGBB hex, got {hex_color!r}")
    return int(hex_color[1:], 16)


def _format_amount(amount: int) -> str:
    """Deterministic integer formatting with thousands separators."""
    return f"{amount:,}"


def _clamp(text: str, limit: int) -> str:
    """Safe truncation WITH ellipsis, for numeric/formatted content only.

    Never applied to theme-sourced strings on their own — those raise via
    :func:`validate_embed` instead (silent truncation would hide a bug the
    gate exists to prevent).
    """
    if len(text) <= limit:
        return text
    if limit < len(_ELLIPSIS):
        return ""
    return text[: limit - len(_ELLIPSIS)] + _ELLIPSIS


def validate_embed(embed: dict) -> dict:
    """The single budget gate: every view returns through here.

    Raises :class:`RenderBudgetError` on any cap violation. Because all
    number-bearing strings were already clamped at composition time, a
    failure here means theme-sourced text overflowed a slot the gate
    bounds it to fit — an engine or pack bug, surfaced loudly.
    """
    checks = [
        (1 <= len(embed["title"]) <= TITLE_LIMIT, "title", len(embed["title"])),
        (
            len(embed["description"]) <= DESCRIPTION_LIMIT,
            "description",
            len(embed["description"]),
        ),
        (len(embed["fields"]) <= MAX_FIELDS, "fields", len(embed["fields"])),
        (0 <= embed["color"] <= 0xFFFFFF, "color", embed["color"]),
    ]
    for i, field in enumerate(embed["fields"]):
        checks.append(
            (1 <= len(field["name"]) <= FIELD_NAME_LIMIT, f"fields[{i}].name", len(field["name"]))
        )
        checks.append(
            (
                1 <= len(field["value"]) <= FIELD_VALUE_LIMIT,
                f"fields[{i}].value",
                len(field["value"]),
            )
        )
    for ok, slot, measured in checks:
        if not ok:
            raise RenderBudgetError(
                f"embed budget violated at {slot!r} (measured {measured}): "
                "theme-sourced text overflowed a gate-bounded slot"
            )
    return embed


def _field(name: str, value: str, inline: bool) -> dict:
    return {"name": name, "value": value, "inline": inline}


def _labelled(emoji: str, name: str) -> str:
    """The one composition rule for themed labels: ``{emoji} {name}``."""
    return f"{emoji} {name}"


def _prestige_specs(theme: Theme) -> list:
    spec = theme.prestige_spec()
    return [spec] if spec is not None else []


def _label_slot(theme: Theme, slot: str) -> str | None:
    """The pack's themed override for a render label, or ``None``.

    Reads the OPTIONAL ``labels`` block (schema v1, additive): an absent
    block, or an unset/empty slot, yields ``None`` so the caller falls
    back to the neutral scaffolding this layer shipped with.
    """
    labels = theme.labels
    if labels is None:
        return None
    return getattr(labels, slot, None) or None


def render_status(state: GameState, theme: Theme, now: int) -> dict:
    """The status view: balances, generator counts + rates, offline gains.

    ``now`` is the caller's unix timestamp; production accrued since
    ``state.last_seen`` is DISPLAYED (never credited — crediting is
    :func:`idle_engine.engine.apply_offline_progress`, the engine's job).
    """
    specs = theme.generator_specs()
    upgrade_specs = theme.upgrade_specs()
    prestige_specs = _prestige_specs(theme)
    rates = production_per_second(state, specs, upgrade_specs, prestige_specs)
    earned = offline_progress(state, specs, state.last_seen, now, upgrade_specs, prestige_specs)

    description = theme.description
    gain_lines = []
    for currency in theme.currencies.values():
        amount = earned.get(currency.currency_id, 0)
        if amount > 0:
            gain_lines.append(
                f"+{_format_amount(amount)} {_labelled(currency.emoji, currency.name)}"
            )
    if gain_lines:
        gains_text = "\n".join(gain_lines)
        template = _label_slot(theme, "offline_return")
        if template is not None:
            # Themed flavor line: replace the one substitution token with
            # the formatted gains, clamped (numeric tier) to the room the
            # fixed template text leaves. The template itself is
            # theme-sourced — never truncated; if it cannot fit,
            # validate_embed raises (theme-overflow tier).
            fixed = len(template) - len(_GAINS_PLACEHOLDER)
            room = DESCRIPTION_LIMIT - len(description) - 2 - fixed
            line = template.replace(_GAINS_PLACEHOLDER, _clamp(gains_text, max(room, 0)), 1)
            description = description + "\n\n" + line
        else:
            room = DESCRIPTION_LIMIT - len(description) - 2
            if room >= 1:
                description = description + "\n\n" + _clamp(gains_text, room)

    fields = []
    prestige_currency = theme.prestige.currency if theme.prestige else None
    for currency in theme.currencies.values():
        cid = currency.currency_id
        if cid == prestige_currency:
            held = state.prestige.get(cid, 0)
            value = _format_amount(held)
        else:
            value = _format_amount(state.balances.get(cid, 0))
            rate = rates.get(cid, 0)
            if rate > 0:
                value += f" (+{_format_amount(rate)}/s)"
        fields.append(
            _field(_labelled(currency.emoji, currency.name), _clamp(value, FIELD_VALUE_LIMIT), True)
        )
    for generator in theme.generators.values():
        spec = next(s for s in specs if s.spec_id == generator.generator_id)
        count = state.owned.get(spec.spec_id, 0)
        value = f"× {_format_amount(count)}"
        if count:
            rate = production_per_second(state, [spec], upgrade_specs, prestige_specs).get(
                spec.produces, 0
            )
            value += f" · +{_format_amount(rate)}/s"
        fields.append(
            _field(_labelled(generator.emoji, generator.name), _clamp(value, FIELD_VALUE_LIMIT), True)
        )

    return validate_embed(
        {
            "title": _label_slot(theme, "status_title") or _labelled(theme.emoji, theme.name),
            "description": description,
            "color": embed_color_int(theme.embed_color),
            "fields": fields,
        }
    )


def render_shop(state: GameState, theme: Theme) -> dict | None:
    """The upgrade-shop view: each upgrade's next level, cost, affordability.

    Returns ``None`` when the pack declares no ``upgrades`` block. Costs
    come from the engine's pre-registered curve (``idle_engine.economy``)
    at the state's CURRENT level. Upgrade flavor ``description`` is not
    composed into the cost field in v1 — the schema gives it the whole
    1024-char budget, so composing it with anything could overflow on a
    legal pack (see docs/render-layer.md).
    """
    if not theme.upgrades:
        return None
    spec_by_id = {spec.spec_id: spec for spec in theme.upgrade_specs()}
    level_label = _label_slot(theme, "level") or _NEUTRAL_LEVEL_LABEL
    fields = []
    for upgrade in theme.upgrades.values():
        spec = spec_by_id[upgrade.upgrade_id]
        level = state.upgrades.get(spec.spec_id, 0)
        cost = upgrade_cost(spec, level)
        affordable = state.balances.get(spec.cost_currency, 0) >= cost
        currency = theme.currencies[spec.cost_currency]
        mark = "✅" if affordable else "\U0001f512"
        value = (
            f"{mark} {level_label} {_format_amount(level)} → {_format_amount(level + 1)}"
            f" · {_format_amount(cost)} {_labelled(currency.emoji, currency.name)}"
        )
        fields.append(
            _field(_labelled(upgrade.emoji, upgrade.name), _clamp(value, FIELD_VALUE_LIMIT), False)
        )
    return validate_embed(
        {
            "title": _label_slot(theme, "shop_title") or _labelled(theme.emoji, theme.name),
            "description": _label_slot(theme, "shop_description") or theme.description,
            "color": embed_color_int(theme.embed_color),
            "fields": fields,
        }
    )


def render_prestige(state: GameState, theme: Theme) -> dict | None:
    """The prestige view: eligibility, progress, projected award.

    Returns ``None`` when the pack declares no ``prestige`` block. Shows
    (never performs) the reset: progress of the measured currency toward
    the threshold, and the held prestige balance with the award a reset
    right now would bank.
    """
    if theme.prestige is None:
        return None
    spec = theme.prestige_spec()
    measured = theme.currencies[theme.prestige.measures]
    awarded = theme.currencies[theme.prestige.currency]
    lifetime = state.lifetime.get(spec.measures, 0)
    held = state.prestige.get(spec.awards, 0)
    mark = "✅" if prestige_eligible(state, spec) else "\U0001f512"
    progress_label = _label_slot(theme, "prestige_progress")
    progress_prefix = f"{mark} {progress_label}" if progress_label else mark
    progress = f"{progress_prefix} {_format_amount(lifetime)} / {_format_amount(spec.threshold)}"
    projected = f"{_format_amount(held)} (+{_format_amount(prestige_award(state, spec))})"
    fields = [
        _field(_labelled(measured.emoji, measured.name), _clamp(progress, FIELD_VALUE_LIMIT), True),
        _field(_labelled(awarded.emoji, awarded.name), _clamp(projected, FIELD_VALUE_LIMIT), True),
    ]
    return validate_embed(
        {
            "title": _labelled(theme.prestige.action_emoji, theme.prestige.action_name),
            "description": theme.prestige.action_description,
            "color": embed_color_int(theme.embed_color),
            "fields": fields,
        }
    )
