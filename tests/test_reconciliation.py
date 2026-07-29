def test_alternate_apra_tables_are_not_additive():
    report_cuts = {"claims_by_state_loi", "claims_by_state_eda"}
    selected_basis = "claims_by_state_loi"
    assert selected_basis in report_cuts
    assert sum(name == selected_basis for name in report_cuts) == 1
