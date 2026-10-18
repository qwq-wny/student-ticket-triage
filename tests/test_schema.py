import pytest
from pydantic import ValidationError

from app.schema import TicketRequest


def good_input(**changes):
    values = {
        "text": "production is down",
        "customer_tier": "premium",
        "monthly_revenue": 100,
    }
    values.update(changes)
    return values


def test_valid_and_boundary_values_work():
    short = TicketRequest(**good_input(text="abc", monthly_revenue=0))
    long = TicketRequest(**good_input(text="a" * 4000, monthly_revenue=1_000_000_000))
    assert short.text == "abc"
    assert long.customer_tier == "premium"


def test_invalid_values_are_rejected():
    bad_inputs = [
        good_input(text="ab"),
        good_input(text="a" * 4001),
        good_input(customer_tier="enterprise"),
        good_input(monthly_revenue=-1),
        good_input(monthly_revenue=1_000_000_001),
        good_input(text=None),
    ]
    for payload in bad_inputs:
        with pytest.raises(ValidationError):
            TicketRequest(**payload)


def test_extra_fields_are_rejected():
    with pytest.raises(ValidationError):
        TicketRequest(**good_input(extra="not allowed"))
