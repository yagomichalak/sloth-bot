import pytest
from unittest.mock import Mock
import os
from typing import List, Dict, Union, Optional
from tests.data import users

from cogs.teacherfeedback import TeacherFeedback

# SLC: Sloth Language Class

class TestSlothLanguageClass:
    """ Class for testing the features inside Sloth's
    Language Class system. """

    @pytest.mark.skip(reason="Not implemented.")
    def test_start_classroom(self) -> None:
        """ Tests the creation of a classroom. """

        # TeacherFeedback.create_class = Mock()
        pass

    @pytest.mark.skip(reason="Not implemented.")
    def test_end_classroom(self) -> None: pass

    @pytest.mark.skip(reason="Not implemented.")
    def test_reward_people(self) -> None: pass

