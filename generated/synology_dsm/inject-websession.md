```markdown
# synology_dsm: inject-websession

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [inject-websession](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/inject-websession)                                                     |
| Status | **done**                                                                 |

## Overview

This rule requires that integrations making HTTP requests use `aiohttp` or `httpx` and inject a `websession` obtained from Home Assistant's helpers into their underlying client library.

The `synology_dsm` integration communicates with a Synology NAS, which involves making HTTP/HTTPS requests. Therefore, this rule is applicable.

The integration utilizes `aiohttp` as its HTTP library, specifically by leveraging Home Assistant's `async_get_clientsession` helper function. The obtained `websession` is correctly passed as the first argument to the constructor of the `SynologyDSM` client library.

This pattern is consistently applied in both the `async_setup` function within `__init__.py` (via the `SynoApi` class) and the `async_validate_input_create_entry` method in `config_flow.py`:

In `homeassistant/components/synology_dsm/common.py`:
```python
session = async_get_clientsession(self._hass, self._entry.data[CONF_VERIFY_SSL])
self.dsm = SynologyDSM(
    session, # <-- websession is passed here
    self._entry.data[CONF_HOST],
    ...
)
```

In `homeassistant/components/synology_dsm/config_flow.py`:
```python
session = async_get_clientsession(self.hass, verify_ssl)
api = SynologyDSM(
    session, host, port, username, password, use_ssl, timeout=DEFAULT_TIMEOUT # <-- websession is passed here
)
```

By following this pattern, the integration correctly integrates with Home Assistant's session management, allowing for efficient resource utilization and adherence to the `inject-websession` rule.

## Suggestions

No suggestions needed.
```

_Created at 2025-05-25 11:53:00. Prompt tokens: 39396, Output tokens: 516, Total tokens: 40632_
