# Welcome to Terminal Casino

This is a set of casino games all in the Terminal. This is a 100% Python project. 
We primarily use the official [OSC Discord](https://discord.gg/qAGudju6) to communicate.

## How to Contribute
1. Find an issue to work on
2. Comment on the issue and let us assign you
3. Create a fork of the branch you'd like to work on
4. Code up something cool
5. Make a pull request and wait for approval
* If you want to work on an issue in collaboration with multiple OSC members, be careful not to submit overlapping PRs.

## How to Run
1. Open Terminal
2. cd into your TERMINALCASINO folder
3. Execute the following command to run the program:
```
python -m casino.main
```

## Roadmap

1. Documentation: continue to update the new docs/ folder with technical explanations of the games (keyed towards developers, not users)
2. OOP Overhaul: spring-boards off of documentation, we will release a blackjack/template doc shortly (as blackjack is now fully OOP) that contributors can use as inspiration when overhauling the remaining games. For future feature development, it's important that the games are modular, readable, and logically structured.
3. [Textual](https://textual.textualize.io) Overhaul: Textual is an incredibly powerful terminal UI library. Kevin and I feel that switching to this will make Terminal Casino resemble a professional project, not to mention features of [tabs](https://textual.textualize.io/widget_gallery/#tabs), [loading bars](https://textual.textualize.io/widget_gallery/#loadingindicator), and other [widgets](https://textual.textualize.io/widget_gallery), which will all vastly improve the user experience. What's incredible about Textual is that it will make our UI workflow far simpler. Everything we need will be inside one library instead of being triaged across multiple.
4. Multiplayer: P2P multiplayer sessions. We're still discussing possible remote-networking solutions, but at the very least, multiplayer across the same Wi-Fi network will be possible.
