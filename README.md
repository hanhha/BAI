# BAI
A Telegram bot that can help me to manipulate notes and check some stuffs basing on my commands.

## Supported commands
* /start                    - intiialize bot so that it can respond.
* /note                     - start to recording note. Following sending message will be treated as note's content until /end command. Use ,,, after inline tag.
* /note all                 - show all notes.
* /note tag1 tag2 tag3 ...  - show notes with tag1, tag2, tag3, ...
* /note tags                - select tags and then show notes with selected tags.
* /note timestamp           - append content to this note
* /diary                    - start to recording entry. Following sending message will be treated as entry's content until /end command. Use ,,, after inline tag.
* /diary all                - show all entries.
* /diary tag1 tag2 tag3 ... - show entries with tag1, tag2, tag3, ...
* /diary tags               - select tags and then show entries with selected tags.
* /diary timestamp          - Append content to this entry
* /end <tag1 tag2 tag3 ...> - finish recording (note/diary) and save it to disk with tags.
* /check_plate <plate number> - check movement violation of car with given plate number.
* /lookup <word1 word2 ...>   - lookup words in English-Vietnamese dictionary then show their descriptions.
 
## Conversation
[Chatterbot](https://chatterbot.readthedocs.io/en/stable/) to serve conversation.
