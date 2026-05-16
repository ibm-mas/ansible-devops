def calculateManageTimeouts(masAppwsComponents):
    """Calculate appropriate timeout values for Manage app configuration.

    Determines delay and retry values based on whether Manage is being configured
    in foundation mode (no components) or full mode (with components). Foundation
    mode uses shorter timeouts since configuration is faster, while full mode uses
    longer timeouts to accommodate the additional time needed for component setup.

    Args:
        masAppwsComponents (dict, optional): Dictionary of Manage components to install.
            Format: {'base': {'version': 'latest'}, 'health': {'version': 'latest'}}.
            None or empty dict indicates foundation mode.

    Returns:
        dict: Dictionary containing 'delay' and 'retries' keys with integer values.
            Foundation mode: delay=240, retries=60 (total ~4 hours)
            Full mode: delay=360, retries=180 (total ~18 hours)
    """
    # Foundation mode: no components or empty dict
    if not masAppwsComponents or len(masAppwsComponents) == 0:
        return {"delay": 240, "retries": 60}

    # Full mode: components are being installed
    return {"delay": 360, "retries": 180}


class FilterModule(object):
    def filters(self):
        return {"calculate_manage_timeouts": calculateManageTimeouts}
