import io
import random

import chess
import chess.pgn
import chess.svg
import streamlit as st
from datasets import load_dataset

st.set_page_config(page_title="Chess Openings", page_icon="♖")

# Load external CSS
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


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
if "final_move_completed" not in st.session_state:
    st.session_state.final_move_completed = False
if "random_opening" not in st.session_state:
    st.session_state.random_opening = None
if "completed_openings" not in st.session_state:
    st.session_state.completed_openings = set()
if "score" not in st.session_state:
    st.session_state.score = 0

data = load_data()
if data.empty:
    st.error("No data available. Failed to load from Hugging Face dataset.")
    st.stop()


def update_score():
    # Note: keeping it as a function to be able to try different scores
    st.session_state.score += 1
    #  score = 0
    # for opening in st.session_state.completed_openings:
    #     opening_data = data[data["name"] == opening].iloc[0]
    #     moves_count = opening_data["pgn"].count(".")
    #     score += moves_count

    # return score


# App layout
# st.markdown(
#     "<h1 style='text-align: center; font-size: 32px; margin-bottom: 10px; margin-top: -25px; padding-top: 0; text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);'>Practice Chess Openings</h1>",
#     unsafe_allow_html=True,
# )

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

    # Random Opening button with custom styling
    random_button = st.button(
        "Random Opening",
        key="random_opening_button",
        use_container_width=True,
        help="Select a random opening",
        type="primary",  # This will give it a filled style
    )

    # Remove the previous CSS styling attempt
    # The CSS is now loaded from the external file

    if random_button:
        available_openings = [
            opening
            for opening in filtered_data["name"].unique()
            if opening not in st.session_state.completed_openings
        ]
        if available_openings:
            st.session_state.random_opening = random.choice(available_openings)
        else:
            st.warning(
                "You've completed all available openings! Resetting completed list."
            )
            st.session_state.completed_openings.clear()
            st.session_state.random_opening = random.choice(
                list(filtered_data["name"].unique())
            )
        st.rerun()

    # Check if the random_opening is still in the filtered data
    unique_openings = list(filtered_data["name"].unique())
    if st.session_state.random_opening not in unique_openings:
        st.session_state.random_opening = None

    opening = st.selectbox(
        label="Select an opening",
        options=unique_openings,
        index=unique_openings.index(st.session_state.random_opening)
        if st.session_state.random_opening
        else 0,
        key="opening_selector",
        placeholder="Select an opening",
    )

    if opening and opening != st.session_state.current_opening:
        st.session_state.current_opening = opening
        st.session_state.move_index = 0
        st.session_state.user_move = ""
        st.session_state.board = chess.Board()
        st.session_state.final_move_completed = False
        if "success_message" in st.session_state:
            del st.session_state.success_message

        # Get PGN for the selected opening and parse it
        selected_opening = filtered_data[filtered_data["name"] == opening].iloc[0]
        pgn = selected_opening["pgn"]
        game = chess.pgn.read_game(io.StringIO(pgn))
        st.session_state.moves = list(game.mainline_moves())

    with st.expander("Instructions"):
        st.write("This app lets you practice ~3500 chess openings.")
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
        st.write("---")
        st.write(
            "This app is using the [Lichess](https://lichess.org/) openings dataset via [HuggingFace](https://huggingface.co/datasets/Lichess/chess-openings)"
        )
        st.write(
            "This is just a toy app. Go to [Lichess](https://lichess.org/) \
            or [Chess.com](https://chess.com) for serious chess practice \
            (although I think this functionality isn't available there)"
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
        st.session_state.final_move_completed = False
        if "success_message" in st.session_state:
            del st.session_state.success_message
        update_board()


# Create two columns: one for the board and buttons, one for the move list
col1, col2 = st.columns([3, 1])

with col1:
    if st.session_state.current_opening:
        st.markdown(
            f"""
            <div style='width: 360px; margin-bottom: 10px;'>
                <h3 style='
                    background: linear-gradient(90deg, #0077be, #00a86b);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    display: inline-block;
                    font-weight: bold;
                '>
                    {st.session_state.current_opening}
                </h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_prev, col_next, right_col = st.columns([5, 2, 2])

        with col_prev:
            st.button(
                "⬅️ &nbsp; Previous",
                disabled=st.session_state.move_index == 0,
                on_click=update_prev_move,
            )
        with col_next:
            st.button(
                "Next &nbsp;&nbsp;&nbsp;➡️",
                disabled=(st.session_state.move_index >= len(st.session_state.moves))
                or (
                    not hide_next_moves
                    and st.session_state.move_index == len(st.session_state.moves)
                ),
                on_click=update_next_move,
            )

        board_container = st.empty()
        board_container.image(chess.svg.board(board=st.session_state.board, size=400))

        # User input for next move
        if hide_next_moves and st.session_state.move_index < len(
            st.session_state.moves
        ):
            col_input, col_submit, col_right = st.columns([3, 1, 1])

            def submit_move():
                if st.session_state.user_move.strip() == "":
                    return
                user_move = st.session_state.user_move
                try:
                    user_chess_move = st.session_state.board.parse_san(user_move)
                    correct_move = st.session_state.moves[st.session_state.move_index]
                    if user_chess_move == correct_move:
                        update_score()
                        st.session_state.move_index += 1
                        if st.session_state.move_index == len(st.session_state.moves):
                            st.session_state.success_message = "🎉 &nbsp; Well done!"
                            st.session_state.final_move_completed = True
                            st.session_state.completed_openings.add(
                                st.session_state.current_opening
                            )
                        else:
                            st.session_state.success_message = (
                                "✅ Correct! Moving to the next one"
                            )

                        st.session_state.user_move = ""
                        update_board()
                    else:
                        st.session_state.error_message = "😭 Incorrect move. Try again!"
                except ValueError as e:
                    error_message = str(e).lower()
                    if (
                        "invalid san" in error_message
                        or "unexpected" in error_message
                        or "unterminated" in error_message
                    ):
                        st.session_state.error_message = "🚫 Invalid format. Please use standard SAN notation (e.g., e4 or Nf3)."
                    else:
                        st.session_state.error_message = "⛔ Invalid move. This move is not allowed in the current position."

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
                    if not st.session_state.final_move_completed:
                        del st.session_state.success_message

            with col_submit:
                st.markdown("<br>", unsafe_allow_html=True)
                submit_button = st.button(
                    "Submit",
                    on_click=submit_move,
                )

        if st.session_state.final_move_completed:
            col_success, col_empty = st.columns([1, 2])
            with col_success:
                st.success("🎉 &nbsp; Well done!")

    else:
        st.info("Please select an opening from the sidebar to begin.")

with col2:
    if st.session_state.current_opening:
        st.subheader("Moves", divider="green")
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

with st.sidebar:
    st.markdown("---")

    # score = update_score()
    st.metric(
        label="Score",
        value=st.session_state.score,
        help="1 point per correct move",
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("Completed Openings")
    with col2:
        if st.button("Reset", key="reset_completed", help="Reset completed openings"):
            st.session_state.completed_openings.clear()
            st.rerun()

    with st.expander("View Completed Openings"):
        if st.session_state.completed_openings:
            for completed_opening in st.session_state.completed_openings:
                st.markdown(f"- {completed_opening}")
        else:
            st.markdown("No openings completed yet.")
