
import argparse
import json
from dataclasses import asdict, dataclass
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

MONEY = Decimal("0.01")
MAX_CONSUMPTION = Decimal("20000")


def round_money(value):
    """Round an EGP amount to two decimal places."""
    return value.quantize(MONEY, rounding=ROUND_HALF_UP)


# --------------------------------------------------
# INPUT VALIDATION
# --------------------------------------------------

def parse_kwh(value):
    """Validate monthly electricity consumption."""

    if isinstance(value, bool):
        raise ValueError("Consumption must be a number.")

    if not isinstance(value, (int, float, str, Decimal)):
        raise ValueError("Consumption must be a number.")

    if isinstance(value, str):
        value = value.strip()

        if not value or "," in value:
            raise ValueError(
                "Enter a number such as 400 or 400.5."
            )

    try:
        consumption = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(
            "Invalid electricity consumption."
        ) from None

    if not consumption.is_finite():
        raise ValueError("Consumption must be finite.")

    if consumption < 0:
        raise ValueError(
            "Consumption cannot be negative."
        )

    if consumption > MAX_CONSUMPTION:
        raise ValueError(
            "Consumption cannot exceed 20,000 kWh."
        )

    return consumption


# --------------------------------------------------
# DATA CLASSES
# --------------------------------------------------

@dataclass
class LineItem:
    from_kwh: float
    to_kwh: float
    quantity_kwh: float
    rate_piastres: float
    amount_egp: float


@dataclass
class BillResult:
    consumption_kwh: float
    schedule_id: str
    schedule_label: str
    schedule_status: str
    team_checked: bool
    category_max_kwh: float | None
    rate_multiplier: float
    line_items: list[LineItem]
    energy_charge_egp: float
    service_fee_egp: float
    service_fee_status: str
    total_egp: float

    def to_dict(self):
        """Convert the bill into a dictionary."""
        return asdict(self)


# --------------------------------------------------
# VALIDATE TARIFF CONFIGURATION
# --------------------------------------------------

def _validate_schedule(schedule):
    """Check that tariff categories and bands are valid."""

    if not isinstance(schedule, dict):
        raise ValueError(
            "A tariff schedule must be an object."
        )

    categories = schedule.get("categories")

    if not isinstance(categories, list) or not categories:
        raise ValueError(
            "A schedule must contain categories."
        )

    previous_max = Decimal("-1")

    for index, category in enumerate(categories):

        maximum = category.get("max_kwh")
        is_last = index == len(categories) - 1

        if maximum is None:
            if not is_last:
                raise ValueError(
                    "Only the final category may be unlimited."
                )
            max_decimal = None

        else:
            max_decimal = Decimal(str(maximum))

            if (
                not max_decimal.is_finite()
                or max_decimal <= previous_max
            ):
                raise ValueError(
                    "Category limits must increase."
                )

            previous_max = max_decimal

        bands = category.get("bands")

        if not isinstance(bands, list) or not bands:
            raise ValueError(
                "Every category must have pricing bands."
            )

        expected_start = Decimal("0")

        for band_index, band in enumerate(bands):

            if not isinstance(band, list) or len(band) != 3:
                raise ValueError(
                    "Every band must contain three values."
                )

            start, end, rate = band

            start = Decimal(str(start))
            rate = Decimal(str(rate))

            if (
                not start.is_finite()
                or start != expected_start
            ):
                raise ValueError(
                    "Pricing bands have a gap or overlap."
                )

            if not rate.is_finite() or rate <= 0:
                raise ValueError(
                    "Pricing rates must be positive."
                )

            if end is None:
                if not is_last or band_index != len(bands) - 1:
                    raise ValueError(
                        "An unlimited band must be last."
                    )

                expected_start = None

            else:
                end = Decimal(str(end))

                if (
                    not end.is_finite()
                    or end <= start
                ):
                    raise ValueError(
                        "Band limits must increase."
                    )

                expected_start = end

            if (
                expected_start is None
                and band_index != len(bands) - 1
            ):
                raise ValueError(
                    "No bands may follow an unlimited band."
                )

        if max_decimal is None:
            if expected_start is not None:
                raise ValueError(
                    "Final category must cover unlimited kWh."
                )

        elif expected_start != max_decimal:
            raise ValueError(
                "Bands must cover the full category."
            )

        fee = Decimal(
            str(category.get("service_fee_egp", 0))
        )

        if not fee.is_finite() or fee < 0:
            raise ValueError(
                "Service fees cannot be negative."
            )


# --------------------------------------------------
# MAIN TARIFF ENGINE
# --------------------------------------------------

class TariffEngine:
    """Calculate residential electricity bills."""

    def __init__(self, config):

        if not isinstance(config, dict):
            raise ValueError(
                "Invalid tariff configuration."
            )

        self.config = config
        self.schedules = config.get("schedules", {})
        self.default_schedule = config.get(
            "default_schedule"
        )

        if (
            not isinstance(self.schedules, dict)
            or not self.schedules
        ):
            raise ValueError(
                "No tariff schedules were found."
            )

        if self.default_schedule not in self.schedules:
            raise ValueError(
                "The default tariff schedule does not exist."
            )

        for schedule in self.schedules.values():
            _validate_schedule(schedule)

    @classmethod
    def from_file(cls, path):
        """Load tariff settings from JSON."""

        with open(path, "r", encoding="utf-8") as file:
            config = json.load(file)

        return cls(config)

    def list_schedules(self):
        """List available electricity schedules."""

        return [
            {
                "id": schedule_id,
                "label": schedule.get(
                    "label", schedule_id
                ),
                "status": schedule.get(
                    "status", "unknown"
                ),
                "team_checked": schedule.get(
                    "team_checked", False
                ),
            }
            for schedule_id, schedule in self.schedules.items()
        ]

    def get_schedule(self, schedule_id=None):
        """Get one tariff schedule."""

        schedule_id = (
            schedule_id or self.default_schedule
        )

        if schedule_id not in self.schedules:
            raise ValueError(
                f"Unknown tariff schedule: {schedule_id}"
            )

        return self.schedules[schedule_id]

    def calculate_bill(
        self,
        kwh,
        schedule_id=None,
        include_service_fee=False,
        rate_multiplier=1.0,
    ):
        """Calculate a household electricity bill."""

        consumption = parse_kwh(kwh)

        if isinstance(rate_multiplier, bool):
            raise ValueError(
                "Invalid rate multiplier."
            )

        try:
            multiplier = Decimal(
                str(rate_multiplier)
            )
        except (InvalidOperation, ValueError):
            raise ValueError(
                "Invalid rate multiplier."
            ) from None

        if (
            not multiplier.is_finite()
            or multiplier <= 0
        ):
            raise ValueError(
                "Rate multiplier must be positive."
            )

        schedule_id = (
            schedule_id or self.default_schedule
        )

        schedule = self.get_schedule(schedule_id)

        # Find the correct consumption category.
        category = None

        for candidate in schedule["categories"]:

            maximum = candidate["max_kwh"]

            if (
                maximum is None
                or consumption <= Decimal(str(maximum))
            ):
                category = candidate
                break

        if category is None:
            raise ValueError(
                "No matching tariff category."
            )

        # Calculate electricity charges.
        line_items = []
        energy_total = Decimal("0")

        for start, end, rate in category["bands"]:

            start = Decimal(str(start))

            end = (
                consumption
                if end is None
                else Decimal(str(end))
            )

            rate = Decimal(str(rate))

            used = max(
                Decimal("0"),
                min(consumption, end) - start,
            )

            if used <= 0:
                continue

            amount = round_money(
                used
                * rate
                * multiplier
                / Decimal("100")
            )

            energy_total += amount

            line_items.append(
                LineItem(
                    from_kwh=float(start),
                    to_kwh=float(start + used),
                    quantity_kwh=float(used),
                    rate_piastres=float(
                        rate * multiplier
                    ),
                    amount_egp=float(amount),
                )
            )

        # Service fee is optional and unverified.
        service_fee = Decimal("0")

        if include_service_fee:
            service_fee = Decimal(
                str(category.get("service_fee_egp", 0))
            )

        service_fee = round_money(service_fee)
        energy_total = round_money(energy_total)
        total = round_money(
            energy_total + service_fee
        )

        maximum = category["max_kwh"]

        return BillResult(
            consumption_kwh=float(consumption),
            schedule_id=schedule_id,
            schedule_label=schedule.get(
                "label", schedule_id
            ),
            schedule_status=schedule.get(
                "status", "unknown"
            ),
            team_checked=schedule.get(
                "team_checked", False
            ),
            category_max_kwh=(
                float(maximum)
                if maximum is not None
                else None
            ),
            rate_multiplier=float(multiplier),
            line_items=line_items,
            energy_charge_egp=float(
                energy_total
            ),
            service_fee_egp=float(
                service_fee
            ),
            service_fee_status=schedule.get(
                "service_fee_status",
                "unknown"
            ),
            total_egp=float(total),
        )


# --------------------------------------------------
# RUN FROM THE TERMINAL
# --------------------------------------------------

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=(
            "EgyptPowerSim electricity bill calculator"
        )
    )

    parser.add_argument(
        "kwh",
        help="Monthly electricity consumption in kWh",
    )

    parser.add_argument(
        "--schedule",
        default=None,
        help="Optional tariff schedule ID",
    )

    parser.add_argument(
        "--fee",
        action="store_true",
        help="Include unverified service fee",
    )

    args = parser.parse_args()

    config_path = (
        Path(__file__).resolve().parent.parent
        / "config"
        / "tariffs.json"
    )

    engine = TariffEngine.from_file(
        config_path
    )

    result = engine.calculate_bill(
        kwh=args.kwh,
        schedule_id=args.schedule,
        include_service_fee=args.fee,
    )

    print(
        json.dumps(
            result.to_dict(),
            indent=2,
        )
    )
