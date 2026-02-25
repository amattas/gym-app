from gym_api.services.measurement_service import _calculate_bmi


def test_bmi_calculation():
    # 80kg, 180cm => BMI = 80 / 1.8^2 = 24.7
    bmi = _calculate_bmi(80.0, 180.0)
    assert bmi == 24.7


def test_bmi_calculation_short():
    # 60kg, 150cm => BMI = 60 / 1.5^2 = 26.7
    bmi = _calculate_bmi(60.0, 150.0)
    assert bmi == 26.7


def test_bmi_calculation_tall():
    # 90kg, 190cm => BMI = 90 / 1.9^2 = 24.9
    bmi = _calculate_bmi(90.0, 190.0)
    assert bmi == 24.9
