from dataclasses import dataclass

from engine.trust.models import IdentityType, ScopeRef


def _canonical_snowflake(value, field_name):
    text = str(value).strip()
    if not text or not text.isascii() or not text.isdigit():
        raise ValueError(f"{field_name} must be a positive Discord snowflake")

    number = int(text)
    if number <= 0:
        raise ValueError(f"{field_name} must be a positive Discord snowflake")

    return str(number)


def discord_stable_id(user_id):
    return f"discord:user:{_canonical_snowflake(user_id, 'user_id')}"


@dataclass(frozen=True)
class DiscordTrustContext:
    user_id: str
    guild_id: str | None
    channel_id: str | None
    identity_type: IdentityType

    @classmethod
    def from_ids(
        cls,
        user_id,
        guild_id=None,
        channel_id=None,
        *,
        is_bot=False,
    ):
        canonical_user = _canonical_snowflake(user_id, "user_id")
        canonical_guild = (
            _canonical_snowflake(guild_id, "guild_id")
            if guild_id is not None
            else None
        )
        canonical_channel = (
            _canonical_snowflake(channel_id, "channel_id")
            if channel_id is not None
            else None
        )

        if canonical_channel is not None and canonical_guild is None:
            raise ValueError("channel_id requires guild_id")

        return cls(
            user_id=canonical_user,
            guild_id=canonical_guild,
            channel_id=canonical_channel,
            identity_type=(
                IdentityType.SERVICE if is_bot else IdentityType.HUMAN
            ),
        )

    @property
    def stable_id(self):
        return f"discord:user:{self.user_id}"

    @property
    def authorization_scope(self):
        if self.guild_id is not None and self.channel_id is not None:
            return ScopeRef.channel_scope(self.guild_id, self.channel_id)
        if self.guild_id is not None:
            return ScopeRef.guild_scope(self.guild_id)
        return ScopeRef.self_scope(self.stable_id)

    @property
    def memory_scope(self):
        guild_key = (
            f"discord:guild:{self.guild_id}"
            if self.guild_id is not None
            else "discord:dm"
        )
        channel_key = (
            f"discord:channel:{self.channel_id}"
            if self.channel_id is not None
            else f"discord:dm:{self.user_id}"
        )
        return (guild_key, channel_key, self.stable_id)


def bind_discord_identity(trust_service, context):
    return trust_service.ensure_guest(
        context.stable_id,
        identity_type=context.identity_type,
    )
