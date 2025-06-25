# geocaching: config-flow

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [geocaching](https://www.home-assistant.io/integrations/geocaching/) |
| Rule   | [config-flow](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/config-flow)                                                     |
| Status | **done**                                                                 |
| Reason |                                                                          |

## Overview

The `config-flow` rule applies to this integration as it requires user authentication (via OAuth2) to connect to the Geocaching cloud service.

The integration fully follows this rule by providing a complete and robust configuration flow for setting it up via the user interface.

- **Manifest:** The `manifest.json` file correctly enables the feature by setting `"config_flow": true`.
- **Config Flow Implementation:** The integration includes a `config_flow.py` file. It leverages the standard `AbstractOAuth2FlowHandler` which is the recommended practice for integrations using OAuth2. This handler manages the standard flow steps, such as picking an implementation and redirecting the user to the provider for authorization.
- **Strings:** A `strings.json` file is present and contains the necessary translations for the UI, including steps like `pick_implementation` and `reauth_confirm`. It correctly uses placeholders to reference common translations (e.g., `[%key:common::config_flow::abort::already_configured_account%]`).
- **Validation and Unique ID:** In `config_flow.py`, the `async_oauth_create_entry` method successfully validates the received credentials by making an API call (`await api.update()`). It then uses the returned username to set a `unique_id`, preventing duplicate configurations for the same account.
- **Reauthentication:** The flow correctly implements `async_step_reauth` and `async_step_reauth_confirm` to handle token expiration and guide the user through re-authentication.

The implementation is a modern, standard example of an OAuth2-based config flow in Home Assistant.

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 18:48:29 using gemini-2.5-pro-preview-06-05. Prompt tokens: 6072, Output tokens: 471, Total tokens: 8603._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
