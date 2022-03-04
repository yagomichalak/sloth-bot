import os
import sys

import pytest
from unittest.mock import Mock

from typing import List, Dict, Union, Optional



# Appends the path of folders 2 folders back, so you can import them
# sys.path.append(
#     os.path.join(
#         os.path.dirname(
#             os.path.realpath(__file__)
#         ), os.pardir, os.pardir
#     )
# )
# print(    os.path.join(
#         os.path.dirname(
#             os.path.realpath(__file__)
#         ), os.pardir, os.pardir
#     ))


# import cogs
# from cogs.teacherfeedback import TeacherFeedback

# SLC: Sloth Language Class
# RUN: pytest --asyncio-mode=auto

class TestSlothLanguageClass:
    """ Class for testing the features inside Sloth's
    Language Class system. """

    

    # @pytest.mark.skip(reason="Not implemented.")
    @pytest.mark.asyncio
    async def test_start_classroom(self) -> None:
        """ Tests the creation of a classroom. """


        from cogs import teacherfeedback

        # teacherfeedback.TeacherFeedback.create_class(member)
        
        #  = Mock()


    @pytest.mark.skip(reason="Not implemented.")
    def test_end_classroom(self) -> None: pass

    @pytest.mark.skip(reason="Not implemented.")
    def test_reward_people(self) -> None: pass

