# synology_dsm: discovery

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [discovery](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/discovery)                                                     |
| Status | **done**                                                                 |

## Overview

This rule encourages integrations to implement discovery mechanisms for devices that support it, improving user experience by simplifying setup. Synology DSM devices are typically discoverable on the local network via protocols like SSDP and mDNS (Zeroconf).

The `synology_dsm` integration fully complies with this rule by implementing discovery using both SSDP and Zeroconf:

1.  **Manifest Configuration:** The `homeassistant/components/synology_dsm/manifest.json` file explicitly declares support for both discovery methods:
    ```json
    "ssdp": [
      {
        "manufacturer": "Synology",
        "deviceType": "urn:schemas-upnp-org:device:Basic:1"
      }
    ],
    "zeroconf": [
      {
        "type": "_http._tcp.local.",
        "properties": {
          "vendor": "synology*"
        }
      }
    ]
    ```
    This configuration allows Home Assistant to automatically detect Synology devices broadcasting their presence using these protocols.

2.  **Config Flow Implementation:** The `homeassistant/components/synology_dsm/config_flow.py` handles the discovery information received by Home Assistant:
    *   The `SynologyDSMFlowHandler` class includes an `async_step_zeroconf` method that processes discovery information from Zeroconf. It extracts the host, name, and MAC address (`discovery_info`).
    *   It also includes an `async_step_ssdp` method that processes discovery information from SSDP. It extracts the host and MAC address from the `SsdpServiceInfo`.
    *   Both discovery steps delegate the actual handling to a shared helper method, `_async_from_discovery`. This method checks if the discovered device (identified by its MAC address as the unique ID) is already configured and handles potential host IP updates or initiates the `link` step (`async_step_link`) to complete the configuration for new discoveries.

By leveraging both SSDP and Zeroconf discovery and implementing the necessary config flow steps, the `synology_dsm` integration makes it easy for users to find and set up their Synology NAS devices without manually entering connection details. This demonstrates full compliance with the `discovery` rule.

_Created at 2025-05-25 11:49:37. Prompt tokens: 40077, Output tokens: 600, Total tokens: 41416_
