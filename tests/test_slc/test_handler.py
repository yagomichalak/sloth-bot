import pytest
from unittest.mock import Mock
import os

# SLC: Sloth Language Class

class TestSlothLanguageClass:
    """ Class for testing the features inside Sloth's
    Language Class system. """

    @pytest.mark.skip(reason="Skipped for testing purposes.")
    def test_one_equals_one(self) -> None:
        """ Testing test that checks whether 1 equals to 1. """

        assert 1 == 1