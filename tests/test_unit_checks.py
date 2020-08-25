from c3schecker.checks import ChecksRegistry


def test_checks_registry():
    # There should be only one checks registry
    r1 = ChecksRegistry()
    r2 = ChecksRegistry()
    assert r1 is r2

    # Checks registry must have at least "C3S-0.1" convention
    assert "C3S-0.1" in r1

    def some_check():
        pass

    # Registering an unexistent check must create the entry in the registry
    r1.add("Inexistent", "some_check", some_check)
    assert "Inexistent" in r1
    assert "some_check" in r1["Inexistent"]
    assert r1["Inexistent"]["some_check"] == some_check

    # After registering a check, they must be in the registry
    r1.add("C3S-0.1", "some_check", some_check)
    r1.add("C3S-0.1", "some_other_check", some_check)
    assert list(r1["C3S-0.1"].keys()) == ["some_check", "some_other_check"]

    def a_different_check_impl():
        pass

    # Updating a check in the registry
    r1.update("C3S-0.1", {"some_check": a_different_check_impl})
    assert r1["C3S-0.1"]["some_check"] == a_different_check_impl
