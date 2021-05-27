
class PATHS:
    AVATAR_ROTATION = "./sources/avatar.json"
    AVATARS = dict(
        fruits = "./sources/images/fruits-muOS.png",
        ag = "./sources/images/ag-muOS.png"
    )

emojiFirst = "⏪"
emojiPrior = "⬅"
emojiNext = "➡"
emojiLast = "⏩"

emoji1 = "1️⃣"
emoji2 = "2️⃣"
emoji3 = "3️⃣"
emoji4 = "4️⃣"
emoji5 = "5️⃣"
emoji6 = "6️⃣"
emoji7 = "7️⃣"
emoji8 = "8️⃣"
emoji9 = "9️⃣"
emoji10 = "🔟"

emojiNumbers = "🔢"
emojiArrows = "↔️"

emojiLock = "🔒"
emojiUnlock = "🔓"

smolArrows = [emojiPrior, emojiNext]
arrows = [emojiFirst, emojiPrior, emojiNext, emojiLast]
indices = [emoji1, emoji2, emoji3, emoji4, emoji5, emoji6, emoji7, emoji8, emoji9, emoji10]
switches = [emojiNumbers, emojiArrows]

paginationIndex = lambda index, length, locked: f"Page {index} of {length}." + (" Any user can navigate using reactions." if not locked else " The issuing user can navigate using reactions.")