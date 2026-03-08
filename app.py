import streamlit as st
from llm import enhance_prompt
from examples import load_examples
import json

# ── Page config (must be first Streamlit call) ──────────────────────────────
st.set_page_config(
    page_title="Prompt Enhancer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Dark mode CSS injection ──────────────────────────────────────────────────
st.markdown("""
<style>
    /* Force dark background regardless of system theme */
    .stApp { background-color: #0e1117; color: #fafafa; }
    .stTextArea textarea {
        background-color: #1e2130;
        color: #fafafa;
        border: 1px solid #3a3f5c;
        border-radius: 8px;
        font-size: 15px;
    }
    .output-box {
        background-color: #1e2130;
        border: 1px solid #3a3f5c;
        border-radius: 8px;
        padding: 1.2rem;
        font-size: 14px;
        line-height: 1.7;
        white-space: pre-wrap;
    }
    .badge {
        background: #2d3250;
        border-radius: 4px;
        padding: 2px 8px;
        font-size: 12px;
        color: #7b8cde;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state defaults ───────────────────────────────────────────────────
if "output" not in st.session_state:
    st.session_state.output = ""
if "history" not in st.session_state:
    st.session_state.history = []
if "seed" not in st.session_state:
    st.session_state.seed = 0  # Used to force regeneration

# ── Header ───────────────────────────────────────────────────────────────────
st.title("⚡ Prompt Enhancer")
st.caption("Turn vague prompts into precision-engineered instructions for any LLM.")

# ── Sidebar: intent presets ──────────────────────────────────────────────────
with st.sidebar:
    st.header("Settings")
    intent_override = st.selectbox(
        "Force intent detection to:",
        ["Auto-detect", "Code generation", "Writing/copywriting",
         "Data analysis", "Summarization", "Creative brainstorm"],
        index=0
    )
    temperature = st.slider("LLM Temperature", 0.1, 1.0, 0.7, 0.1)
    show_meta = st.checkbox("Show detected intent + tokens", value=False)

# ── Main input ───────────────────────────────────────────────────────────────
examples = load_examples()
example_labels = ["(none)"] + [e["label"] for e in examples]
selected_example = st.selectbox("Load an example:", example_labels)

if selected_example != "(none)":
    default_input = next(e["input"] for e in examples if e["label"] == selected_example)
else:
    default_input = ""

user_input = st.text_area(
    "Your vague prompt:",
    value=default_input,
    height=120,
    placeholder='e.g. "write me a python script that reads csv files"',
    key="user_input"
)

col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    enhance_btn = st.button("⚡ Enhance", type="primary", use_container_width=True)
with col2:
    regen_btn = st.button("🔁 Regenerate", use_container_width=True,
                          disabled=not st.session_state.output)
    
from streamlit_extras.copy_to_clipboard import copy_to_clipboard_button

# ── Trigger enhancement ──────────────────────────────────────────────────────
def run_enhancement(seed: int = 0):
    if not user_input.strip():
        st.warning("Please enter a prompt first.")
        return

    with st.spinner("Enhancing your prompt..."):
        try:
            result = enhance_prompt(
                user_input,
                intent_override=intent_override,
                temperature=temperature,
                seed=seed
            )
            st.session_state.output = result["enhanced"]
            st.session_state.intent = result["intent"]
            st.session_state.tokens = result["tokens"]
            st.session_state.history.append(result["enhanced"])
        except Exception as e:
            st.error(f"LLM error: {str(e)}")


if enhance_btn:
    st.session_state.seed = 0
    run_enhancement(seed=0)

if regen_btn:
    st.session_state.seed += 1
    run_enhancement(seed=st.session_state.seed)


# ── Output display ───────────────────────────────────────────────────────────
if st.session_state.output:
    st.divider()

    # Meta info
    if show_meta:
        col_a, col_b = st.columns(2)
        col_a.markdown(f'**Detected intent:** <span class="badge">{st.session_state.get("intent","—")}</span>',
                       unsafe_allow_html=True)
        col_b.markdown(f'**Tokens used:** <span class="badge">{st.session_state.get("tokens","—")}</span>',
                       unsafe_allow_html=True)

    st.subheader("✨ Enhanced Prompt")
    st.markdown(
        f'<div class="output-box">{st.session_state.output}</div>',
        unsafe_allow_html=True
    )

    # Copy button (streamlit-extras)
    copy_to_clipboard_button(
        "📋 Copy to clipboard",
        st.session_state.output,
        after_copy_label="✅ Copied!"
    )

    # Version history expander
    if len(st.session_state.history) > 1:
        with st.expander(f"🕐 Version history ({len(st.session_state.history)} versions)"):
            for i, version in enumerate(reversed(st.session_state.history)):
                st.markdown(f"**Version {len(st.session_state.history) - i}**")
                st.code(version, language="")
                st.divider()