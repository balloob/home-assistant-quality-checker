# devolo_home_control: test-before-setup

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [devolo_home_control](https://www.home-assistant.io/integrations/devolo_home_control/) |
| Rule   | [test-before-setup](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/test-before-setup)                                                     |
| Status | **done**                                                                 |

## Overview

The `test-before-setup` rule requires that an integration verifies it can connect to the device or service and be set up correctly during initialization, raising appropriate exceptions to inform the user of any issues. This rule applies to the `devolo_home_control` integration as it uses a config entry to manage its setup process.

The integration fully complies with this rule by performing several checks within its `async_setup_entry` function in `__init__.py`.

1.  **Authentication and Maintenance Check:**
    The integration calls the `check_mydevolo_and_get_gateway_ids` helper function. This function performs two critical checks against the mydevolo cloud service:
    *   It verifies user credentials by calling `mydevolo.credentials_valid()`. If they are incorrect, it raises `ConfigEntryAuthFailed`, which correctly prompts the user for reauthentication.
    *   It checks if the service is in maintenance mode via `mydevolo.maintenance()`. If it is, it raises `ConfigEntryNotReady`, signaling a temporary issue that Home Assistant should retry later.

    ```python
    # homeassistant/components/devolo_home_control/__init__.py
    def check_mydevolo_and_get_gateway_ids(mydevolo: Mydevolo) -> list[str]:
        """Check if the credentials are valid and return user's gateway IDs as long as mydevolo is not in maintenance mode."""
        if not mydevolo.credentials_valid():
            raise ConfigEntryAuthFailed(
                translation_domain=DOMAIN,
                translation_key="invalid_auth",
            )
        if mydevolo.maintenance():
            raise ConfigEntryNotReady(
                translation_domain=DOMAIN,
                translation_key="maintenance",
            )
    
        return mydevolo.get_gateway_ids()
    ```

2.  **Gateway Connectivity Check:**
    After retrieving the gateway IDs, the integration attempts to establish a connection with each gateway by instantiating the `HomeControl` class from the underlying API. This operation is wrapped in a `try...except` block. If a gateway is offline, the API raises a `GatewayOfflineError`. The integration correctly catches this exception and raises `ConfigEntryNotReady`, informing the user that the connection failed and that Home Assistant will retry.

    ```python
    # homeassistant/components/devolo_home_control/__init__.py
    try:
        # ...
        for gateway_id in gateway_ids:
            entry.runtime_data.append(
                await hass.async_add_executor_job(
                    partial(
                        HomeControl,
                        # ...
                    )
                )
            )
    except GatewayOfflineError as err:
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="connection_failed",
            translation_placeholders={"gateway_id": gateway_id},
        ) from err
    ```

By implementing these checks, the integration ensures that setup proceeds only when authentication is successful and devices are reachable, providing immediate and clear feedback to the user in case of failure. This adheres perfectly to the `test-before-setup` rule.

---

_Created at 2025-06-25 19:01:12 using gemini-2.5-pro-preview-06-05. Prompt tokens: 13342, Output tokens: 838, Total tokens: 16870._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
