# tilt_pi: discovery-update-info

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [tilt_pi](https://www.home-assistant.io/integrations/tilt_pi/) |
| Rule   | [discovery-update-info](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/discovery-update-info)                                                     |
| Status | **exempt**                                       |
| Reason | The integration does not support discovery. This rule only applies to integrations that discover devices on the network. |

## Overview

The `discovery-update-info` rule requires that integrations using discovery mechanisms (like Zeroconf, SSDP, or DHCP) are able to update the network information (e.g., IP address) of an already configured device when it is re-discovered.

This rule is not applicable to the `tilt_pi` integration because it does not implement any discovery features. The integration's configuration flow relies entirely on the user providing the network address of the Tilt Pi instance manually.

This can be verified by examining the integration's code:
1.  **`manifest.json`**: The manifest file does not declare any discovery helpers. There are no keys for `zeroconf`, `ssdp`, or `dhcp`.
2.  **`config_flow.py`**: The configuration flow only implements the `async_step_user` method. It does not contain any discovery handlers like `async_step_zeroconf` or `async_step_ssdp`. The user is prompted to enter a URL, and the integration attempts to connect to the host provided in that URL.

Since the integration does not discover devices, it cannot fulfill the requirement of updating device information from a discovery event. Therefore, it is exempt from this rule.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 18:54:19 using gemini-2.5-pro-preview-06-05. Prompt tokens: 4332, Output tokens: 409, Total tokens: 6407._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
