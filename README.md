---
title: Practice Chess Openings
emoji: ♖
colorFrom: blue
colorTo: gray
sdk: streamlit
sdk_version: 1.38.0
app_file: app.py
pinned: false
license: cc0-1.0
datasets:
  - Lichess/chess-openings
suggested_hardware: cpu-basic
---

# Chess Openings

This little app lets you practice ~3500 chess openings.

This is just a toy app A(I) wrote for fun. Go to [Lichess](https://lichess.org/) or [Chess.com](https://chess.com) for serious chess practice.

## Entering moves

- Use standard algebraic notation (SAN)
- Examples: e4, Nf3, O-O (castling), exd5 (pawn capture)
- Specify the piece (except for pawns) + destination square
- Use 'x' for captures, '+' for check, '#' for checkmate

## Piece symbols

- ♔ King (K)
- ♕ Queen (Q)
- ♖ Rook (R)
- ♗ Bishop (B)
- ♘ Knight (N)
- ♙ Pawn (no letter)

See full notation [here](<https://en.wikipedia.org/wiki/Algebraic_notation_(chess)>)

## Dataset

This app is using the [Lichess](https://lichess.org/) openings dataset via [HuggingFace](https://huggingface.co/datasets/Lichess/chess-openings)

## License

The license is `CC0-1.0` to match the dataset's license.
