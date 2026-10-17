"""Smoke and sanity tests. Run: .venv/bin/python -m pytest -q"""
import os
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient  # noqa: E402

from api.main import app  # noqa: E402
from twinpulse import service  # noqa: E402
from twinpulse.metrics import clarke_zone  # noqa: E402
from twinpulse.features import insulin_activity_kernel  # noqa: E402

client = TestClient(app)


def test_board_lists_all_children_sorted_by_risk():
    r = client.get("/api/board").json()["patients"]
    assert len(r) == 12
    risks = [p["p_low"] for p in r]
    assert risks == sorted(risks, reverse=True)


def test_patient_payload_has_fhir_and_twin():
    p = client.get("/api/patients/TP-001").json()
    assert p["fhir"]["resourceType"] == "Bundle"
    assert any(e["resource"]["resourceType"] == "Consent" for e in p["fhir"]["entry"])
    assert 0 <= p["tonight"]["risk"]["p_low"] <= 1
    assert len(p["tonight"]["band"]) > 100


def test_unknown_patient_is_404():
    assert client.get("/api/patients/NOPE").status_code == 404


@pytest.mark.parametrize("pid", ["TP-001", "TP-002"])
def test_bedtime_snack_never_raises_risk(pid):
    base = service.tonight(pid)["risk"]["p_low"]
    snack = service.whatif(pid, snack_g=15)["risk"]["p_low"]
    assert snack <= base


def test_less_insulin_never_raises_low_risk():
    base = service.tonight("TP-002")["risk"]["p_low"]
    less = service.whatif("TP-002", dinner_rapid_pct=-20)["risk"]["p_low"]
    assert less <= base


def test_night_guard_warns_before_the_low():
    g = service.night_guard("TP-002")
    assert g["available"] and g["lead_min"] is not None and g["lead_min"] >= 15


def test_fingerstick_family_has_no_realtime_guard():
    assert service.night_guard("TP-001")["available"] is False


def test_insulin_kernel_sums_to_one_unit():
    activity, iob = insulin_activity_kernel()
    assert abs(activity.sum() - 1) < 0.02
    assert iob[0] == pytest.approx(1, abs=1e-6) and iob[-1] < 0.02


def test_clarke_zones():
    assert clarke_zone(100, 105) == "A"
    assert clarke_zone(250, 60) == "E"
    assert np.isclose(sum(1 for _ in "ABCDE"), 5)
