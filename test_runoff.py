"""Pytest test suite for SCS-CN runoff calculation module."""

import pytest
from scs_cn_runoff import calculate_runoff, calculate_S, calculate_Ia


class TestZeroRunoffConditions:
    """Test cases where no runoff is generated due to insufficient rainfall."""

    @pytest.mark.parametrize(
        "P,CN",
        [
            (0, 80),
            (5, 80),
            (12.7, 80),
        ],
    )
    def test_no_runoff_when_precipitation_below_ia(self, P, CN):
        """Test that runoff is zero when precipitation is at or below initial abstraction.

        In the SCS-CN method, initial abstraction (Ia) represents the amount of
        precipitation lost to surface storage, interception, and infiltration before
        runoff begins. When P <= Ia, no direct runoff occurs.
        """
        Q = calculate_runoff(P, CN)
        assert Q == 0


class TestNormalConditions:
    """Test cases for normal runoff conditions."""

    def test_normal_case(self):
        """Test the standard SCS-CN case with P=50mm and CN=80.

        This is the baseline test case that verifies the SCS-CN formula
        produces the expected runoff value for typical watershed conditions.
        CN=80 represents moderate runoff potential.
        """
        Q = calculate_runoff(50, 80)
        assert Q == pytest.approx(13.8, abs=0.1)

    def test_high_cn_produces_more_runoff(self):
        """Test that higher CN values produce more runoff for same precipitation.

        The Curve Number directly relates to runoff potential - higher CN indicates
        less infiltration and more runoff. This test verifies that physical
        relationship holds: CN=95 should produce more runoff than CN=80.
        """
        Q_80 = calculate_runoff(50, 80)
        Q_95 = calculate_runoff(50, 95)
        assert Q_95 > Q_80

    def test_max_cn_impervious(self):
        """Test CN=100 produces runoff close to precipitation (impervious surface).

        CN=100 represents completely impervious surfaces (all rainfall becomes
        runoff). The result should be very close to but not exceeding P.
        """
        Q = calculate_runoff(50, 100)
        assert Q == pytest.approx(50, abs=0.5)


class TestPhysicalConstraints:
    """Test that the model respects fundamental physical constraints."""

    def test_runoff_never_exceeds_precipitation(self):
        """Test that runoff Q cannot exceed precipitation P (conservation of mass).

        This is a fundamental physical constraint - the amount of runoff cannot
        exceed the amount of precipitation that fell. This test uses a high CN
        value to stress the boundary condition.
        """
        P = 100
        CN = 90
        Q = calculate_runoff(P, CN)
        assert Q <= P


class TestMonotonicity:
    """Test that runoff increases monotonically with CN."""

    def test_runoff_increases_with_cn(self):
        """Test that runoff increases as CN increases (keeping P constant).

        This is a critical physical validation: higher CN means higher runoff
        potential. The model should produce monotonically increasing runoff
        as CN increases from 60 to 100.
        """
        P = 50
        previous_Q = None

        for CN in range(60, 101):
            Q = calculate_runoff(P, CN)

            if previous_Q is not None:
                assert Q >= previous_Q, (
                    f"Runoff should increase with CN: "
                    f"CN={CN - 1} gave Q={previous_Q:.4f}, CN={CN} gave Q={Q:.4f}"
                )

            previous_Q = Q


class TestInputValidation:
    """Test input validation and error handling."""

    def test_negative_precipitation_raises_error(self):
        """Test that negative precipitation raises ValueError.

        Negative rainfall is physically impossible and should be rejected
        with a clear error message.
        """
        with pytest.raises(ValueError):
            calculate_runoff(-10, 80)

    def test_cn_below_valid_range_raises_error(self):
        """Test that CN below 1 raises ValueError.

        CN values below 1 are outside the valid SCS-CN range and should
        be rejected.
        """
        with pytest.raises(ValueError):
            calculate_runoff(50, 0)

    def test_cn_above_valid_range_raises_error(self):
        """Test that CN above 100 raises ValueError.

        CN values above 100 are outside the valid SCS-CN range and should
        be rejected.
        """
        with pytest.raises(ValueError):
            calculate_runoff(50, 101)
