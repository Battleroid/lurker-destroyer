import argparse
from datetime import datetime, timedelta

import discord


class Lurker(discord.Client):
    def __init__(self, *args, **kwargs):
        self.target_server = kwargs["server"]
        self.target_role = kwargs["role"]
        self.cutoff_date = datetime.now() - timedelta(days=kwargs["cutoff"])
        self.target_limit_role = kwargs.get("limit_role")
        self.for_real = kwargs["for_real"]
        self.message_limit = kwargs["message_limit"]
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        dry_run = "[DRY RUN] " if not self.for_real else ""
        server = self.get_guild(self.target_server)
        role = server.get_role(self.target_role)
        if self.target_limit_role:
            limit_role = server.get(self.target_limit_role)
        print(f"{dry_run}Cutoff date is {self.cutoff_date}")
        print(f'{dry_run}Targeting server: {self.target_server} - "{server.name}"')
        print(f'{dry_run}Applying role to users: {self.target_role} - "{role.name}"')
        print(f"{dry_run}Searching for users and last messages ...")
        if self.target_limit_role:
            print(f'{dry_run}Only targeting users with the "{limit_role.name}" role')

        # Get last message for each user in channel
        last_messages = {}
        for channel in server.text_channels:
            print(f"Looking in channel {channel.name} ...")
            async for message in channel.history(limit=self.message_limit):
                # If last message for the author is newer than what we have, reset to that message
                last_messages.setdefault(message.author, message)
                if message.created_at > last_messages[message.author].created_at:
                    print(
                        f"Reset last message for {message.author} to {message.created_at}"
                    )
                    last_messages[message.author] = message

        too_old = []
        for author, message in last_messages.items():
            if author.bot:
                print(f"Skipping {author.name} bot ...")
                continue
            if self.target_limit_role:
                if limit_role not in author.roles:
                    print(f"Skipping {author.name}, missing limit role ...")
                    continue
            if message.created_at < self.cutoff_date:
                expired = (self.cutoff_date - message.created_at).days
                print(
                    f"{author.name} will be cut, last message was {expired.days} days before cutoff ({message.created_at}: {message.content}"
                )
                too_old.append(author)

        for author in too_old:
            if self.target_limit_role:
                print(f"{dry_run}Kicking {author.name}")
                if self.for_real:
                    await author.kick()
            else:
                print(f"{dry_run}Applying role to {author.name}")
                if self.for_real:
                    await author.add_roles(role, reason="Lurker")

        await self.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("TOKEN", type=str)
    parser.add_argument("SERVER_ID", type=int)
    parser.add_argument("ROLE_ID", type=int, help="Role to apply")
    parser.add_argument("--limit-role", type=int, help="Role to target")
    parser.add_argument("--day-cutoff", type=int, default=180, help="Day delta cutoff")
    parser.add_argument(
        "--message-limit",
        type=int,
        default=100000,
        help="Number of messages to go back for each channel",
    )
    parser.add_argument(
        "--for-real",
        default=False,
        action="store_true",
        help="Really kick or add roles",
    )
    args = parser.parse_args()
    intents = discord.Intents.default()
    intents.guilds = True
    intents.members = True
    intents.messages = True
    intents.guild_messages = True
    lurker = Lurker(
        server=args.SERVER_ID,
        role=args.ROLE_ID,
        cutoff=args.day_cutoff,
        limit_role=args.limit_role,
        for_real=args.for_real,
        message_limit=args.message_limit,
        intents=intents,
    )
    lurker.run(args.TOKEN)
