from ansible.utils.display import Display

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

    # Timing notes:
    # - 240s = 4 minutes
    # - 360s = 6 minutes
    timeoutConfigs = {
        "foundation": {"delay": 240, "retries": 60},  # ~4 hours total
        "base": {"delay": 240, "retries": 60},  # ~4 hours total
        "health": {"delay": 360, "retries": 60},  # ~6 hours total
        "unknown": {"delay": 360, "retries": 180}  # ~18 hours total
    }

    display = Display()
    display.v(f"Estimating configuration timeout for: {masAppwsComponents}")

    if masAppwsComponents is not None and not isinstance(masAppwsComponents, dict):
        raise ValueError("masAppwsComponents must be a dictionary or None")

    if not masAppwsComponents or len(masAppwsComponents) == 0:
        config = "foundation"
    elif set(masAppwsComponents) == set(["base"]):
        config = "base"
    elif set(masAppwsComponents) == set(["base", "health"]):
        config = "health"
    else:
        config = "unknown"

    # Calculate and display timeout information
    formattedDelay = f"{timeoutConfigs[config]['delay'] * timeoutConfigs[config]['retries'] / 3600:.1f}"
    timeoutInfo = f"{timeoutConfigs[config]['retries']} retries with {timeoutConfigs[config]['delay']}s delay (approximately {formattedDelay} hrs)"
    display.v(f"Setting timeout for Manage ({config}): {timeoutInfo}")
    return timeoutConfigs[config]


class FilterModule(object):
    def filters(self):
        return {"calculate_manage_timeouts": calculateManageTimeouts}
