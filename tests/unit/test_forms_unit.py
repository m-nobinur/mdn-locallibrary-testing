import datetime

import pytest

from catalog.forms import RenewBookForm


pytestmark = [pytest.mark.unit]


def test_renewal_date_rejects_past_date():
    form = RenewBookForm(
        data={"renewal_date": datetime.date.today() - datetime.timedelta(days=1)}
    )

    assert not form.is_valid()
    assert "Invalid date - renewal in past" in form.errors["renewal_date"]


def test_renewal_date_rejects_more_than_four_weeks_ahead():
    form = RenewBookForm(
        data={
            "renewal_date": datetime.date.today() + datetime.timedelta(weeks=4, days=1)
        }
    )

    assert not form.is_valid()
    assert (
        "Invalid date - renewal more than 4 weeks ahead" in form.errors["renewal_date"]
    )


def test_renewal_date_accepts_today_boundary():
    form = RenewBookForm(data={"renewal_date": datetime.date.today()})

    assert form.is_valid()


def test_renewal_date_accepts_four_week_boundary():
    form = RenewBookForm(
        data={"renewal_date": datetime.date.today() + datetime.timedelta(weeks=4)}
    )

    assert form.is_valid()


def test_renewal_date_field_metadata():
    form = RenewBookForm()

    assert form.fields["renewal_date"].label in (None, "renewal date")
    assert (
        form.fields["renewal_date"].help_text
        == "Enter a date between now and 4 weeks (default 3)."
    )
