
import copy
from decimal import Decimal
from pathlib import Path

import pytest

from src.tariff_engine import TariffEngine, parse_kwh


# Locate the tariff file automatically.
CONFIG_PATH = (
    Path(__file__).resolve().parent.parent
    / "config"
    / "tariffs.json"
)

APRIL = "egyptera_2026_04"
AUGUST = "reported_2026_08"


@pytest.fixture
def engine():
    """Create a fresh tariff calculator for each test."""
    return TariffEngine.from_file(CONFIG_PATH)


# TEST 1: The default schedule is April.
def test_default_schedule(engine):
    result = engine.calculate_bill(400)

    assert result.schedule_id == APRIL
    assert result.consumption_kwh == 400


# TEST 2: Check April category boundaries.
def test_april_boundary_bills(engine):
    expected = {
        0: 0.00,
        50: 34.00,
        100: 73.00,
        200: 190.00,
        350: 422.50,
        400: 520.00,
        650: 1007.50,
        1000: 2100.00,
        1001: 2582.58,
    }

    for kwh, amount in expected.items():
        result = engine.calculate_bill(kwh, APRIL)

        assert result.total_egp == pytest.approx(amount)


# TEST 3: Check the reported August schedule.
def test_august_bills(engine):
    expected = {
        50: 34.00,
        100: 77.50,
        200: 212.00,
        400: 582.00,
        1000: 2350.00,
    }

    for kwh, amount in expected.items():
        result = engine.calculate_bill(kwh, AUGUST)

        assert result.total_egp == pytest.approx(amount)


# TEST 4: Bill breakdown adds up correctly.
def test_line_items_add_up(engine):
    for schedule in (APRIL, AUGUST):
        for kwh in (50, 150, 400, 800, 1200):
            result = engine.calculate_bill(kwh, schedule)

            item_total = sum(
                item.amount_egp
                for item in result.line_items
            )

            assert item_total == pytest.approx(
                result.energy_charge_egp
            )


# TEST 5: More consumption never gives a lower bill.
def test_bill_never_decreases(engine):
    for schedule in (APRIL, AUGUST):
        previous = 0.0

        for kwh in range(1501):
            bill = engine.calculate_bill(
                kwh, schedule
            ).energy_charge_egp

            assert bill >= previous
            previous = bill


# TEST 6: Fractional electricity consumption.
def test_fractional_kwh(engine):
    result = engine.calculate_bill(400.5, APRIL)

    assert result.total_egp == pytest.approx(520.98)


# TEST 7: Service fee is optional.
def test_service_fee(engine):
    without_fee = engine.calculate_bill(
        400, APRIL
    )

    with_fee = engine.calculate_bill(
        400,
        APRIL,
        include_service_fee=True,
    )

    assert without_fee.service_fee_egp == 0
    assert with_fee.service_fee_egp == 15
    assert with_fee.total_egp == pytest.approx(535.0)


# TEST 8: Unverified information is identified.
def test_unverified_flags(engine):
    april = engine.get_schedule(APRIL)
    august = engine.get_schedule(AUGUST)

    assert april["team_checked"] is False
    assert august["team_checked"] is False

    assert august["status"] == "reported_unverified"
    assert april["service_fee_status"] == "unverified"


# TEST 9: A multiplier of 1 changes nothing.
def test_multiplier_one(engine):
    normal = engine.calculate_bill(400, APRIL)

    unchanged = engine.calculate_bill(
        400,
        APRIL,
        rate_multiplier=1.0,
    )

    assert normal.to_dict() == unchanged.to_dict()


# TEST 10: A 10% rate increase changes energy only.
def test_rate_increase(engine):
    result = engine.calculate_bill(
        400,
        APRIL,
        include_service_fee=True,
        rate_multiplier=1.10,
    )

    assert result.energy_charge_egp == pytest.approx(572.0)
    assert result.service_fee_egp == 15
    assert result.total_egp == pytest.approx(587.0)
    assert result.category_max_kwh == 650


# TEST 11: Invalid electricity inputs are rejected.
def test_invalid_consumption():
    invalid_values = [
        -1,
        -0.5,
        "hello",
        "",
        "1,000",
        "abc123",
        True,
        False,
        None,
        float("nan"),
        float("inf"),
        float("-inf"),
        20001,
    ]

    for value in invalid_values:
        with pytest.raises(ValueError):
            parse_kwh(value)


# TEST 12: Unknown tariff schedules are rejected.
def test_unknown_schedule(engine):
    with pytest.raises(ValueError):
        engine.calculate_bill(
            400,
            schedule_id="unknown_schedule",
        )


# TEST 13: Invalid rate multipliers are rejected.
def test_invalid_multiplier(engine):
    invalid_multipliers = [
        -1,
        0,
        True,
        float("nan"),
        float("inf"),
        "not-a-number",
    ]

    for multiplier in invalid_multipliers:
        with pytest.raises(ValueError):
            engine.calculate_bill(
                400,
                APRIL,
                rate_multiplier=multiplier,
            )


# TEST 14: Broken tariff configuration is rejected.
def test_broken_configuration(engine):
    broken = copy.deepcopy(engine.config)

    # Create a gap in the first category.
    broken["schedules"][APRIL]["categories"][0][
        "bands"
    ][0][0] = 10

    with pytest.raises(ValueError):
        TariffEngine(broken)

    broken_rate = copy.deepcopy(engine.config)

    # A negative electricity rate is invalid.
    broken_rate["schedules"][APRIL]["categories"][0][
        "bands"
    ][0][2] = -68

    with pytest.raises(ValueError):
        TariffEngine(broken_rate)
