import base64
import json
import os
import subprocess
import sys
import time
import urllib.parse
from io import BytesIO

# --- Automated Dependency Check & Installation ---
REQUIRED_PACKAGES = ["streamlit", "groq", "requests", "httpx"]

for pkg in REQUIRED_PACKAGES:
    try:
        __import__(pkg)
    except ImportError:
        print(f"Installing missing dependency: {pkg}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

import httpx
import requests
import streamlit as st
from groq import Groq

# 1. Page Config
st.set_page_config(page_title="Black Vortex - Migration Support AI", page_icon="🌍", layout="wide")

# 2. Add your Groq API Key HERE or via Streamlit secrets
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY", ""))

client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# --- Colorful Black Vortex Theme ---
st.markdown("""
<style>
:root {
    --bv-purple: #7c3aed;
    --bv-blue: #2563eb;
    --bv-cyan: #06b6d4;
    --bv-pink: #ec4899;
    --bv-orange: #f97316;
    --bv-green: #10b981;
    --bv-ink: #16213e;
    --bv-muted: #64748b;
}

/* Page background + typography */
.stApp {
    background:
        radial-gradient(circle at 8% 5%, rgba(124,58,237,.16), transparent 25%),
        radial-gradient(circle at 92% 8%, rgba(6,182,212,.14), transparent 23%),
        radial-gradient(circle at 80% 75%, rgba(236,72,153,.10), transparent 25%),
        linear-gradient(180deg, #f8fbff 0%, #eef4ff 48%, #f8f7ff 100%);
}

section.main > div.block-container {
    max-width: 1180px !important;
    padding-top: 2rem !important;
    padding-bottom: 9rem !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #17133b 0%, #21174f 48%, #102f4e 100%) !important;
    border-right: 1px solid rgba(255,255,255,.10) !important;
}
section[data-testid="stSidebar"] * {
    color: #f8fbff;
}
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #c8d4ea !important;
}
section[data-testid="stSidebar"] .stButton > button,
section[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
    background: rgba(255,255,255,.09) !important;
    border: 1px solid rgba(255,255,255,.14) !important;
    color: #fff !important;
    border-radius: 12px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(124,58,237,.42) !important;
    border-color: rgba(255,255,255,.28) !important;
    transform: translateY(-1px);
}

/* Hero header */
.bv-hero {
    position: relative;
    overflow: hidden;
    padding: 1.45rem 1.65rem 1.35rem;
    margin-bottom: 1rem;
    border-radius: 24px;
    color: white;
    background: linear-gradient(120deg, #17133b 0%, #41217a 42%, #0f6da8 100%);
    box-shadow: 0 18px 42px rgba(45, 35, 104, .22);
}
.bv-hero::before,
.bv-hero::after {
    content: "";
    position: absolute;
    border-radius: 999px;
    filter: blur(4px);
    opacity: .42;
}
.bv-hero::before {
    width: 180px;
    height: 180px;
    right: -45px;
    top: -80px;
    background: #ec4899;
}
.bv-hero::after {
    width: 160px;
    height: 160px;
    left: 48%;
    bottom: -115px;
    background: #06b6d4;
}
.bv-hero-content { position: relative; z-index: 1; }
.bv-brand {
    font-size: 2.4rem;
    line-height: 1;
    font-weight: 800;
    letter-spacing: -0.04em;
}
.bv-gradient-text {
    background: linear-gradient(90deg, #fff, #a5f3fc, #fbcfe8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.bv-subtitle {
    margin-top: .48rem;
    font-size: 1.08rem;
    font-weight: 600;
    color: #e9ddff;
}
.bv-caption {
    margin-top: .3rem;
    color: #cbd5f5;
    font-size: .92rem;
}
.bv-badge-row { margin-top: .85rem; display:flex; flex-wrap:wrap; gap:.45rem; }
.bv-badge {
    display:inline-block;
    padding:.34rem .65rem;
    border-radius:999px;
    font-size:.78rem;
    font-weight:700;
    color:#fff;
    background:rgba(255,255,255,.13);
    border:1px solid rgba(255,255,255,.18);
    backdrop-filter: blur(8px);
}

/* Journey expander */
div[data-testid="stExpander"] {
    border: 1px solid rgba(124,58,237,.16) !important;
    border-radius: 18px !important;
    background: rgba(255,255,255,.75) !important;
    box-shadow: 0 12px 32px rgba(61,45,111,.08) !important;
    backdrop-filter: blur(10px);
}

/* Journey cards */
.bv-journey-card {
    padding: .85rem .75rem;
    min-height: 108px;
    border-radius: 16px;
    color: #1f2937;
    border: 1px solid rgba(255,255,255,.7);
    box-shadow: 0 8px 18px rgba(31,41,55,.07);
    transition: transform .18s ease, box-shadow .18s ease;
}
.bv-journey-card:hover { transform: translateY(-3px); box-shadow: 0 14px 24px rgba(31,41,55,.11); }
.bv-journey-card .icon { font-size: 1.55rem; }
.bv-journey-card .title { margin-top:.25rem; font-weight:800; font-size:.95rem; }
.bv-journey-card .desc { margin-top:.15rem; font-size:.75rem; color:#475569; }
.bv-journey-1 { background: linear-gradient(135deg,#ede9fe,#ddd6fe); }
.bv-journey-2 { background: linear-gradient(135deg,#dbeafe,#bfdbfe); }
.bv-journey-3 { background: linear-gradient(135deg,#dcfce7,#bbf7d0); }
.bv-journey-4 { background: linear-gradient(135deg,#fef3c7,#fde68a); }
.bv-journey-5 { background: linear-gradient(135deg,#cffafe,#a5f3fc); }
.bv-journey-6 { background: linear-gradient(135deg,#fce7f3,#fbcfe8); }

/* Chat messages: colorful but readable */
[data-testid="stChatMessage"] {
    border-radius: 20px !important;
    padding: .85rem 1rem !important;
    margin: .65rem 0 !important;
    box-shadow: 0 7px 20px rgba(30,41,59,.06) !important;
    border: 1px solid rgba(148,163,184,.12) !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg, #eef2ff, #f5f3ff) !important;
    border-left: 4px solid #7c3aed !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: linear-gradient(135deg, #ecfeff, #f0fdf4) !important;
    border-left: 4px solid #06b6d4 !important;
}
[data-testid="stChatMessage"] img {
    border-radius: 16px !important;
}

/* General buttons */
.stButton > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    transition: all .18s ease !important;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 8px 18px rgba(79,70,229,.16);
}

/* Inputs */
div[data-baseweb="input"] > div,
div[data-baseweb="textarea"] > div,
div[data-baseweb="select"] > div {
    border-radius: 12px !important;
    border-color: rgba(124,58,237,.18) !important;
}

/* Fixed chat bar styling, preserving its current sidebar behavior */
.st-key-fixed_chat_bar {
    background: linear-gradient(135deg, rgba(255,255,255,.96), rgba(245,243,255,.96)) !important;
    border: 1px solid rgba(124,58,237,.16) !important;
    box-shadow: 0 16px 40px rgba(58, 45, 116, .22) !important;
    backdrop-filter: blur(16px) !important;
}
.st-key-fixed_chat_bar [data-testid="stChatInput"] > div {
    border: 2px solid rgba(99,102,241,.22) !important;
    background: white !important;
    box-shadow: inset 0 0 0 1px rgba(255,255,255,.7) !important;
}
.st-key-fixed_chat_bar [data-testid="stChatInput"]:focus-within > div {
    border-color: rgba(124,58,237,.65) !important;
    box-shadow: 0 0 0 4px rgba(124,58,237,.11) !important;
}
.st-key-fixed_chat_bar [data-testid="stPopover"] button {
    border-radius: 13px !important;
    background: linear-gradient(135deg,#7c3aed,#2563eb) !important;
    color:white !important;
    border: none !important;
    box-shadow: 0 8px 18px rgba(79,70,229,.28) !important;
}

/* Gentle entrance animation */
.bv-hero, [data-testid="stChatMessage"], .bv-journey-card {
    animation: bvFadeUp .32s ease both;
}
@keyframes bvFadeUp {
    from { opacity:0; transform:translateY(5px); }
    to { opacity:1; transform:translateY(0); }
}

@media (max-width: 768px) {
    .bv-brand { font-size: 1.85rem; }
    .bv-hero { padding: 1.15rem 1.05rem; border-radius: 20px; }
    section.main > div.block-container { padding-top: 1rem !important; }
}
</style>
""", unsafe_allow_html=True)

# --- MIGRATION SUPPORT MODE ---
MIGRATION_SYSTEM_PROMPT = """
You are Black Vortex, a safe, respectful Migration Support Assistant.
Your purpose is to help migrants, refugees, displaced people, and families understand practical options
for moving safely and settling into a new place.

Your priorities are:
1. Safety, dignity, and non-discrimination.
2. Clear, simple language; avoid complicated legal jargon.
3. Practical help with documents, jobs, housing, food, education, healthcare access, transport,
   translation, budgeting, scam awareness, and finding trusted services.
4. Never encourage illegal border crossing, document fraud, trafficking, exploitation, or evading authorities.
5. Do not pretend to be a lawyer, doctor, immigration officer, or government official.
6. Do not ask users to share sensitive credentials such as Aadhaar numbers, passport numbers,
   bank PINs, passwords, OTPs, or full identity documents in chat.
7. When rules depend on country/state or can change, clearly say that the user should verify with
   the relevant official government/aid organisation website.
8. For emergencies, tell the user to contact local emergency services or a trusted local organisation.
9. Treat every person with dignity, including migrant workers, refugees, asylum-seekers, students,
   families, and people displaced by disasters or conflict.

If a user gives a migration problem, respond with:
- What the problem is
- Safe next steps
- Documents/information that may be needed (without asking for sensitive numbers)
- Possible official/trusted places to seek help
- A warning about common scams when relevant
"""

MIGRATION_RESOURCES = [
    ("🇮🇳 e-Shram", "https://eshram.gov.in/", "India's official portal for unorganised workers, including migrant workers."),
    ("🍚 One Nation One Ration Card", "https://dfpd.gov.in/distribution-of-food-grains/en", "Official information on ration portability for eligible NFSA beneficiaries who move within India."),
    ("🌍 UNHCR Help", "https://help.unhcr.org/", "Country-specific information for refugees, asylum-seekers and stateless people."),
    ("🛡️ UNHCR Services", "https://www.unhcr.org/services-refugees-asylum-seekers-and-stateless-people", "Trusted information on protection, education, work, family reunification and related services."),
]

MIGRATION_QUICK_GUIDES = {
    "🧳 Moving Safely": [
        "Keep copies of important documents in a secure place.",
        "Share your travel plan with a trusted person.",
        "Avoid unofficial agents who promise guaranteed visas, jobs, or border crossings.",
        "Never hand over passwords, OTPs, or bank PINs to an agent."
    ],
    "💼 Finding Work": [
        "Ask for a written job offer with employer name, location, duties, hours and pay.",
        "Check whether recruitment fees are legal and reasonable before paying anything.",
        "Never surrender your original identity documents to an unknown recruiter.",
        "For India, migrant and unorganised workers can explore the official e-Shram portal."
    ],
    "🏠 Housing": [
        "Ask for the rent, deposit, rules and notice period in writing.",
        "Confirm the address before paying a deposit.",
        "Keep a record of payments and receipts.",
        "Be careful with listings that demand urgent cash payments."
    ],
    "🍚 Food & Essentials": [
        "Check whether your local public-distribution or food-support benefits are portable.",
        "In India, eligible NFSA beneficiaries can use One Nation One Ration Card portability after the required authentication.",
        "Look for local shelters, community kitchens, NGOs, and municipal support services."
    ],
    "🎓 Education": [
        "Ask the destination school/college about admission requirements and language support.",
        "Keep school records and certificates safely stored.",
        "Ask about scholarships, fee support, transport and accommodation where applicable."
    ],
    "🏥 Health": [
        "Carry a basic record of medicines and prescriptions when travelling.",
        "Find the nearest public hospital/clinic before moving when possible.",
        "In urgent situations, contact local emergency services or a trusted medical provider."
    ],
    "🚨 Scam Protection": [
        "No trustworthy service should need your OTP or banking PIN.",
        "Be suspicious of 'guaranteed visa', 'guaranteed job', or 'pay now or lose your place' claims.",
        "Verify organisations using their official websites or known local offices.",
        "Keep screenshots, receipts and messages if you need to report fraud."
    ],
}

def migration_response(prompt_text):
    """Answer migration-support questions using the normal AI model with a safety-focused system prompt."""
    if not client:
        return "Migration Support is available, but the Groq API key is missing. Configure it in .streamlit/secrets.toml."
    messages = [
        {"role": "system", "content": MIGRATION_SYSTEM_PROMPT},
        {"role": "user", "content": prompt_text},
    ]
    return safe_chat_completion(client, messages, max_tokens=700)


def safe_chat_completion(client, messages, max_tokens=None):
    if not client or not client.api_key:
        raise ValueError("Groq API key is missing or invalid. Check .streamlit/secrets.toml.")

    # List of active production models on Groq with fallbacks
    candidate_models = [
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "qwen/qwen3.6-27b",
        "llama-3.1-8b-instant",
    ]

    last_exception = None
    for model_id in candidate_models:
        try:
            kwargs = {"model": model_id, "messages": messages}
            if max_tokens:
                kwargs["max_tokens"] = max_tokens
            response = client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            err_msg = str(e)
            # Catch genuine 401 Authentication/API key issues immediately
            if any(code in err_msg for code in ["401", "Authentication", "Invalid API Key"]):
                raise Exception(f"API Key Error: {e}")
            
            # Save exception and try the next candidate model
            last_exception = e
            continue

    raise last_exception


def generate_chat_title(first_user_message):
    """Generate a short title for the chat using Groq."""
    if not client:
        return (
            first_user_message[:20] + "..."
            if len(first_user_message) > 20
            else first_user_message
        )
    try:
        title = safe_chat_completion(
            client,
            messages=[
                {
                    "role": "system",
                    "content": "Create a brief 3-5 word title summarizing the user message. Output ONLY the title text, nothing else.",
                },
                {"role": "user", "content": first_user_message},
            ],
            max_tokens=15,
        )
        return title.strip().strip('"')
    except Exception:
        return (
            first_user_message[:20] + "..."
            if len(first_user_message) > 20
            else first_user_message
        )


def fetch_generated_image(prompt):
    """Refines prompt using Groq and fetches raw image bytes with fallback servers."""
    detailed_prompt = prompt
    if client:
        try:
            refined = safe_chat_completion(
                client,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert AI image prompt engineer. Convert the user's request into a short, detailed image prompt under 25 words. Do not use quotes or special characters. Output ONLY the refined prompt.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=40,
            )
            detailed_prompt = refined.strip().replace('"', "").replace("'", "")
        except Exception:
            detailed_prompt = prompt

    seed = int(time.time())
    encoded_prompt = urllib.parse.quote(detailed_prompt)

    urls = [
        f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux&nologo=true&seed={seed}",
        f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&seed={seed}",
    ]

    for url in urls:
        try:
            response = requests.get(url, timeout=15)
            if response.status_code == 200 and len(response.content) > 1000:
                return response.content, detailed_prompt
        except Exception:
            continue

    return None, detailed_prompt


# --- Initialize Device-Isolated Session State ---
if "all_data" not in st.session_state:
    st.session_state.all_data = {"Main Account": {}}

if "current_account" not in st.session_state:
    st.session_state.current_account = list(st.session_state.all_data.keys())[0]

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None

if "scroll_to_bottom" not in st.session_state:
    st.session_state.scroll_to_bottom = False


# --- Sidebar UI ---
st.sidebar.title("👤 Accounts & Chats")

accounts_list = list(st.session_state.all_data.keys())
current_acc_index = (
    accounts_list.index(st.session_state.current_account)
    if st.session_state.current_account in accounts_list
    else 0
)

selected_account = st.sidebar.selectbox(
    "Active Account:", accounts_list, index=current_acc_index
)

if selected_account != st.session_state.current_account:
    st.session_state.current_account = selected_account
    st.session_state.active_chat_id = None
    st.rerun()

col_acc1, col_acc2 = st.sidebar.columns(2)

with col_acc1:
    with st.popover("➕ New Acc", use_container_width=True):
        new_acc_name = st.text_input("Account Name", key="new_acc_input")
        if st.button("Create", use_container_width=True):
            clean_name = new_acc_name.strip()
            if clean_name:
                if clean_name not in st.session_state.all_data:
                    st.session_state.all_data[clean_name] = {}
                    st.session_state.current_account = clean_name
                    st.session_state.active_chat_id = None
                    st.success(f"Account '{clean_name}' created!")
                    st.rerun()
                else:
                    st.warning("Account already exists!")

with col_acc2:
    with st.popover("🗑️ Delete", use_container_width=True):
        st.write(f"Delete account **'{st.session_state.current_account}'**?")
        st.caption("This will permanently remove all its chats for this device session.")
        if st.button("Confirm Delete", type="primary", use_container_width=True):
            del st.session_state.all_data[st.session_state.current_account]

            if not st.session_state.all_data:
                st.session_state.all_data = {"Main Account": {}}

            st.session_state.current_account = list(
                st.session_state.all_data.keys()
            )[0]
            st.session_state.active_chat_id = None
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("🌍 Migration Help Hub")
st.sidebar.caption("Practical, safe support for migrants, workers, students, refugees and families.")

migration_topic = st.sidebar.selectbox(
    "Quick help topic",
    ["Select a topic"] + list(MIGRATION_QUICK_GUIDES.keys()),
    key="migration_topic"
)

if migration_topic != "Select a topic":
    with st.sidebar.expander(migration_topic, expanded=True):
        for tip in MIGRATION_QUICK_GUIDES[migration_topic]:
            st.markdown(f"• {tip}")

# Dropdown Menu for Extra Links
with st.sidebar.expander("🔗 Extra Links", expanded=False):
    for resource_name, resource_url, resource_desc in MIGRATION_RESOURCES:
        st.markdown(f"[{resource_name}]({resource_url})")
        st.caption(resource_desc)

st.sidebar.info("🔒 Privacy rule: never enter sensitive credentials, PINs, or ID numbers into the chatbot.")

active_acc = st.session_state.current_account
account_chats = st.session_state.all_data.get(active_acc, {})

st.sidebar.subheader("💬 Conversations")

if st.sidebar.button("➕ New Chat", use_container_width=True):
    st.session_state.active_chat_id = None
    st.rerun()

for cid in reversed(list(account_chats.keys())):
    chat_data = account_chats[cid]
    if isinstance(chat_data, dict):
        chat_title = chat_data.get("title", f"Chat {cid}")
    else:
        chat_title = f"Chat {cid}"

    is_active = st.session_state.active_chat_id == cid
    button_label = f"📌 {chat_title}" if is_active else f"📝 {chat_title}"

    col1, col2 = st.sidebar.columns([0.8, 0.2])

    with col1:
        if st.button(button_label, key=f"btn_{cid}", use_container_width=True):
            st.session_state.active_chat_id = cid
            st.rerun()

    with col2:
        if st.button("🗑️", key=f"del_{cid}", use_container_width=True):
            del st.session_state.all_data[active_acc][cid]

            if st.session_state.active_chat_id == cid:
                st.session_state.active_chat_id = None

            st.rerun()


# --- Main App Interface ---
st.markdown(f"""
<div class="bv-hero">
  <div class="bv-hero-content">
    <div class="bv-brand"><span class="bv-gradient-text">🌍 Black Vortex</span></div>
    <div class="bv-subtitle">Migration Support AI</div>
    <div class="bv-caption">A friendly digital companion for safer journeys, work, study and settlement.</div>
    <div class="bv-badge-row">
      <span class="bv-badge">🤖 Powered by AI</span>
      <span class="bv-badge">🛡️ Safety-first</span>
      <span class="bv-badge">🌐 Migration-focused</span>
      <span class="bv-badge">👤 {active_acc}</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

with st.expander("🧭 Migration Journey — What can Black Vortex help with?", expanded=False):
    dash_cols = st.columns(6)
    dashboard_items = [
        ("🧳", "Plan", "Travel & documents"),
        ("💼", "Work", "Jobs & worker safety"),
        ("🏠", "Settle", "Housing & essentials"),
        ("🎓", "Learn", "School & skills"),
        ("🗣️", "Translate", "Language support"),
        ("🛡️", "Protect", "Scam & safety awareness"),
    ]
    for idx, (col, (icon, title, desc)) in enumerate(zip(dash_cols, dashboard_items), start=1):
        with col:
            st.markdown(
                f"<div class='bv-journey-card bv-journey-{idx}'>"
                f"<div class='icon'>{icon}</div>"
                f"<div class='title'>{title}</div>"
                f"<div class='desc'>{desc}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )


if (
    st.session_state.active_chat_id
    and st.session_state.active_chat_id in account_chats
):
    selected = account_chats[st.session_state.active_chat_id]
    if isinstance(selected, dict):
        current_messages = selected.get("messages", [])
    else:
        current_messages = selected
else:
    current_messages = [
        {
            "role": "system",
            "content": MIGRATION_SYSTEM_PROMPT + f"\nCurrent profile name: {active_acc}. Do not infer sensitive information from the name.",
        }
    ]

# Display Messages
for msg in current_messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            if msg.get("type") == "image":
                st.image(msg["content"], caption=msg.get("prompt_text"))
            else:
                st.write(msg["content"])


# --- AUTO-SCROLL AFTER SENDING A MESSAGE ---
# This flag is set only after a message is processed, so normal manual scrolling
# and opening older conversations are not interrupted.
if st.session_state.pop("scroll_to_bottom", False):
    st.components.v1.html(
        """
        <script>
        (() => {
            const scrollToBottom = () => {
                try {
                    const parentDoc = window.parent.document;
                    const candidates = [
                        parentDoc.scrollingElement,
                        parentDoc.documentElement,
                        parentDoc.body,
                        parentDoc.querySelector('[data-testid="stAppViewContainer"]'),
                        parentDoc.querySelector('section.main')
                    ].filter(Boolean);

                    candidates.forEach((el) => {
                        try {
                            if (el === parentDoc.scrollingElement || el === parentDoc.documentElement || el === parentDoc.body) {
                                el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
                            } else {
                                el.scrollTo({ top: el.scrollHeight, behavior: 'smooth' });
                            }
                        } catch (_) {}
                    });

                    try {
                        window.parent.scrollTo({ top: parentDoc.documentElement.scrollHeight, behavior: 'smooth' });
                    } catch (_) {}
                } catch (_) {}
            };

            // Run repeatedly because Streamlit may still be laying out the
            // newly-generated assistant response or an image.
            setTimeout(scrollToBottom, 40);
            setTimeout(scrollToBottom, 180);
            setTimeout(scrollToBottom, 450);
            setTimeout(scrollToBottom, 900);
        })();
        </script>
        """,
        height=0,
    )


# --- FIXED BOTTOM CHAT BAR ---
# Keep the plus button and chat input together. The whole bar follows the
# main content area: centered when the sidebar is closed and shifted right
# when the sidebar is open, similar to a modern chat application.
st.markdown("""
<style>
/* Main chat footer: fixed, centered by default. */
.st-key-fixed_chat_bar {
    position: fixed !important;
    left: 50% !important;
    bottom: 0.85rem !important;
    transform: translateX(-50%) !important;
    width: min(920px, calc(100vw - 2rem)) !important;
    z-index: 999999 !important;
    padding: 0.15rem 0.2rem !important;
    background: var(--background-color, #ffffff) !important;
    border-radius: 18px !important;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.14) !important;
}

/* Preserve the two-column alignment: plus button on the left, prompt on right. */
.st-key-fixed_chat_bar [data-testid="stHorizontalBlock"] {
    align-items: center !important;
    gap: 0.35rem !important;
}

/* Keep the plus column compact. */
.st-key-fixed_chat_bar [data-testid="column"]:first-child {
    min-width: 48px !important;
    width: 48px !important;
    flex: 0 0 48px !important;
}

/* Make the actual chat input fill the remaining footer width. */
.st-key-fixed_chat_bar [data-testid="stChatInput"] {
    position: static !important;
    width: 100% !important;
    max-width: none !important;
    transform: none !important;
    bottom: auto !important;
    left: auto !important;
}

.st-key-fixed_chat_bar [data-testid="stChatInput"] > div {
    background: transparent !important;
    border-radius: 16px !important;
    box-shadow: none !important;
}

/* When the sidebar is OPEN, center the footer in the remaining main area
   instead of letting it sit underneath the sidebar. */
@media (min-width: 769px) {
    body:has([data-testid="stSidebar"][aria-expanded="true"]) .st-key-fixed_chat_bar {
        left: calc(50% + 10.5rem) !important;
        width: min(920px, calc(100vw - 21rem - 2rem)) !important;
    }
}

/* Extra-wide screens: use a little more room while keeping the bar centered. */
@media (min-width: 1400px) {
    body:has([data-testid="stSidebar"][aria-expanded="true"]) .st-key-fixed_chat_bar {
        left: calc(50% + 11rem) !important;
        width: min(980px, calc(100vw - 22rem - 2rem)) !important;
    }
}

/* Reserve space so the last message never disappears behind the fixed bar. */
section.main > div.block-container {
    padding-bottom: 8rem !important;
}

/* Mobile: sidebar becomes an overlay, so keep the bar within the viewport. */
@media (max-width: 768px) {
    .st-key-fixed_chat_bar {
        left: 50% !important;
        width: calc(100vw - 1rem) !important;
        bottom: 0.45rem !important;
    }

    section.main > div.block-container {
        padding-bottom: 7rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

pending_prompt = None

with st.container(key="fixed_chat_bar"):
    col_plus, col_input = st.columns([0.08, 0.92], vertical_alignment="center")

    with col_plus:
        with st.popover("➕", help="Quick Tools & Features", use_container_width=True):
            st.markdown("### 🧰 Pick a Feature")
            feature_choice = st.radio(
                "Choose an option:",
                ["🗺️ Build Migration Plan", "🗣️ Translation Helper", "🚨 Scam Check"],
                key="feature_choice_radio"
            )
            st.markdown("---")

            if feature_choice == "🗺️ Build Migration Plan":
                destination = st.text_input("Destination country/state/city", key="plan_destination")
                purpose = st.selectbox("Main purpose", ["Work", "Study", "Family", "Safety", "Other"], key="plan_purpose")
                language = st.text_input("Preferred language", value="English", key="plan_language")
                if st.button("Generate & Send Plan", key="btn_create_plan", use_container_width=True):
                    if destination.strip():
                        pending_prompt = f"Create a practical migration preparation plan for someone moving to {destination.strip()} for {purpose}. Preferred language: {language}. Cover documents to check, travel safety, housing, work/study, food, healthcare, language, scam prevention, and trusted official resources. Do not ask for sensitive ID numbers."
                    else:
                        st.warning("Please enter a destination.")

            elif feature_choice == "🗣️ Translation Helper":
                target_language = st.text_input("Translate into", value="Hindi", key="target_language")
                text_to_translate = st.text_area("Text to translate", key="text_to_translate")
                if st.button("Translate & Send", key="btn_translate", use_container_width=True):
                    if text_to_translate.strip():
                        pending_prompt = f"Translate the following practical message into {target_language}. Preserve meaning and keep it easy to understand. Do not add extra information.\n\n{text_to_translate}"
                    else:
                        st.warning("Enter some text first.")

            elif feature_choice == "🚨 Scam Check":
                suspicious_message = st.text_area("Paste a job/visa/rental message to check", key="scam_message")
                if st.button("Analyze & Send", key="btn_scam_check", use_container_width=True):
                    if suspicious_message.strip():
                        pending_prompt = "Analyze this message for possible migration, recruitment, rental or document scams. Identify red flags, explain why they matter, and suggest safe verification steps. Do not make a definitive legal accusation.\n\n" + suspicious_message
                    else:
                        st.warning("Paste a message first.")

    with col_input:
        prompt_input = st.chat_input(
            "Ask Black Vortex or record your voice...",
            accept_audio=True,
            key="user_chat_input",
        )

# Determine final message string from either chat input, tool action button, or voice input
user_message = ""
prompt_audio_bytes = None

if pending_prompt:
    user_message = pending_prompt
elif prompt_input:
    if prompt_input.audio:
        prompt_audio_bytes = prompt_input.audio
    else:
        user_message = prompt_input.text

# Process input when triggered
if user_message or prompt_audio_bytes:
    is_image_request = False

    # Handle Audio Input First
    if prompt_audio_bytes:
        with st.chat_message("user"):
            st.audio(prompt_audio_bytes, format="audio/wav")
            with st.spinner("🎙️ Transcribing voice..."):
                try:
                    audio_data = prompt_audio_bytes.read()
                    translation = client.audio.transcriptions.create(
                        file=("recording.wav", audio_data),
                        model="whisper-large-v3-turbo",
                        language="en",
                    )
                    user_message = translation.text
                    st.write(f"*(Transcribed: '{user_message}')*")
                except Exception as e:
                    st.error(f"❌ Transcription failed: {e}")
                    st.stop()
    else:
        with st.chat_message("user"):
            st.write(user_message)

    # Manage Active Chat State
    if (
        st.session_state.active_chat_id is None
        or st.session_state.active_chat_id not in account_chats
    ):
        new_id = str(int(time.time()))
        title = generate_chat_title(user_message)

        st.session_state.active_chat_id = new_id

        if active_acc not in st.session_state.all_data:
            st.session_state.all_data[active_acc] = {}

        st.session_state.all_data[active_acc][new_id] = {
            "title": title,
            "messages": [
                {
                    "role": "system",
                    "content": MIGRATION_SYSTEM_PROMPT + f"\nCurrent profile name: {active_acc}. Do not infer sensitive information from the name.",
                }
            ],
        }
        current_messages = st.session_state.all_data[active_acc][new_id][
            "messages"
        ]

    current_messages.append({"role": "user", "content": user_message})

    # Detect Image Request
    image_keywords = [
        "generate image", "draw", "create image", "picture of",
        "show me an image", "make an image", "paint", "sketch",
        "render", "illustration of", "photo of"
    ]
    is_image_request = any(kw in user_message.lower() for kw in image_keywords)

    # Process Assistant Output
    with st.chat_message("assistant"):
        if is_image_request:
            with st.spinner("🎨 Generating your image..."):
                img_data, detailed_prompt = fetch_generated_image(user_message)

                if img_data:
                    b64_img = base64.b64encode(img_data).decode("utf-8")
                    img_str = f"data:image/jpeg;base64,{b64_img}"

                    st.image(img_str, caption=f"Prompt: {detailed_prompt}")
                    current_messages.append({
                        "role": "assistant",
                        "type": "image",
                        "content": img_str,
                        "prompt_text": f"Prompt: {detailed_prompt}",
                    })
                else:
                    st.error("⚠️ Image generation server timed out. Please try sending the prompt again!")
        else:
            with st.spinner("Thinking..."):
                api_messages = [
                    {"role": m["role"], "content": m["content"]}
                    for m in current_messages
                    if m.get("type") != "image"
                ]
                if client:
                    try:
                        reply = safe_chat_completion(client, api_messages)
                    except Exception as e:
                        reply = f"⚠️ Unable to reach Groq API: {e}"
                else:
                    reply = "Groq API key missing. Configure it in .streamlit/secrets.toml."
                st.write(reply)
                current_messages.append({"role": "assistant", "content": reply})

    # Refresh UI
    st.session_state.all_data[active_acc][st.session_state.active_chat_id][
        "messages"
    ] = current_messages

    # On the next Streamlit rerun, automatically take the user to the newest message.
    st.session_state.scroll_to_bottom = True
    st.rerun()
