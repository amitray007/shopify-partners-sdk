"""Enums in models/enums.py must match the Partner API schema value for value."""

from enum import Enum

import pytest

from shopify_partners_sdk.models import enums
from shopify_partners_sdk.schema import load_schema

pytestmark = pytest.mark.unit

SCHEMA = load_schema("2026-10")

# Python enum name -> schema enum name, where they differ.
SCHEMA_NAMES = {"AppEventType": "AppEventTypes"}
UNSTABLE_ONLY = {"EventsinkTopic"}
NOT_IN_SCHEMA: set[str] = set()


def python_enums() -> dict[str, type[Enum]]:
    return {
        name: value
        for name, value in vars(enums).items()
        if isinstance(value, type)
        and issubclass(value, Enum)
        and value.__module__ == enums.__name__
    }


@pytest.mark.parametrize(
    "name", sorted(set(python_enums()) - UNSTABLE_ONLY - NOT_IN_SCHEMA)
)
def test_enum_matches_2026_10_schema(name):
    enum_cls = python_enums()[name]
    schema_name = SCHEMA_NAMES.get(name, name)
    assert sorted(m.value for m in enum_cls) == sorted(SCHEMA.enum_values(schema_name))


def test_unstable_enum_matches_unstable_schema():
    unstable = load_schema("unstable")
    assert sorted(m.value for m in enums.EventsinkTopic) == sorted(
        unstable.enum_values("EventsinkTopic")
    )


def test_every_2026_10_enum_has_a_python_counterpart():
    covered = {SCHEMA_NAMES.get(n, n) for n in python_enums()}
    assert set(SCHEMA.type_names("ENUM")) <= covered


@pytest.mark.parametrize(
    "removed",
    [
        "ConversationStatus",
        "JobStatus",
        "MessageSentVia",
        "ChargeStatus",
        "ServiceType",
    ],
)
def test_enums_for_removed_or_invented_types_are_gone(removed):
    assert not hasattr(enums, removed)


def test_transaction_type_has_no_invented_values():
    values = {m.value for m in enums.TransactionType}
    assert not values & {
        "LEGACY_TRANSACTION",
        "REFERRAL_TRANSACTION",
        "TAX_TRANSACTION",
    }


def test_enums_compare_equal_to_strings():
    assert enums.EventType.SUBSCRIPTION_CREATED == "SUBSCRIPTION_CREATED"
    assert enums.AppEventTypes is enums.AppEventType
