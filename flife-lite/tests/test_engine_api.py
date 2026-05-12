from flife_lite_engine.api import run_fatigue_analysis


def test_run_fatigue_analysis_returns_life_prediction():
    result = run_fatigue_analysis(
        {
            "settings": {
                "method": "dirlik",
                "meanStressCorrection": "goodman",
                "cycleCounting": "four-point",
                "safetyFactor": 1.2,
                "damageModel": "miners-rule",
            },
            "material": {
                "id": "steel-42crmo4",
                "name": "42CrMo4 Steel",
                "utsMpa": 1080,
                "snIntercept": 1.8e19,
                "snSlope": 6,
            },
        }
    )

    assert result.life_seconds > 0
    assert result.damage_per_second > 0
    assert result.peak_stress_mpa > result.rms_stress_mpa
    assert result.cycles
    assert result.sn_curve
