import pandas as pd

from src.fremtpl2.frequency import FORMULA
from src.fremtpl2.preprocessing import split_train_validation_test


def test_policy_id_is_not_a_feature_and_offset_is_declared():
    assert "IDpol" not in FORMULA


def test_policy_splits_are_disjoint():
    frame = pd.DataFrame({"IDpol": range(100)})
    train, validation, test = split_train_validation_test(frame)
    assert not set(train.IDpol) & set(validation.IDpol)
    assert not set(train.IDpol) & set(test.IDpol)
    assert not set(validation.IDpol) & set(test.IDpol)
