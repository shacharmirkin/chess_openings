import io

import chess
import chess.pgn
import chess.svg
import streamlit as st
from datasets import load_dataset

st.set_page_config(page_title="Practice Chess Openings", page_icon="♖")


@st.cache_data
def load_data():
    ds = load_dataset("Lichess/chess-openings", split="train")
    df = ds.to_pandas()
    print(f"Total openings: {len(df)}")
    print(df["pgn"].head())
    return df


# Initialize session state variables
if "move_index" not in st.session_state:
    st.session_state.move_index = 0
if "user_move" not in st.session_state:
    st.session_state.user_move = ""
if "current_opening" not in st.session_state:
    st.session_state.current_opening = None
if "board" not in st.session_state:
    st.session_state.board = chess.Board()
if "moves" not in st.session_state:
    st.session_state.moves = []

data = load_data()

if data.empty:
    st.error("No data available. Failed to load from Hugging Face dataset.")
    st.stop()

# App layout
st.title("Practice Chess Openings")

with st.sidebar:
    st.header("Settings")

    # Move range slider
    min_moves, max_moves = st.slider(
        "Select range of moves:", min_value=1, max_value=18, value=(1, 18), step=1
    )
    print(f"{min_moves=}, {max_moves=}")

    # Hide next moves checkbox
    hide_next_moves = st.checkbox("Hide next moves", value=True)

    # Filter the data based on the min and max number of moves
    filtered_data = data[
        (data["pgn"].str.count("\.") >= min_moves)
        & (data["pgn"].str.count("\.") <= max_moves)
    ]
    print(f"Total openings after filtering: {len(filtered_data)}")

    if filtered_data.empty:
        st.error(
            "No openings found with the specified number of moves. Please adjust your selection."
        )
        st.stop()

    opening = st.selectbox(
        label="Select an opening",
        options=list(filtered_data["name"].unique()),
        index=None,
        key="opening_selector",
        placeholder="Select an opening",
    )

    if opening and opening != st.session_state.current_opening:
        st.session_state.current_opening = opening
        st.session_state.move_index = 0
        st.session_state.user_move = ""
        st.session_state.board = chess.Board()

        # Get PGN for the selected opening
        selected_opening = filtered_data[filtered_data["name"] == opening].iloc[0]
        pgn = selected_opening["pgn"]

        # Parse PGN
        game = chess.pgn.read_game(io.StringIO(pgn))
        st.session_state.moves = list(game.mainline_moves())

    with st.expander("Instructions"):
        st.write("Entering moves:")
        st.write("Use standard algebraic notation (SAN)")
        st.write("Examples: e4, Nf3, O-O (castling), exd5 (pawn capture)")
        st.write("Specify the piece (except for pawns) + destination square")
        st.write("Use 'x' for captures, '+' for check, '#' for checkmate")

        st.write("\nPiece symbols:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.write("♔ King (K)")
            st.write("♕ Queen (Q)")
        with col2:
            st.write("♖ Rook (R)")
            st.write("♗ Bishop (B)")
        with col3:
            st.write("♘ Knight (N)")
            st.write("♙ Pawn (no letter)")

        st.write(
            "See full notation [here](https://en.wikipedia.org/wiki/Algebraic_notation_(chess))"
        )
        st.write(
            "This app is using the [Lichess](https://lichess.org/) openings dataset via [HuggingFace](https://huggingface.co/datasets/Lichess/chess-openings)"
        )


def update_board():
    st.session_state.board = chess.Board()
    for move in st.session_state.moves[: st.session_state.move_index]:
        st.session_state.board.push(move)


def update_next_move():
    if st.session_state.move_index < len(st.session_state.moves):
        st.session_state.move_index += 1
        update_board()


def update_prev_move():
    if st.session_state.move_index > 0:
        st.session_state.move_index -= 1
        update_board()


# Create two columns: one for the board and buttons, one for the move list
col1, col2 = st.columns([3, 1])

with col1:
    if st.session_state.current_opening:
        st.subheader(f":blue[{st.session_state.current_opening}]")

        col_prev, col_next, right_col = st.columns([1, 1, 1])

        with col_prev:
            st.button(
                "⬅️ Previous",
                disabled=st.session_state.move_index == 0,
                on_click=update_prev_move,
            )
        with col_next:
            st.button(
                "➡️ Next",
                disabled=st.session_state.move_index >= len(st.session_state.moves),
                on_click=update_next_move,
            )

        board_container = st.empty()
        board_container.image(chess.svg.board(board=st.session_state.board, size=450))

        # User input for next move
        if hide_next_moves and st.session_state.move_index < len(
            st.session_state.moves
        ):
            col_input, col_submit, col_right = st.columns([2, 1, 1])

            def submit_move():
                if st.session_state.user_move.strip() == "":
                    return
                user_move = st.session_state.user_move
                try:
                    user_chess_move = st.session_state.board.parse_san(user_move)
                    correct_move = st.session_state.moves[st.session_state.move_index]
                    if user_chess_move == correct_move:
                        st.session_state.success_message = (
                            "Correct move! Moving to the next one."
                        )
                        st.session_state.move_index += 1
                        st.session_state.user_move = ""
                        update_board()
                    else:
                        st.session_state.error_message = "Incorrect move. Try again!"
                except ValueError as e:
                    error_message = str(e).lower()
                    if (
                        "invalid san" in error_message
                        or "unexpected" in error_message
                        or "unterminated" in error_message
                    ):
                        st.session_state.error_message = "Invalid move format. Please use standard SAN notation (e.g., e4 or Nf3)."
                    else:
                        st.session_state.error_message = "Invalid move. This move is not allowed in the current position."

            with col_input:
                user_move = st.text_input(
                    label="Enter your move",
                    placeholder="Enter your move (e.g., e4 or Nf3)",
                    key="user_move",
                    value=st.session_state.user_move,
                    label_visibility="hidden",
                    on_change=submit_move,
                )
                if "error_message" in st.session_state:
                    st.error(st.session_state.error_message)
                    del st.session_state.error_message
                elif "success_message" in st.session_state:
                    st.success(st.session_state.success_message)
                    del st.session_state.success_message

            with col_submit:
                st.markdown("<br>", unsafe_allow_html=True)
                submit_button = st.button(
                    "Submit",
                    on_click=submit_move,
                )
    else:
        st.info("Please select an opening from the sidebar to begin.")

with col2:
    if st.session_state.current_opening:
        st.header("Moves", divider="green")
        move_text = ""
        current_node = chess.pgn.Game()
        for i, move in enumerate(st.session_state.moves):
            if i % 2 == 0:
                move_number = i // 2 + 1
                move_text += f"{move_number}. "
            san_move = current_node.board().san(move)
            if i < st.session_state.move_index:
                move_text += f"**{san_move}** "
            elif hide_next_moves:
                move_text += "... "
            else:
                move_text += f"{san_move} "
            if i % 2 == 1 or i == len(st.session_state.moves) - 1:
                move_text += "\n"
            current_node = current_node.add_variation(move)
        st.markdown(move_text)
