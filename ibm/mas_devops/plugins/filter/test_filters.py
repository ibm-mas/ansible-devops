# -----------------------------------------------------------
# Licensed Materials - Property of IBM
# 5737-M66, 5900-AAA
# (C) Copyright IBM Corp. 2025 All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication, or disclosure
# restricted by GSA ADP Schedule Contract with IBM Corp.
# -----------------------------------------------------------

from filters import *
import pytest


##########################################################################


def test_is_channel_upgrade_path_valid_for_blank_target_channel():
    paths = {'a': ['b', 'c']}
    assert is_channel_upgrade_path_valid('a', '', paths)


def test_is_channel_upgrade_path_valid_for_invalid_target_channel():
    paths = {'a': ['b', 'c']}
    assert not is_channel_upgrade_path_valid('a', 'd', paths)


def test_is_channel_upgrade_path_valid_for_valid_target_channel():
    paths = {'a': ['b', 'c']}
    assert is_channel_upgrade_path_valid('a', 'c', paths)


def test_is_channel_upgrade_path_valid_for_invalid_current_channel():
    paths = {'a': ['b', 'c']}
    assert not is_channel_upgrade_path_valid('d', 'c', paths)


def test_is_channel_upgrade_path_valid_for_string_target_channel():
    paths = {'a': 'b'}
    assert is_channel_upgrade_path_valid('a', 'b', paths)


def test_is_channel_upgrade_path_valid_for_invalid_paths():
    paths = {'a': 1}
    assert not is_channel_upgrade_path_valid('a', 'b', paths)


##########################################################################


def test_get_default_upgrade_channel_for_valid_current_channel():
    paths = {'a': ['b', 'c']}
    assert 'b' == get_default_upgrade_channel('a', paths)


def test_get_default_upgrade_channel_for_string_target_channel():
    paths = {'a': 'b'}
    assert 'b' == get_default_upgrade_channel('a', paths)


def test_get_default_upgrade_channel_for_invalid_current_channel():
    paths = {'a': ['b', 'c']}
    with pytest.raises(KeyError):
        get_default_upgrade_channel('b', paths)


def test_get_default_upgrade_channel_for_invalid_paths():
    paths = {'a': 1}
    assert None == get_default_upgrade_channel('a', paths)


##########################################################################
