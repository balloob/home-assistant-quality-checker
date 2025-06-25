# altruist: reauthentication-flow
| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [altruist](https://www.home-assistant.io/integrations/altruist/) |
| Rule   | [reauthentication-flow](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/reauthentication-flow)                                                     |
| Status | **exempt**                                       |
| Reason | The integration connects to a local device via its IP address and does not use any authentication credentials like API keys or passwords. |

## Overview
The `reauthentication-flow` rule requires integrations to implement a UI flow for users to update their credentials (like a password or API token) if they become invalid.

This rule does not apply to the `altruist` integration. The integration connects to a local device and identifies it solely by its IP address or hostname. As seen in the `config_flow.py`, the only piece of information requested from the user and stored in the config entry is the host:

`config_flow.py`:
```python
# ...
                return self.async_create_entry(
                    title=self.device.id,
                    data={
                        CONF_HOST: ip_address,
                    },
                )
# ...
```

The integration does not use any passwords, API tokens, or other forms of credentials that could be changed by the user and would necessitate a reauthentication flow. According to the rule's exception: "If the integration doesn't require any form of authentication, this rule doesn't apply."

Since authentication is based on network reachability of the `CONF_HOST` and not on credentials, this rule is not applicable. If the device's IP address changes, that would be a case for a `reconfiguration-flow`, not a `reauthentication-flow`.

## Suggestions
No suggestions needed.

---

_Created at 2025-06-25 18:51:42 using gemini-2.5-pro-preview-06-05. Prompt tokens: 6919, Output tokens: 422, Total tokens: 8579._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
