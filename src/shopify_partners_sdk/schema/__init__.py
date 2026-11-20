"""Partner API schema bundled with the SDK.

Each supported API version ships as a compact JSON file in ``data/``, generated from
Shopify's introspection data by ``schema/utils/build_sdk_schema.py``. The schema types
query variables exactly and catches invalid field names before a request is sent.
"""

from difflib import get_close_matches
from functools import cache, lru_cache
from importlib.resources import files
import json
from typing import Any, Literal

from shopify_partners_sdk.exceptions.validation import SchemaValidationError

Operation = Literal["query", "mutation"]

_DATA = files(__package__) / "data"
_LEAF_KINDS = {"SCALAR", "ENUM"}


def _bundled_versions() -> tuple[str, ...]:
    names = (entry.name for entry in _DATA.iterdir())
    return tuple(
        sorted(
            name.removeprefix("partner_").removesuffix(".json")
            for name in names
            if name.startswith("partner_") and name.endswith(".json")
        )
    )


SUPPORTED_API_VERSIONS: tuple[str, ...] = _bundled_versions()


def named_type(type_ref: str) -> str:
    """Strip list and non-null wrappers: ``[Foo!]!`` becomes ``Foo``."""
    return type_ref.strip("[]!")


def _did_you_mean(name: str, candidates: Any) -> list[str]:
    return get_close_matches(name, list(candidates), n=3, cutoff=0.6)


def _unknown(what: str, name: str, where: str, candidates: Any) -> None:
    suggestions = _did_you_mean(name, candidates)
    hint = (
        f" Did you mean {' or '.join(repr(s) for s in suggestions)}?"
        if suggestions
        else ""
    )
    raise SchemaValidationError(
        f"Unknown {what} '{name}' on {where}.{hint}", suggestions
    )


class PartnerSchema:
    """Read-only view of one Partner API version's types, fields, and arguments."""

    def __init__(self, version: str, data: dict[str, Any]) -> None:
        """Wrap compact schema data for one API version."""
        self.version = version
        self._types: dict[str, dict[str, Any]] = data["types"]
        self._roots: dict[str, str | None] = {
            "query": data["queryType"],
            "mutation": data["mutationType"],
        }

    def root_type(self, operation: Operation) -> str:
        """Name of the root type for ``query`` or ``mutation``."""
        root = self._roots[operation]
        if root is None:
            raise SchemaValidationError(
                f"API version {self.version} has no {operation} operations."
            )
        return root

    def type(self, name: str) -> dict[str, Any]:
        """Compact definition of a named type."""
        if name not in self._types:
            _unknown("type", name, f"API version {self.version}", self._types)
        return self._types[name]

    def type_names(self, kind: str | None = None) -> list[str]:
        """Names of all types, optionally only one kind such as ``ENUM``."""
        return [n for n, t in self._types.items() if kind is None or t["kind"] == kind]

    def kind(self, name: str) -> str:
        return str(self.type(name)["kind"])

    def is_leaf(self, name: str) -> bool:
        """True for scalars and enums, which take no sub-selection."""
        return self.kind(name) in _LEAF_KINDS

    def field(self, parent: str, name: str) -> dict[str, Any]:
        """Definition of ``parent.name``; raises with suggestions when unknown."""
        fields = self.type(parent).get("fields", {})
        if name not in fields:
            implementors = self._types_defining(name, self.possible_types(parent))
            if implementors:
                raise SchemaValidationError(
                    f"Field '{name}' is not defined on {self.kind(parent).lower()} "
                    f"'{parent}'. Select it inside an inline fragment on one of: "
                    f"{', '.join(implementors)} (FieldSelector.add_interface_field)."
                )
            _unknown("field", name, f"type '{parent}'", fields)
        return dict(fields[name])

    def root_field(self, operation: Operation, name: str) -> dict[str, Any]:
        """Definition of a top-level query or mutation field."""
        return self.field(self.root_type(operation), name)

    def argument_type(self, parent: str, field: str, argument: str) -> str:
        """GraphQL type of ``argument`` on ``parent.field``, e.g. ``[EventType!]``."""
        args = self.field(parent, field)["args"]
        if argument not in args:
            _unknown("argument", argument, f"field '{parent}.{field}'", args)
        return str(args[argument])

    def required_arguments(self, parent: str, field: str) -> list[str]:
        return list(self.field(parent, field).get("required", []))

    def input_field_type(self, input_type: str, name: str) -> str:
        fields = self.type(input_type).get("inputFields", {})
        if name not in fields:
            _unknown("input field", name, f"input type '{input_type}'", fields)
        return str(fields[name])

    def enum_values(self, name: str) -> list[str]:
        return list(self.type(name).get("enumValues", []))

    def check_enum_value(self, enum: str, value: str) -> None:
        values = self.enum_values(enum)
        if value not in values:
            _unknown("value", value, f"enum '{enum}'", values)

    def possible_types(self, name: str) -> list[str]:
        """Concrete types behind an interface or union (empty for objects)."""
        return list(self.type(name).get("possibleTypes", []))

    def check_fragment(self, parent: str, fragment_type: str) -> None:
        """Ensure ``... on fragment_type`` can apply where ``parent`` is expected."""
        # GraphQL allows a fragment when the two types share a concrete object type.
        if not set(self._concrete_types(parent)) & set(
            self._concrete_types(fragment_type)
        ):
            raise SchemaValidationError(
                f"Fragment on '{fragment_type}' can never match type '{parent}'."
            )

    def _concrete_types(self, name: str) -> list[str]:
        return self.possible_types(name) or [name]

    def _types_defining(self, field: str, type_names: list[str]) -> list[str]:
        return [t for t in type_names if field in self._types[t].get("fields", {})]


@cache
def load_schema(version: str) -> PartnerSchema:
    """Load the bundled schema for an API version (cached)."""
    if version not in SUPPORTED_API_VERSIONS:
        raise SchemaValidationError(
            f"No bundled schema for API version '{version}'. "
            f"Supported versions: {', '.join(SUPPORTED_API_VERSIONS)}."
        )
    raw = (_DATA / f"partner_{version}.json").read_text(encoding="utf-8")
    return PartnerSchema(version, json.loads(raw))


__all__ = [
    "SUPPORTED_API_VERSIONS",
    "PartnerSchema",
    "load_schema",
    "named_type",
]
