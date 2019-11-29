from discord import Embed
from resources.structures.Bloxlink import Bloxlink # pylint: disable=import-error
from resources.exceptions import Message, UserNotVerified # pylint: disable=import-error

update_member = Bloxlink.get_module("roblox", attrs=["update_member"])
parse_message = Bloxlink.get_module("commands", attrs="parse_message")


@Bloxlink.command
class GetRoleCommand(Bloxlink.Module):
	"""retrieves your bound roles"""

	def __init__(self):
		self.aliases = ["getroles", "give me roles please"]


	@Bloxlink.flags
	async def __main__(self, CommandArgs):
		author = CommandArgs.message.author

		if not (CommandArgs.guild_data.get("groupIDs") or CommandArgs.guild_data.get("roleBinds")): 
			raise Message(f"This server has no bind configuration! Please run ``{CommandArgs.prefix}bind`` to make a new bind.",
						  type="silly")

		async with CommandArgs.response.loading():
			try:
				added, removed, nickname, errors, roblox_user = await update_member(
					CommandArgs.message.author,
					guild      = CommandArgs.message.guild,
					guild_data = CommandArgs.guild_data,
					roles      = True,
					nickname   = True)

				embed = Embed(title=f"Roblox Profile for {roblox_user.username}")
				embed.set_author(name=str(author), icon_url=author.avatar_url, url=roblox_user.profile_link)

				if not (added or removed):
					raise Message("All caught up! There no roles to add or remove.", type="success")

				if added:
					embed.add_field(name="Added Roles", value=", ".join(added))
				if removed:
					embed.add_field(name="Removed Roles", value=", ".join(removed))
				if nickname:
					embed.description = f"**Nickname:** ``{nickname}``"
				if errors:
					embed.add_field(name="Errors", value=", ".join(errors))

				embed.set_footer(text="Powered by Bloxlink", icon_url=Bloxlink.user.avatar_url)

				await CommandArgs.response.send(embed=embed)

			except UserNotVerified:
				message = CommandArgs.message
				message.content = f"{CommandArgs.prefix}verify"

				await parse_message(message)
				