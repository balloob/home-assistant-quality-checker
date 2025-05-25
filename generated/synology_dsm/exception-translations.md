```markdown
# synology_dsm: exception-translations

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [exception-translations](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/exception-translations)                                                     |
| Status | **todo**                                                                 |

## Overview

This rule requires that user-facing error messages originating from exceptions inherit `HomeAssistantError` (or a subclass) and utilize `translation_domain` and `translation_key` for translatability, with corresponding entries in the `exceptions` section of `strings.json`.

The `synology_dsm` integration uses several subclasses of `HomeAssistantError` for different failure scenarios, such as `ConfigEntryNotReady`, `ConfigEntryAuthFailed`, `UpdateFailed`, `BrowseError`, and `Unresolvable`. However, it currently raises these exceptions by passing a direct string message (or an f-string containing dynamic details) to the exception constructor, rather than using the `translation_domain` and `translation_key` parameters.

Specific examples include:

*   In `homeassistant/components/synology_dsm/__init__.py`, `ConfigEntryNotReady` is raised with a `details` string derived from the underlying Synology API exception (e.g., `raise ConfigEntryNotReady(details) from err`).
*   In `homeassistant/components/synology_dsm/common.py`, `ConfigEntryAuthFailed` is raised with an f-string containing connection/authentication details (e.g., `raise ConfigEntryAuthFailed(f"reason: {details}") from err`).
*   In `homeassistant/components/synology_dsm/coordinator.py`, `UpdateFailed` is raised with an f-string containing the API communication error (e.g., `raise UpdateFailed(f"Error communicating with API: {err}") from err` and `raise UpdateFailed(f"Error communicating with API: {err}") from err`).
*   In `homeassistant/components/synology_dsm/media_source.py`, `BrowseError` and `Unresolvable` are raised with direct string messages (e.g., `raise BrowseError("Diskstation not initialized")`, `raise Unresolvable("No album id")`, etc.).

Additionally, the `homeassistant/components/synology_dsm/strings.json` file currently lacks the required `"exceptions": {}` section to define translatable keys for these error messages.

Because the integration raises translatable `HomeAssistantError` subclasses without providing translation keys and doesn't have the necessary `strings.json` structure, it does not comply with the `exception-translations` rule.

## Suggestions

To make the `synology_dsm` integration compliant with the `exception-translations` rule, follow these steps:

1.  **Add an `exceptions` section to `homeassistant/components/synology_dsm/strings.json`**: This section will hold the translation keys and messages for exceptions.

    ```json
    {
      ...
      "exceptions": {
        "config_entry_not_ready": {
          "message": "Synology DSM is not ready. Details: {details}"
        },
        "auth_failed": {
          "message": "Authentication failed. Reason: {details}"
        },
        "update_failed": {
          "message": "Error communicating with API during update: {error}"
        },
        "browse_diskstation_not_initialized": {
          "message": "Diskstation is not initialized"
        },
        "unresolvable_no_album_id": {
          "message": "No album id"
        },
        "unresolvable_no_file_name": {
          "message": "No file name"
        },
        "unresolvable_no_file_extension": {
          "message": "No file extension"
        }
      },
      ...
    }
    ```
    Adjust the messages and placeholders (`{details}`, `{error}`) as needed based on what information is useful to the user.

2.  **Modify exception raising in `homeassistant/components/synology_dsm/__init__.py`**:
    Change:
    ```python
    except (*SYNOLOGY_CONNECTION_EXCEPTIONS, SynologyDSMNotLoggedInException) as err:
        # ...
        details = EXCEPTION_UNKNOWN # or err.args[0].get(...)
        raise ConfigEntryNotReady(details) from err
    ```
    To use a translation key, potentially with `details` as a placeholder:
    ```python
    except (*SYNOLOGY_CONNECTION_EXCEPTIONS, SynologyDSMNotLoggedInException) as err:
        # ...
        details = EXCEPTION_UNKNOWN # or err.args[0].get(...)
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="config_entry_not_ready",
            translation_placeholders={"details": str(details)}, # Ensure details is a string
        ) from err
    ```

3.  **Modify exception raising in `homeassistant/components/synology_dsm/common.py`**:
    Change:
    ```python
    raise ConfigEntryAuthFailed(f"reason: {details}") from err
    ```
    To use a translation key with `details` as a placeholder:
    ```python
    raise ConfigEntryAuthFailed(
        translation_domain=DOMAIN,
        translation_key="auth_failed",
        translation_placeholders={"details": str(details)}, # Ensure details is a string
    ) from err
    ```

4.  **Modify exception raising in `homeassistant/components/synology_dsm/coordinator.py`**:
    Change:
    ```python
    raise UpdateFailed(f"Error communicating with API: {err}") from err
    ```
    To use a translation key with the low-level error `err` as a placeholder:
    ```python
    raise UpdateFailed(
        translation_domain=DOMAIN,
        translation_key="update_failed",
        translation_placeholders={"error": str(err)}, # Ensure error is a string
    ) from err
    ```
    Apply this change to both places where `UpdateFailed` is raised with this message.

5.  **Modify exception raising in `homeassistant/components/synology_dsm/media_source.py`**:
    Change:
    ```python
    raise BrowseError("Diskstation not initialized")
    ```
    To use a translation key:
    ```python
    raise BrowseError(
        translation_domain=DOMAIN,
        translation_key="browse_diskstation_not_initialized",
    )
    ```
    Change:
    ```python
    raise Unresolvable("No album id")
    # Similarly for "No file name" and "No file extension"
    ```
    To use translation keys:
    ```python
    raise Unresolvable(
        translation_domain=DOMAIN,
        translation_key="unresolvable_no_album_id",
    )
    # Similarly for other Unresolvable errors with their respective keys
    ```

By implementing these changes, the error messages displayed to the user will be translatable according to the Home Assistant translation system.
```

_Created at 2025-05-25 11:51:38. Prompt tokens: 39549, Output tokens: 1660, Total tokens: 43882_
