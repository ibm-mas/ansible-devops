"""
Reusable external API mocks for testing.

This module provides factory functions to create mock HTTP responses
for external APIs like Fyre.
"""
from unittest.mock import Mock
from typing import Dict, Any, Optional


def create_mock_http_response(
    status_code: int = 200,
    json_data: Optional[Dict[str, Any]] = None,
    text: str = "",
    headers: Optional[Dict[str, str]] = None
) -> Mock:
    """
    Create a mock HTTP response object.

    Args:
        status_code: HTTP status code
        json_data: JSON response data
        text: Response text
        headers: Response headers

    Returns:
        Mock: Mock HTTP response object.
    """
    response = Mock()
    response.status_code = status_code
    response.json.return_value = json_data or {}
    response.text = text
    response.headers = headers or {}
    return response


def create_mock_fyre_response(
    status: str = "success",
    deployed_status: str = "deployed",
    details: str = "Cluster is ready",
    status_code: int = 200
) -> Mock:
    """
    Create a mock Fyre API response.

    Args:
        status: Status field value
        deployed_status: Deployed status field value
        details: Details message
        status_code: HTTP status code

    Returns:
        Mock: Mock Fyre API response.
    """
    json_data = {
        'status': status,
        'details': details
    }

    if deployed_status:
        json_data['deployed_status'] = deployed_status

    return create_mock_http_response(
        status_code=status_code,
        json_data=json_data
    )


def create_mock_fyre_hostname_available_response() -> Mock:
    """
    Create a mock Fyre hostname check response for available hostname.

    Returns:
        Mock: Mock response indicating hostname is available.
    """
    return create_mock_fyre_response(
        status="success",
        deployed_status=None,
        details="Hostname is available"
    )


def create_mock_fyre_hostname_unavailable_response() -> Mock:
    """
    Create a mock Fyre hostname check response for unavailable hostname.

    Returns:
        Mock: Mock response indicating hostname is not available.
    """
    return create_mock_fyre_response(
        status="error",
        deployed_status=None,
        details="Hostname is already in use"
    )


def create_mock_fyre_cluster_deploying_response() -> Mock:
    """
    Create a mock Fyre cluster status response for deploying cluster.

    Returns:
        Mock: Mock response indicating cluster is deploying.
    """
    return create_mock_fyre_response(
        status="success",
        deployed_status="deploying",
        details="Cluster is being deployed"
    )


def create_mock_fyre_cluster_deployed_response() -> Mock:
    """
    Create a mock Fyre cluster status response for deployed cluster.

    Returns:
        Mock: Mock response indicating cluster is deployed.
    """
    return create_mock_fyre_response(
        status="success",
        deployed_status="deployed",
        details="Cluster is deployed and ready"
    )


def create_mock_fyre_cluster_not_exist_response() -> Mock:
    """
    Create a mock Fyre cluster status response for non-existent cluster.

    Returns:
        Mock: Mock response indicating cluster does not exist.
    """
    return create_mock_http_response(
        status_code=400,
        json_data={
            'status': 'error',
            'details': 'Cluster/environment test-cluster does not exist'
        }
    )


def create_mock_fyre_unauthorized_response() -> Mock:
    """
    Create a mock Fyre API response for unauthorized access.

    Returns:
        Mock: Mock response indicating unauthorized access.
    """
    return create_mock_http_response(
        status_code=400,
        json_data={
            'status': 'error',
            'details': 'user testuser NOT authorized to get cluster status for cluster id 12345'
        }
    )


def create_mock_fyre_rate_limited_response() -> Mock:
    """
    Create a mock Fyre API response for rate limiting.

    Returns:
        Mock: Mock response indicating rate limiting.
    """
    return create_mock_http_response(
        status_code=423,
        json_data={
            'status': 'error',
            'details': 'user testuser (id 12345) blocked at 2025-10-20 05:50:30 until 2025-10-20 09:50:30 due to too many requests that resulted in an error'
        }
    )


def create_mock_http_error_response(
    status_code: int = 500,
    message: str = "Internal Server Error"
) -> Mock:
    """
    Create a mock HTTP error response.

    Args:
        status_code: HTTP error status code
        message: Error message

    Returns:
        Mock: Mock HTTP error response.
    """
    return create_mock_http_response(
        status_code=status_code,
        json_data={
            'status': 'error',
            'details': message
        }
    )

# Made with Bob
