# Breakout

A classic Breakout arcade game built with Python and pygame-ce. Bounce the ball off the paddle, break every brick and try to beat your high score.

## How to play

- Keep the ball in play with the paddle.
- Each brick you break adds to your score. Higher rows are worth more.
- You have 3 lives. Lose them all and the game is over.
- Break every brick to win.

## Controls

| Key | Action |
|---|---|
| Left / Right or A / D | Move the paddle |
| Space or Enter | Start the game (menu) |
| P | Pause and resume |
| R | Restart (when paused, or after game over or a win) |
| Mouse click | Press the on-screen buttons |
| Mouse or touch | Move the paddle |
| P or the Pause button | Pause and resume |

## Run it on your computer

```bash
git clone https://github.com/muhammadatiqsyed-pythonprojects/breakout.git
cd breakout
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
python main.py
```

On Windows Git Bash use the `source` line above. On macOS or Linux use `source .venv/bin/activate`.

## Play online

https://muhammadatiqsyed-pythonprojects.github.io/breakout/

## Credits

Images and sounds by Kenney (www.kenney.nl), licensed CC0. Full list in `assets/CREDITS.md`.

## License

All rights reserved. Licence to be decided.