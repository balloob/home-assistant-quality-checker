# geocaching: test-before-configure

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [geocaching](https://www.home-assistant.io/integrations/geocaching/) |
| Rule   | [test-before-configure](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/test-before-configure)                                                     |
| Status | **done**                                       |

## Overview

The `test-before-configure` rule applies to this integration because it is a `cloud_polling` integration that authenticates and connects to the external Geocaching API. The rule requires that the connection and credentials be validated during the configuration flow before a config entry is created.

The `geocaching` integration correctly implements this rule. Since it uses OAuth2 for authentication, the validation does not occur in `async_step_user` but rather in `async_oauth_create_entry`, which is the correct place for OAuth-based flows. This method is called after the user has successfully authenticated with Geocaching and Home Assistant has received an access token.

In `config_flow.py`, the `async_oauth_create_entry` method performs the following steps:
1.  It initializes the `GeocachingApi` client with the newly acquired access token.
2.  It immediately makes an API call to fetch user data: `status = await api.update()`. This call serves as a test to validate that the token is valid and the connection to the service is working.
3.  It inspects the response from the API call to ensure a valid user and username are returned: `if not status.user or not status.user.username:`.
4.  If the API call fails (by raising an exception) or if the returned data is invalid, the flow is aborted (`return self.async_abort(reason="oauth_error")`), preventing a non-functional entry from being created.
5.  Only after the successful API call and data validation does it proceed to create the config entry with `self.async_create_entry(...)`.

This implementation perfectly aligns with the requirements of the `test-before-configure` rule.

```python
# homeassistant/components/geocaching/config_flow.py

    async def async_oauth_create_entry(self, data: dict[str, Any]) -> ConfigFlowResult:
        """Create an oauth config entry or update existing entry for reauth."""
        api = GeocachingApi(
            environment=ENVIRONMENT,
            token=data["token"]["access_token"],
            session=async_get_clientsession(self.hass),
        )
        # The connection is tested here, before creating the entry.
        status = await api.update()
        if not status.user or not status.user.username:
            # The flow is aborted if the test fails.
            return self.async_abort(reason="oauth_error")

        if existing_entry := await self.async_set_unique_id(
            status.user.username.lower()
        ):
            self.hass.config_entries.async_update_entry(existing_entry, data=data)
            await self.hass.config_entries.async_reload(existing_entry.entry_id)
            return self.async_abort(reason="reauth_successful")
        # The entry is only created after a successful test.
        return self.async_create_entry(title=status.user.username, data=data)
```

## Suggestions

No suggestions needed.

---

_Created at 2025-06-25 18:50:14 using gemini-2.5-pro-preview-06-05. Prompt tokens: 5988, Output tokens: 797, Total tokens: 8573._

_Report based on [`f0a78aa`](https://github.com/home-assistant/core/tree/f0a78aadbe1ed91862f40c87da69b37962c1f0d7)._

_AI can be wrong. Always verify the report and the code against the rule._
