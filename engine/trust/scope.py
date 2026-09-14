from engine.trust.models import Capability, ScopeRef


def parse_capability(value):
    normalized = value.strip().lower()
    for capability in Capability:
        if capability.value == normalized:
            return capability
    return None


def parse_scope(value, actor_id):
    text = value.strip()
    lowered = text.lower()

    if lowered == "global":
        return ScopeRef.global_scope()

    if lowered == "self":
        return ScopeRef.self_scope(actor_id)

    if lowered.startswith("guild:"):
        guild_id = text.split(":", 1)[1].strip()
        if guild_id:
            return ScopeRef.guild_scope(guild_id)
        return None

    if lowered.startswith("channel:"):
        payload = text.split(":", 1)[1]
        if ":" not in payload:
            return None
        guild_id, channel_id = payload.split(":", 1)
        guild_id = guild_id.strip()
        channel_id = channel_id.strip()
        if guild_id and channel_id:
            return ScopeRef.channel_scope(guild_id, channel_id)

    return None
