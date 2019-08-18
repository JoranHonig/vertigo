from eth_vertigo.test_runner.test_result import TestResult


def test_create():
    # Act
    test_result = TestResult(
        title="title",
        full_title="full title",
        duration=10,
        success=True
    )

    # Assert
    assert "title" == test_result.title
    assert "full title" == test_result.full_title
    assert 10 == test_result.duration
    assert True is test_result.success
