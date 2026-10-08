import streamlit as st
import requests
import base64
from pathlib import Path
import html


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MCP AI Assistant",
    page_icon="assets/ai_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CONFIG
# =========================================================

API_URL = "http://127.0.0.1:8000/chat"
HEALTH_URL = "http://127.0.0.1:8000/health"

LOGO_PATH = Path("assets/ai_logo.png")


# =========================================================
# IMAGE HELPER
# =========================================================

def image_to_base64(image_path: Path) -> str:

    if not image_path.exists():
        return ""

    return base64.b64encode(
        image_path.read_bytes()
    ).decode("utf-8")


LOGO_B64 = image_to_base64(LOGO_PATH)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL
    ===================================================== */

    .stApp {
        background: #080b14;
        color: #f5f7ff;
    }

    .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    header[data-testid="stHeader"] {
        background: transparent;
    }


    /* =====================================================
       SIDEBAR
    ===================================================== */

    section[data-testid="stSidebar"] {
        background: #0d111d;
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    .sidebar-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 5px 20px 5px;
    }

    .sidebar-logo img {
        width: 52px;
        height: 52px;
        object-fit: contain;

        filter:
            drop-shadow(
                0 5px 10px
                rgba(120,100,255,0.25)
            );

        animation:
            sidebarRobotFloat 3.5s ease-in-out infinite;
    }

    .sidebar-title {
        font-size: 20px;
        font-weight: 700;
        color: white;
    }

    .sidebar-subtitle {
        font-size: 12px;
        color: #8d96aa;
        margin-top: 2px;
    }

    .section-title {
        color: #8d96aa;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 25px;
        margin-bottom: 10px;
    }


    /* =====================================================
       SIDEBAR CARDS
    ===================================================== */

    .tool-card {
        background: #151a28;

        border:
            1px solid
            rgba(255,255,255,0.07);

        border-radius: 10px;

        padding: 10px 12px;

        margin-bottom: 8px;

        color: #dce1ef;

        font-size: 13px;

        transition:
            transform 0.25s ease,
            border-color 0.25s ease,
            background 0.25s ease,
            box-shadow 0.25s ease;
    }

    .tool-card:hover {
        transform: translateX(4px);

        background: #1a2030;

        border-color:
            rgba(141,124,255,0.35);

        box-shadow:
            0 5px 18px
            rgba(80,70,180,0.12);
    }

    .tool-card span {
        color: #8d96aa;
        font-size: 11px;
    }


    /* =====================================================
       SIDEBAR STATUS
    ===================================================== */

    .sidebar-status {
        display: flex;
        align-items: center;
        gap: 8px;

        padding: 10px 12px;

        margin-top: 15px;

        border-radius: 10px;

        background: #121725;

        border:
            1px solid
            rgba(255,255,255,0.06);

        color: #aab2c5;

        font-size: 12px;
    }

    .sidebar-status-dot {
        width: 7px;
        height: 7px;

        border-radius: 50%;

        background: #55d98b;

        box-shadow:
            0 0 10px
            rgba(85,217,139,0.5);

        animation:
            statusPulse 2s infinite;
    }


    /* =====================================================
       HERO
    ===================================================== */

    .hero {
        position: relative;

        text-align: center;

        padding:
            25px
            20px
            35px
            20px;

        overflow: hidden;
    }

    .hero::before {
        content: "";

        position: absolute;

        width: 280px;
        height: 280px;

        left: 50%;
        top: 0;

        transform:
            translateX(-50%);

        background:
            radial-gradient(
                circle,
                rgba(125,92,255,0.28) 0%,
                rgba(125,92,255,0.12) 35%,
                transparent 70%
            );

        filter: blur(12px);

        animation:
            heroGlow 4s ease-in-out infinite;

        pointer-events: none;
    }


    /* =====================================================
       HERO ROBOT
    ===================================================== */

    .hero-logo {
        position: relative;

        z-index: 2;

        width: 125px;
        height: 125px;

        object-fit: contain;

        margin-bottom: 8px;

        filter:
            drop-shadow(
                0 10px 20px
                rgba(100,80,255,0.25)
            )
            drop-shadow(
                0 0 10px
                rgba(130,100,255,0.15)
            );

        animation:
            robotFloat 3.5s ease-in-out infinite,
            robotGlow 3s ease-in-out infinite;
    }


    /* =====================================================
       HERO TITLE
    ===================================================== */

    .hero-title {
        position: relative;

        z-index: 3;

        font-size: 38px;

        font-weight: 800;

        margin-top: 5px;

        color: #ffffff;

        animation:
            titleAppear 0.8s ease-out;
    }

    .hero-title span {
        color: #8d7cff;

        animation:
            titleGlow 3s ease-in-out infinite;
    }

    .hero-subtitle {
        position: relative;

        z-index: 3;

        color: #8d96aa;

        font-size: 15px;

        margin-top: 8px;

        animation:
            subtitleAppear 1s ease-out;
    }


    /* =====================================================
       STATUS
    ===================================================== */

    .status-card {
        display: flex;

        justify-content: center;

        align-items: center;

        gap: 8px;

        margin:
            10px
            auto
            25px
            auto;

        width: fit-content;

        padding: 7px 14px;

        border-radius: 20px;

        background:
            rgba(70,200,130,0.08);

        border:
            1px solid
            rgba(70,200,130,0.2);

        color: #7ce3a7;

        font-size: 12px;

        animation:
            statusAppear 0.8s ease-out;
    }

    .status-dot {
        width: 7px;
        height: 7px;

        border-radius: 50%;

        background: #55d98b;

        animation:
            statusPulse 2s infinite;
    }


    /* =====================================================
       WELCOME CARD
    ===================================================== */

    .welcome-card {
        background:
            linear-gradient(
                135deg,
                #121728,
                #0e1320
            );

        border:
            1px solid
            rgba(255,255,255,0.08);

        border-radius: 18px;

        padding: 25px;

        margin-bottom: 20px;

        animation:
            welcomeAppear 0.7s ease-out;

        transition:
            transform 0.3s ease,
            border-color 0.3s ease,
            box-shadow 0.3s ease;
    }

    .welcome-card:hover {
        transform: translateY(-3px);

        border-color:
            rgba(141,124,255,0.25);

        box-shadow:
            0 10px 35px
            rgba(70,60,150,0.15);
    }

    .welcome-content {
        display: flex;

        align-items: center;

        gap: 18px;
    }

    .welcome-logo {
        width: 75px;
        height: 75px;

        object-fit: contain;

        filter:
            drop-shadow(
                0 5px 12px
                rgba(120,100,255,0.20)
            );

        animation:
            welcomeRobot 3s ease-in-out infinite;
    }

    .welcome-title {
        font-size: 20px;

        font-weight: 700;

        color: white;
    }

    .welcome-text {
        color: #929bb0;

        font-size: 14px;

        margin-top: 5px;

        line-height: 1.6;
    }


    /* =====================================================
       CHAT
    ===================================================== */

    [data-testid="stChatMessage"] {
        background: #111624;

        border:
            1px solid
            rgba(255,255,255,0.06);

        border-radius: 14px;

        margin-bottom: 12px;

        transition:
            transform 0.2s ease,
            border-color 0.2s ease;
    }

    [data-testid="stChatMessage"]:hover {
        border-color:
            rgba(141,124,255,0.18);
    }


    /* =====================================================
       CHAT INPUT
    ===================================================== */

    [data-testid="stChatInput"] {
        border-radius: 14px;

        transition:
            box-shadow 0.3s ease;
    }

    [data-testid="stChatInput"]:focus-within {
        box-shadow:
            0 0 0 2px
            rgba(141,124,255,0.20),

            0 0 20px
            rgba(100,80,255,0.10);
    }


    /* =====================================================
       EXECUTION TRACE EXPANDER
    ===================================================== */

    div[data-testid="stExpander"] {

        background:
            linear-gradient(
                135deg,
                #101625,
                #0d121e
            );

        border:
            1px solid
            rgba(141,124,255,0.15);

        border-radius: 14px;

        margin-top: 14px;

        overflow: hidden;

        transition:
            border-color 0.3s ease,
            box-shadow 0.3s ease;
    }

    div[data-testid="stExpander"]:hover {

        border-color:
            rgba(141,124,255,0.30);

        box-shadow:
            0 8px 25px
            rgba(80,70,180,0.10);
    }


    /* Expander title */

    div[data-testid="stExpander"] summary {

        color: #ffffff;

        font-size: 13px;

        font-weight: 600;
    }


    /* =====================================================
       TRACE CONTAINER
    ===================================================== */

    .trace-container {
        padding:
            5px
            3px
            5px
            3px;
    }


    /* =====================================================
       TRACE STEP
    ===================================================== */

    .trace-step {

        display: flex;

        gap: 12px;

        position: relative;

        padding:
            10px
            5px
            17px
            5px;
    }


    /* Vertical timeline */

    .trace-step:not(:last-child)::after {

        content: "";

        position: absolute;

        left: 17px;

        top: 40px;

        width: 1px;

        height:
            calc(100% - 25px);

        background:
            linear-gradient(
                to bottom,
                rgba(141,124,255,0.35),
                rgba(141,124,255,0.05)
            );
    }


    /* =====================================================
       TRACE ICON
    ===================================================== */

    .trace-number {

        width: 27px;

        height: 27px;

        min-width: 27px;

        display: flex;

        align-items: center;

        justify-content: center;

        border-radius: 50%;

        background: #191f32;

        border:
            1px solid
            rgba(141,124,255,0.25);

        font-size: 12px;

        z-index: 2;
    }


    /* =====================================================
       TRACE CONTENT
    ===================================================== */

    .trace-content {

        flex: 1;

        padding-top: 2px;
    }


    .trace-title {

        color: #e8ebf5;

        font-size: 13px;

        font-weight: 600;

        margin-bottom: 4px;
    }


    .trace-description {

        color: #858ea5;

        font-size: 11px;

        line-height: 1.6;

        word-break: break-word;

        background:
            rgba(255,255,255,0.025);

        border-radius: 7px;

        padding: 5px 7px;

        display: inline-block;
    }


    /* =====================================================
       MCP TOOL BADGE
    ===================================================== */

    .trace-tool {

        display: inline-block;

        margin-top: 8px;

        padding: 7px 11px;

        border-radius: 8px;

        background:
            rgba(141,124,255,0.10);

        border:
            1px solid
            rgba(141,124,255,0.20);

        color: #a99cff;

        font-size: 11px;
    }


    .trace-tool strong {

        color: #c2baff;

        margin-left: 3px;
    }


    /* =====================================================
       ANIMATIONS
    ===================================================== */

    @keyframes robotFloat {

        0% {
            transform: translateY(0px);
        }

        50% {
            transform: translateY(-12px);
        }

        100% {
            transform: translateY(0px);
        }
    }


    @keyframes sidebarRobotFloat {

        0% {
            transform: translateY(0px);
        }

        50% {
            transform: translateY(-4px);
        }

        100% {
            transform: translateY(0px);
        }
    }


    @keyframes robotGlow {

        0% {
            filter:
                drop-shadow(
                    0 10px 20px
                    rgba(100,80,255,0.20)
                )
                drop-shadow(
                    0 0 8px
                    rgba(130,100,255,0.12)
                );
        }

        50% {
            filter:
                drop-shadow(
                    0 15px 25px
                    rgba(100,80,255,0.35)
                )
                drop-shadow(
                    0 0 25px
                    rgba(130,100,255,0.35)
                );
        }

        100% {
            filter:
                drop-shadow(
                    0 10px 20px
                    rgba(100,80,255,0.20)
                )
                drop-shadow(
                    0 0 8px
                    rgba(130,100,255,0.12)
                );
        }
    }


    @keyframes heroGlow {

        0% {
            opacity: 0.45;

            transform:
                translateX(-50%)
                scale(0.90);
        }

        50% {
            opacity: 1;

            transform:
                translateX(-50%)
                scale(1.10);
        }

        100% {
            opacity: 0.45;

            transform:
                translateX(-50%)
                scale(0.90);
        }
    }


    @keyframes titleAppear {

        from {
            opacity: 0;

            transform:
                translateY(15px);
        }

        to {
            opacity: 1;

            transform:
                translateY(0);
        }
    }


    @keyframes subtitleAppear {

        from {
            opacity: 0;

            transform:
                translateY(10px);
        }

        to {
            opacity: 1;

            transform:
                translateY(0);
        }
    }


    @keyframes titleGlow {

        0% {
            text-shadow:
                0 0 0
                rgba(141,124,255,0);
        }

        50% {
            text-shadow:
                0 0 15px
                rgba(141,124,255,0.45);
        }

        100% {
            text-shadow:
                0 0 0
                rgba(141,124,255,0);
        }
    }


    @keyframes statusAppear {

        from {
            opacity: 0;

            transform:
                translateY(-8px);
        }

        to {
            opacity: 1;

            transform:
                translateY(0);
        }
    }


    @keyframes statusPulse {

        0% {
            box-shadow:
                0 0 0 0
                rgba(85,217,139,0.60);
        }

        70% {
            box-shadow:
                0 0 0 8px
                rgba(85,217,139,0);
        }

        100% {
            box-shadow:
                0 0 0 0
                rgba(85,217,139,0);
        }
    }


    @keyframes welcomeAppear {

        from {
            opacity: 0;

            transform:
                translateY(20px);
        }

        to {
            opacity: 1;

            transform:
                translateY(0);
        }
    }


    @keyframes welcomeRobot {

        0% {
            transform:
                translateY(0);
        }

        50% {
            transform:
                translateY(-6px)
                rotate(-2deg);
        }

        100% {
            transform:
                translateY(0);
        }
    }


    /* =====================================================
       RESPONSIVE
    ===================================================== */

    @media (max-width: 768px) {

        .hero-title {
            font-size: 30px;
        }

        .hero-logo {
            width: 100px;
            height: 100px;
        }

        .welcome-content {
            flex-direction: column;
            text-align: center;
        }

        .welcome-logo {
            width: 65px;
            height: 65px;
        }

        .hero {
            padding-top: 15px;
        }

        .trace-description {
            font-size: 10px;
        }
    }


    /* =====================================================
       ACCESSIBILITY
    ===================================================== */

    @media (prefers-reduced-motion: reduce) {

        *,
        *::before,
        *::after {

            animation-duration:
                0.01ms !important;

            animation-iteration-count:
                1 !important;

            scroll-behavior:
                auto !important;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    # -----------------------------------------------------
    # LOGO
    # -----------------------------------------------------

    if LOGO_B64:

        st.html(
            f"""
            <div class="sidebar-logo">

                <img
                    src="data:image/png;base64,{LOGO_B64}"
                >

                <div>

                    <div class="sidebar-title">
                        MCP AI Assistant
                    </div>

                    <div class="sidebar-subtitle">
                        Powered by Ollama
                    </div>

                </div>

            </div>
            """
        )


    # -----------------------------------------------------
    # ARCHITECTURE
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="section-title">
            Architecture
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        """
        <div class="tool-card">
            🧠 <b>AI Agent</b><br>
            <span>Ollama + LangChain</span>
        </div>

        <div class="tool-card">
            🔍 <b>MCP Client</b><br>
            <span>Tool discovery & communication</span>
        </div>

        <div class="tool-card">
            🛠️ <b>MCP Server</b><br>
            <span>Exposes AI tools</span>
        </div>

        <div class="tool-card">
            ⚡ <b>FastAPI</b><br>
            <span>Application API</span>
        </div>

        <div class="tool-card">
            🦙 <b>Ollama</b><br>
            <span>Local LLM inference</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


    # -----------------------------------------------------
    # MCP TOOLS
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="section-title">
            MCP Tools
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown(
        """
        <div class="tool-card">
            ➕ <b>add_numbers</b><br>
            <span>Add two numbers</span>
        </div>

        <div class="tool-card">
            ➖ <b>subtract_numbers</b><br>
            <span>Subtract two numbers</span>
        </div>

        <div class="tool-card">
            ✖️ <b>multiply_numbers</b><br>
            <span>Multiply two numbers</span>
        </div>

        <div class="tool-card">
            ➗ <b>divide_numbers</b><br>
            <span>Divide two numbers</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


    # -----------------------------------------------------
    # BACKEND STATUS
    # -----------------------------------------------------

    try:

        health_response = requests.get(
            HEALTH_URL,
            timeout=2,
        )

        backend_online = (
            health_response.status_code == 200
        )

    except Exception:

        backend_online = False


    status_text = (
        "FastAPI Backend Online"
        if backend_online
        else "FastAPI Backend Offline"
    )


    st.html(
        f"""
        <div class="sidebar-status">

            <div class="sidebar-status-dot"></div>

            <div>
                {status_text}
            </div>

        </div>
        """
    )


    # -----------------------------------------------------
    # CLEAR CHAT
    # -----------------------------------------------------

    st.markdown(
        "<br>",
        unsafe_allow_html=True,
    )


    if st.button(
        "🗑️  Clear Conversation",
        use_container_width=True,
    ):

        st.session_state.messages = []

        st.rerun()


# =========================================================
# HERO
# =========================================================

if LOGO_B64:

    st.html(
        f"""
        <div class="hero">

            <img
                src="data:image/png;base64,{LOGO_B64}"
                class="hero-logo"
            >

            <div class="hero-title">
                MCP <span>AI Assistant</span>
            </div>

            <div class="hero-subtitle">
                Intelligent tool calling with MCP + Ollama
            </div>

        </div>

        <div class="status-card">

            <div class="status-dot"></div>

            MCP Agent Ready

        </div>
        """
    )


# =========================================================
# WELCOME CARD
# =========================================================

if len(st.session_state.messages) == 0:

    if LOGO_B64:

        st.html(
            f"""
            <div class="welcome-card">

                <div class="welcome-content">

                    <img
                        src="data:image/png;base64,{LOGO_B64}"
                        class="welcome-logo"
                    >

                    <div>

                        <div class="welcome-title">
                            Hello! I'm your MCP AI Assistant 👋
                        </div>

                        <div class="welcome-text">
                            Ask me a question and I'll decide
                            whether an MCP tool is required.
                            Open the execution trace to see
                            how the agent processed your request.
                        </div>

                    </div>

                </div>

            </div>
            """
        )


# =========================================================
# EXECUTION TRACE DROPDOWN
# =========================================================

def render_execution_trace(data):

    steps = data.get("steps", [])

    if not steps:
        return


    tool = data.get("tool")


    # -----------------------------------------------------
    # BUILD COMPLETE TRACE HTML
    # -----------------------------------------------------

    trace_html = """
    <div class="trace-container">
    """


    for index, step in enumerate(
        steps,
        start=1,
    ):

        icon = html.escape(
            str(
                step.get(
                    "icon",
                    "•",
                )
            )
        )


        title = html.escape(
            str(
                step.get(
                    "title",
                    "",
                )
            )
        )


        description = html.escape(
            str(
                step.get(
                    "description",
                    "",
                )
            )
        )


        trace_html += f"""
        <div class="trace-step">

            <div class="trace-number">
                {icon}
            </div>

            <div class="trace-content">

                <div class="trace-title">
                    {index}. {title}
                </div>

                <div class="trace-description">
                    {description}
                </div>

            </div>

        </div>
        """


    # -----------------------------------------------------
    # TOOL BADGE
    # -----------------------------------------------------

    if tool:

        safe_tool = html.escape(
            str(tool)
        )


        trace_html += f"""
        <div class="trace-tool">

            🛠️ MCP Tool Used:

            <strong>
                {safe_tool}
            </strong>

        </div>
        """


    trace_html += """
    </div>
    """


    # -----------------------------------------------------
    # EXPANDER
    # -----------------------------------------------------

    with st.expander(
        "⚡ Execution Trace",
        expanded=False,
    ):

        # IMPORTANT:
        # Use st.html() instead of st.markdown()
        st.html(trace_html)


# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    role = message["role"]

    content = message["content"]


    # -----------------------------------------------------
    # USER MESSAGE
    # -----------------------------------------------------

    if role == "user":

        with st.chat_message(
            "user",
            avatar="👤",
        ):

            st.markdown(content)


    # -----------------------------------------------------
    # ASSISTANT MESSAGE
    # -----------------------------------------------------

    else:

        if LOGO_PATH.exists():

            with st.chat_message(
                "assistant",
                avatar=str(LOGO_PATH),
            ):

                st.markdown(content)


                execution_data = message.get(
                    "execution"
                )


                if execution_data:

                    render_execution_trace(
                        execution_data
                    )

        else:

            with st.chat_message(
                "assistant",
                avatar="🤖",
            ):

                st.markdown(content)


# =========================================================
# CHAT INPUT
# =========================================================

user_input = st.chat_input(
    "Ask me anything..."
)


# =========================================================
# SEND MESSAGE
# =========================================================

if user_input:

    # -----------------------------------------------------
    # SAVE USER MESSAGE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",

            "content": user_input,
        }
    )


    # -----------------------------------------------------
    # USER MESSAGE
    # -----------------------------------------------------

    with st.chat_message(
        "user",
        avatar="👤",
    ):

        st.markdown(user_input)


    # -----------------------------------------------------
    # ASSISTANT
    # -----------------------------------------------------

    if LOGO_PATH.exists():

        assistant_container = st.chat_message(
            "assistant",
            avatar=str(LOGO_PATH),
        )

    else:

        assistant_container = st.chat_message(
            "assistant",
            avatar="🤖",
        )


    with assistant_container:

        # -------------------------------------------------
        # CALL BACKEND
        # -------------------------------------------------

        with st.spinner(
            "Agent is thinking and selecting tools..."
        ):

            try:

                response = requests.post(
                    API_URL,

                    json={
                        "message": user_input
                    },

                    timeout=120,
                )


                # =========================================
                # SUCCESS
                # =========================================

                if response.status_code == 200:

                    data = response.json()


                    answer = data.get(
                        "answer",
                        "I couldn't generate an answer.",
                    )


                # =========================================
                # BACKEND ERROR
                # =========================================

                else:

                    answer = (
                        f"⚠️ Backend returned "
                        f"HTTP {response.status_code}"
                    )


                    data = {

                        "steps": [

                            {
                                "icon": "❌",

                                "title":
                                    "Backend error",

                                "description":
                                    answer,

                                "status":
                                    "failed",
                            }

                        ]
                    }


            # =============================================
            # CONNECTION ERROR
            # =============================================

            except requests.exceptions.ConnectionError:

                answer = (
                    "⚠️ Could not connect to FastAPI.\n\n"
                    "Make sure the backend is running on "
                    "`http://127.0.0.1:8000`."
                )


                data = {

                    "steps": [

                        {
                            "icon": "❌",

                            "title":
                                "Connection failed",

                            "description":
                                "FastAPI backend is not reachable.",

                            "status":
                                "failed",
                        }

                    ]
                }


            # =============================================
            # TIMEOUT
            # =============================================

            except requests.exceptions.Timeout:

                answer = (
                    "⏳ The request took too long. "
                    "Please try again."
                )


                data = {

                    "steps": [

                        {
                            "icon": "⏳",

                            "title":
                                "Request timeout",

                            "description":
                                "The backend did not respond in time.",

                            "status":
                                "failed",
                        }

                    ]
                }


            # =============================================
            # GENERAL ERROR
            # =============================================

            except Exception as e:

                answer = (
                    f"⚠️ Error: {str(e)}"
                )


                data = {

                    "steps": [

                        {
                            "icon": "❌",

                            "title":
                                "Unexpected error",

                            "description":
                                str(e),

                            "status":
                                "failed",
                        }

                    ]
                }


        # -------------------------------------------------
        # DISPLAY ANSWER
        # -------------------------------------------------

        st.markdown(answer)


        # -------------------------------------------------
        # EXECUTION TRACE
        # -------------------------------------------------

        render_execution_trace(data)


    # -----------------------------------------------------
    # SAVE ASSISTANT MESSAGE
    # -----------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "assistant",

            "content": answer,

            "execution": data,
        }
    )