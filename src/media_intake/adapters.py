from __future__ import annotations

from media_intake.packet import Packet


def render_ai_digest_note(packet: Packet) -> str:
    title = packet.source.source_id
    return f"""---
type: knowledge-inbox
source_type: {packet.source.media_type}
source_platform: {packet.source.platform}
url: "{packet.source.raw}"
source_packet: "{packet.root}"
---

# {title}

## Summary

Write a short synthesis from the packet evidence. Do not rewrite the transcript.

## Key Points

- Extract the main durable idea.
- Note what the visual or audio evidence proves.

## Visual Evidence

Embed only frames that prove or clarify a claim:

```markdown
![Short alt text](<frames/0001.png>)
```

## Classification

- Relevance:
- Actionability:
- Novelty:
- Tags:
- Categories:

## Extracted Tools And Methods

- 

## Source

{packet.source.raw}
"""


def write_profile_outputs(packet: Packet, profile: str) -> list[str]:
    if profile == "generic":
        return []
    if profile == "ai-digest":
        path = packet.root / "ai-digest-note.md"
        path.write_text(render_ai_digest_note(packet), encoding="utf-8")
        return [path.name]
    raise ValueError(f"profile is not implemented yet: {profile}")
