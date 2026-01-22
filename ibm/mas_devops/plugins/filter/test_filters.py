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


##########################################################################
# Tests for set_storage_class_name


def test_set_storage_class_name_with_rwx_access_mode():
    """Test that ReadWriteMany access mode sets RWX storage class"""
    storage_data = [
        {
            'name': 'meta',
            'spec': {
                'accessModes': ['ReadWriteMany'],
                'resources': {'requests': {'storage': '20Gi'}},
                'storageClassName': 'nfs-client'
            },
            'type': 'create'
        }
    ]
    result = set_storage_class_name(storage_data, 'rwo-class', 'rwx-class')
    assert result[0]['spec']['storageClassName'] == 'rwx-class'


def test_set_storage_class_name_with_rwo_access_mode():
    """Test that ReadWriteOnce access mode sets RWO storage class"""
    storage_data = [
        {
            'name': 'data',
            'spec': {
                'accessModes': ['ReadWriteOnce'],
                'resources': {'requests': {'storage': '10Gi'}},
                'storageClassName': 'default'
            },
            'type': 'create'
        }
    ]
    result = set_storage_class_name(storage_data, 'rwo-class', 'rwx-class')
    assert result[0]['spec']['storageClassName'] == 'rwo-class'


def test_set_storage_class_name_with_multiple_items():
    """Test processing multiple storage items with different access modes"""
    storage_data = [
        {
            'name': 'meta',
            'spec': {
                'accessModes': ['ReadWriteMany'],
                'storageClassName': 'old-class'
            }
        },
        {
            'name': 'data',
            'spec': {
                'accessModes': ['ReadWriteOnce'],
                'storageClassName': 'old-class'
            }
        }
    ]
    result = set_storage_class_name(storage_data, 'rwo-class', 'rwx-class')
    assert result[0]['spec']['storageClassName'] == 'rwx-class'
    assert result[1]['spec']['storageClassName'] == 'rwo-class'


def test_set_storage_class_name_with_empty_list():
    """Test that empty list returns empty list"""
    storage_data = []
    result = set_storage_class_name(storage_data, 'rwo-class', 'rwx-class')
    assert result == []


def test_set_storage_class_name_with_missing_spec():
    """Test that items without spec field are skipped"""
    storage_data = [
        {'name': 'invalid', 'type': 'create'},
        {
            'name': 'valid',
            'spec': {
                'accessModes': ['ReadWriteMany'],
                'storageClassName': 'old-class'
            }
        }
    ]
    result = set_storage_class_name(storage_data, 'rwo-class', 'rwx-class')
    assert len(result) == 2
    assert 'spec' not in result[0]
    assert result[1]['spec']['storageClassName'] == 'rwx-class'


def test_set_storage_class_name_with_missing_access_modes():
    """Test that items without accessModes are skipped"""
    storage_data = [
        {
            'name': 'invalid',
            'spec': {
                'storageClassName': 'old-class'
            }
        }
    ]
    result = set_storage_class_name(storage_data, 'rwo-class', 'rwx-class')
    assert result[0]['spec']['storageClassName'] == 'old-class'


def test_set_storage_class_name_with_non_list_access_modes():
    """Test that items with non-list accessModes are skipped"""
    storage_data = [
        {
            'name': 'invalid',
            'spec': {
                'accessModes': 'ReadWriteMany',
                'storageClassName': 'old-class'
            }
        }
    ]
    result = set_storage_class_name(storage_data, 'rwo-class', 'rwx-class')
    assert result[0]['spec']['storageClassName'] == 'old-class'


def test_set_storage_class_name_with_missing_storage_class_name():
    """Test that items without storageClassName are skipped"""
    storage_data = [
        {
            'name': 'invalid',
            'spec': {
                'accessModes': ['ReadWriteMany']
            }
        }
    ]
    result = set_storage_class_name(storage_data, 'rwo-class', 'rwx-class')
    assert 'storageClassName' not in result[0]['spec']


def test_set_storage_class_name_with_empty_access_modes_list():
    """Test that items with empty accessModes list cause IndexError"""
    storage_data = [
        {
            'name': 'invalid',
            'spec': {
                'accessModes': [],
                'storageClassName': 'old-class'
            }
        }
    ]
    # This will raise IndexError due to accessing [0] on empty list
    with pytest.raises(IndexError):
        set_storage_class_name(storage_data, 'rwo-class', 'rwx-class')


def test_set_storage_class_name_with_read_write_once_pod():
    """Test that ReadWriteOncePod access mode sets RWO storage class"""
    storage_data = [
        {
            'name': 'data',
            'spec': {
                'accessModes': ['ReadWriteOncePod'],
                'storageClassName': 'old-class'
            }
        }
    ]
    result = set_storage_class_name(storage_data, 'rwo-class', 'rwx-class')
    assert result[0]['spec']['storageClassName'] == 'rwo-class'


def test_set_storage_class_name_with_read_only_many():
    """Test that ReadOnlyMany access mode sets RWO storage class (not RWX)"""
    storage_data = [
        {
            'name': 'data',
            'spec': {
                'accessModes': ['ReadOnlyMany'],
                'storageClassName': 'old-class'
            }
        }
    ]
    result = set_storage_class_name(storage_data, 'rwo-class', 'rwx-class')
    assert result[0]['spec']['storageClassName'] == 'rwo-class'


def test_set_storage_class_name_preserves_other_fields():
    """Test that other fields in storage items are preserved"""
    storage_data = [
        {
            'name': 'meta',
            'spec': {
                'accessModes': ['ReadWriteMany'],
                'resources': {'requests': {'storage': '20Gi'}},
                'storageClassName': 'old-class',
                'volumeMode': 'Filesystem'
            },
            'type': 'create',
            'custom_field': 'value'
        }
    ]
    result = set_storage_class_name(storage_data, 'rwo-class', 'rwx-class')
    assert result[0]['name'] == 'meta'
    assert result[0]['type'] == 'create'
    assert result[0]['custom_field'] == 'value'
    assert result[0]['spec']['resources'] == {'requests': {'storage': '20Gi'}}
    assert result[0]['spec']['volumeMode'] == 'Filesystem'
    assert result[0]['spec']['storageClassName'] == 'rwx-class'


##########################################################################
