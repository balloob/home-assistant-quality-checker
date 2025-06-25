# tilt_pi: discovery

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [tilt_pi](https://www.home-assistant.io/integrations/tilt_pi/) |
| Rule   | [discovery](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/discovery)                                                     |
| Status | **todo**                                                                 |

## Overview

The `discovery` rule applies to this integration because `tilt_pi` connects to a Tilt Pi device, which is a network-attached service. Devices running on a local network can typically be discovered using protocols like mDNS (Zeroconf) or SSDP, which greatly improves the user experience by eliminating the need for manual configuration.

The `tilt_pi` integration currently does not follow this rule. The setup process relies entirely on manual user input. As seen in `config_flow.py`, the integration only implements `async_step_user`, which requires the user to provide the full URL of the Tilt Pi instance.

```python
# homeassistant/components/tilt_pi/config_flow.py

# ...
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a configuration flow initialized by the user."""

        errors = {}
        if user_input is not None:
            url = URL(user_input[CONF_URL])
            # ... manual parsing and connection check ...
```

Additionally, the `manifest.json` file is missing any discovery-related keys (e.g., `zeroconf` or `ssdp`), which are necessary for Home Assistant to listen for device announcements. By implementing discovery, Home Assistant could automatically detect Tilt Pi instances on the network and present them to the user for easy, one-click setup.

## Suggestions

To comply with this rule, the integration should be updated to support discovery via mDNS (Zeroconf), which is a common method for Raspberry Pi-based projects like Tilt Pi.

### 1. Update `manifest.json`

Add a `zeroconf` key to `manifest.json` to tell Home Assistant which mDNS service type to look for.

**Note:** The service name `_tiltpi._tcp.local.` is a suggestion for a specific service. If the Tilt Pi project advertises a more generic service (like `_http._tcp.local.`), that should be used instead. This should be verified with the Tilt Pi project's documentation or implementation.

```json
// homeassistant/components/tilt_pi/manifest.json
{
  "domain": "tilt_pi",
  "name": "Tilt Pi",
  "codeowners": ["@michaelheyman"],
  "config_flow": true,
  "documentation": "https://www.home-assistant.io/integrations/tilt_pi",
  "iot_class": "local_polling",
  "quality_scale": "bronze",
  "requirements": ["tilt-pi==0.2.1"],
  "zeroconf": ["_tiltpi._tcp.local."]
}
```

### 2. Update `config_flow.py`

Implement the `async_step_zeroconf` and `async_step_discovery_confirm` methods in the `TiltPiConfigFlow` class. This will handle the discovery and user confirmation process.

```python
# homeassistant/components/tilt_pi/config_flow.py

from typing import Any

import aiohttp
from tiltpi import TiltPiClient, TiltPiError
import voluptuous as vol
from yarl import URL

from homeassistant.components import zeroconf
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_URL
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN


class TiltPiConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tilt Pi."""

    # Add properties to store discovered data
    _discovered_host: str
    _discovered_port: int

    async def _check_connection(self, host: str, port: int) -> str | None:
        """Check if we can connect to the TiltPi instance."""
        client = TiltPiClient(
            host,
            port,
            session=async_get_clientsession(self.hass),
        )
        try:
            await client.get_hydrometers()
        except (TiltPiError, TimeoutError, aiohttp.ClientError):
            return "cannot_connect"
        return None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle a configuration flow initialized by the user."""

        errors = {}
        if user_input is not None:
            url = URL(user_input[CONF_URL])
            if (host := url.host) is None:
                errors[CONF_URL] = "invalid_host"
            else:
                self._async_abort_entries_match({CONF_HOST: host})
                port = url.port
                assert port
                error = await self._check_connection(host=host, port=port)
                if error:
                    errors["base"] = error
                else:
                    return self.async_create_entry(
                        title="Tilt Pi",
                        data={
                            CONF_HOST: host,
                            CONF_PORT: port,
                        },
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_URL): str}),
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle a flow initiated by zeroconf discovery."""
        host = discovery_info.host
        port = discovery_info.port

        self._async_abort_entries_match({CONF_HOST: host})
        
        # Test connection before showing the confirmation form
        error = await self._check_connection(host, port)
        if error:
            return self.async_abort(reason=error)
            
        self._discovered_host = host
        self._discovered_port = port

        self.context["title_placeholders"] = {"name": f"Tilt Pi at {host}"}
        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle user confirmation of a discovered device."""
        if user_input is not None:
            return self.async_create_entry(
                title="Tilt Pi",
                data={
                    CONF_HOST: self._discovered_host,
                    CONF_PORT: self._discovered_port,
                },
            )
        
        self._set_confirm_only()
        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders={"name": f"Tilt Pi at {self._discovered_host}"},
        )
```

By making these changes, the `tilt_pi` integration will automatically discover devices, significantly improving usability and adhering to the quality scale standards.

---

_Created at 2025-06-25 18:53:57 using gemini-2.5-pro-preview-06-05. Prompt tokens: 4731, Output tokens: 1703, Total tokens: 9801._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
