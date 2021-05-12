
cogName = "Moderation Cog"
cog = {
    "name": cogName,
    "description": "This part of the bot has a few tools to make moderation easier."
}

deletedMessageText = lambda authorID, deleterID, link: f"> Message from <@{authorID}> deleted by <@{deleterID}>:\n<{link}>"
