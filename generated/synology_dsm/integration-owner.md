```markdown
# synology_dsm: integration-owner

| Info   | Value                                                                    |
|--------|--------------------------------------------------------------------------|
| Name   | [synology_dsm](https://www.home-assistant.io/integrations/synology_dsm/) |
| Rule   | [integration-owner](https://developers.home-assistant.io/docs/core/integration-quality-scale/rules/integration-owner) |
| Status | **done**                                                                 |
| Reason |                                                                          |

## Overview

The `integration-owner` rule requires an integration to list one or more GitHub usernames in the `codeowners` field within its `manifest.json` file. This signifies that individuals have taken responsibility for maintaining the integration and will be notified of relevant issues and pull requests.

This rule applies to the `synology_dsm` integration as it is a standard integration within Home Assistant.

Upon reviewing the provided code, specifically the `homeassistant/components/synology_dsm/manifest.json` file, the integration correctly includes the `codeowners` field with a list of GitHub usernames:

```json
{
  "domain": "synology_dsm",
  "name": "Synology DSM",
  "codeowners": ["@hacf-fr", "@Quentame", "@mib1185"],
  // ... rest of the manifest
}
```

The presence of the `"codeowners": ["@hacf-fr", "@Quentame", "@mib1185"]` entry with multiple valid GitHub usernames indicates that the integration fully complies with the `integration-owner` rule.

## Suggestions

No suggestions needed. The integration already meets the requirements of this rule.
```

_Created at 2025-05-25 11:48:30. Prompt tokens: 39378, Output tokens: 382, Total tokens: 40088_
