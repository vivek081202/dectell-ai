"""
DecTell AI — UI Design System
"""
import requests
import streamlit as st

# ── Pexels image URLs (direct CDN — load in browser at runtime) ───────────────
PEXELS = {
    "hero_bg":      "https://images.pexels.com/photos/7567443/pexels-photo-7567443.jpeg?auto=compress&cs=tinysrgb&w=1400",
    "analytics":    "https://images.pexels.com/photos/590022/pexels-photo-590022.jpeg?auto=compress&cs=tinysrgb&w=900",
    "team":         "https://images.pexels.com/photos/3183197/pexels-photo-3183197.jpeg?auto=compress&cs=tinysrgb&w=900",
    "laptop_dark":  "https://images.pexels.com/photos/1181671/pexels-photo-1181671.jpeg?auto=compress&cs=tinysrgb&w=900",
    "strategy":     "https://images.pexels.com/photos/3184291/pexels-photo-3184291.jpeg?auto=compress&cs=tinysrgb&w=900",
    "meeting":      "https://images.pexels.com/photos/669615/pexels-photo-669615.jpeg?auto=compress&cs=tinysrgb&w=900",
    "code":         "https://images.pexels.com/photos/1181244/pexels-photo-1181244.jpeg?auto=compress&cs=tinysrgb&w=900",
    "research":     "https://images.pexels.com/photos/3760067/pexels-photo-3760067.jpeg?auto=compress&cs=tinysrgb&w=900",
}

# ── Lottie URLs ────────────────────────────────────────────────────────────────
LOTTIE_URLS = {
    "hero":       "https://assets9.lottiefiles.com/packages/lf20_qp1q7mct.json",
    "upload":     "https://assets4.lottiefiles.com/packages/lf20_szlepvdh.json",
    "cleaning":   "https://assets7.lottiefiles.com/packages/lf20_uu0x8lqv.json",
    "eda":        "https://assets3.lottiefiles.com/packages/lf20_qm8eqzse.json",
    "model":      "https://assets5.lottiefiles.com/packages/lf20_fcfjwiyb.json",
    "simulation": "https://assets2.lottiefiles.com/packages/lf20_uwWgICKCxj.json",
    "causal":     "https://assets9.lottiefiles.com/packages/lf20_xyadoh9h.json",
    "chat":       "https://assets5.lottiefiles.com/packages/lf20_2cwDXD.json",
    "report":     "https://assets5.lottiefiles.com/packages/lf20_V9t630.json",
    "dashboard":  "https://assets1.lottiefiles.com/packages/lf20_qyy8GLWHCT.json",
    "about":      "https://assets3.lottiefiles.com/packages/lf20_w51pcehl.json",
    "contact":    "https://assets10.lottiefiles.com/packages/lf20_u25cckyh.json",
}


@st.cache_data(show_spinner=False)
def load_lottie(url: str) -> dict | None:
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def lottie_inline(key: str, height: int = 160):
    try:
        from streamlit_lottie import st_lottie as _stl
        anim = load_lottie(LOTTIE_URLS.get(key, ""))
        if anim:
            _stl(anim, height=height, key=f"lottie_{key}_{height}", speed=0.8)
    except Exception:
        pass


# ── Horizontal top navbar ─────────────────────────────────────────────────────
def render_topnav(active: str = "Home"):
    """
    Render a sticky horizontal navbar using streamlit-option-menu.
    active: the label of the currently active page.
    """
    try:
        from streamlit_option_menu import option_menu
        nav_items   = ["Home", "About", "Upload", "Analysis", "Intelligence", "Dashboard", "Contact"]
        nav_icons   = ["house","info-circle","upload","bar-chart-line","lightning","speedometer2","envelope"]
        selected = option_menu(
            menu_title=None,
            options=nav_items,
            icons=nav_icons,
            default_index=nav_items.index(active) if active in nav_items else 0,
            orientation="horizontal",
            styles={
                "container":      {"padding":"0!important","background":"#0E1624","border-bottom":"1px solid #2C3F60"},
                "icon":           {"color":"#6A88A8","font-size":"0.8rem"},
                "nav-link":       {"font-size":"0.8rem","font-weight":"500","color":"#9BB5CF",
                                   "padding":"0.65rem 1rem","border-radius":"0","font-family":"Inter,sans-serif"},
                "nav-link-selected": {"background":"rgba(0,212,255,0.08)","color":"#00D4FF",
                                      "border-bottom":"2px solid #00D4FF","font-weight":"600"},
            },
        )
        return selected
    except Exception:
        return active


# ── Global CSS ─────────────────────────────────────────────────────────────────
def inject_global_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
    --bg:       #131C2E;
    --surface:  #1A2540;
    --surface2: #213050;
    --surface3: #283860;
    --border:   #2C3F60;
    --border2:  #3A5278;
    --accent:   #00D4FF;
    --accent-lo:rgba(0,212,255,0.08);
    --accent2:  #7C3AED;
    --green:    #10B981;
    --warn:     #F59E0B;
    --danger:   #EF4444;
    --text:     #DDE8F8;
    --subtle:   #9BB5CF;
    --muted:    #6A88A8;
    --faint:    #3A5070;
    --sans:     'Inter', sans-serif;
    --display:  'Space Grotesk', sans-serif;
    --mono:     'JetBrains Mono', monospace;
    --r:        10px;
    --r-lg:     14px;
    --r-xl:     20px;
}

/* ── App shell ── */
.stApp { background: var(--bg) !important; font-family: var(--sans) !important; color: var(--text) !important; }
.main .block-container { padding: 0 2.5rem 4rem !important; max-width: 1380px !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background-color: #0E1624 !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebarNav"] a {
    font-size: 0.855rem !important; font-weight: 500 !important;
    color: var(--subtle) !important; padding: 0.4rem 0.75rem !important;
    border-radius: var(--r) !important; transition: all 0.15s !important; text-decoration: none !important;
}
[data-testid="stSidebarNav"] a:hover { background: var(--surface2) !important; color: var(--text) !important; }
[data-testid="stSidebarNav"] a[aria-current="page"] {
    background: var(--accent-lo) !important; color: var(--accent) !important;
    border-left: 2px solid var(--accent) !important;
}
/* Sidebar toggle — style only, never touch layout props */
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    background-color: #0E1624 !important;
    border: 1px solid var(--border2) !important;
    border-left: none !important;
    border-radius: 0 var(--r) var(--r) 0 !important;
}
[data-testid="stSidebarCollapsedControl"] svg,
[data-testid="collapsedControl"] svg { color: var(--subtle) !important; }

/* ── Typography ── */
h1,h2,h3 { font-family: var(--display) !important; letter-spacing: -0.02em !important; }
h1 { font-size: 2.1rem !important; font-weight: 700 !important; color: var(--text) !important; }
h2 { font-size: 1.45rem !important; font-weight: 600 !important; color: var(--text) !important; }
h3 { font-size: 1.1rem !important;  font-weight: 600 !important; color: var(--subtle) !important; }
p, li { font-size: 0.9rem !important; color: var(--subtle) !important; line-height: 1.65 !important; }
code { font-family: var(--mono) !important; background: var(--surface2) !important; color: var(--accent) !important;
       padding: 0.12em 0.4em !important; border-radius: 4px !important; font-size: 0.82em !important; }

/* ── Buttons ── */

/* Default button — outlined style, visible on dark background */
.stButton > button {
    background: transparent !important;
    color: var(--text) !important;
    border: 1px solid var(--border2) !important;
    border-radius: var(--r) !important;
    font-family: var(--display) !important;
    font-weight: 500 !important;
    font-size: 0.855rem !important;
    letter-spacing: 0.01em !important;
    padding: 0.52rem 1.2rem !important;
    transition: all 0.18s !important;
}
.stButton > button:hover {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border-color: var(--accent) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
}

/* Primary button — filled cyan, dark text */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    background: var(--accent) !important;
    color: #06101C !important;
    border: none !important;
    font-weight: 700 !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
    background: #14E5FF !important;
    color: #06101C !important;
    border: none !important;
    box-shadow: 0 4px 18px rgba(0,212,255,0.28) !important;
}

/* Ensure ALL text inside every button is always visible */
.stButton > button *,
.stButton > button p,
.stButton > button span,
.stButton > button div {
    color: inherit !important;
    background: transparent !important;
    font-size: inherit !important;
    font-weight: inherit !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: var(--r-lg) !important; padding: 1rem 1.25rem !important; transition: border-color 0.2s !important;
}
[data-testid="metric-container"]:hover { border-color: var(--border2) !important; }
[data-testid="stMetricLabel"] { font-size: 0.7rem !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.1em !important; color: var(--muted) !important; }
[data-testid="stMetricValue"] { font-family: var(--display) !important; font-size: 1.6rem !important;
    font-weight: 700 !important; color: var(--text) !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] { background: transparent !important; border-bottom: 1px solid var(--border) !important; gap: 0 !important; }
.stTabs [data-baseweb="tab"] { font-size: 0.845rem !important; font-weight: 500 !important; color: var(--muted) !important;
    background: transparent !important; border: none !important; padding: 0.55rem 1.05rem !important; transition: color 0.15s !important; }
.stTabs [aria-selected="true"] { color: var(--accent) !important; border-bottom: 2px solid var(--accent) !important; background: transparent !important; }

/* ── Inputs ── */
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: var(--r) !important; color: var(--text) !important;
}
.stFileUploader { background: var(--surface) !important; border: 1.5px dashed var(--border2) !important;
    border-radius: var(--r-lg) !important; transition: border-color 0.2s !important; }
.stFileUploader:hover { border-color: var(--accent) !important; }
.stRadio label, .stCheckbox label { font-size: 0.875rem !important; color: var(--subtle) !important; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea {
    background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: var(--r) !important; color: var(--text) !important; font-size: 0.9rem !important;
}

/* ── Expanders ── */
.stExpander { background: var(--surface) !important; border: 1px solid var(--border) !important; border-radius: var(--r) !important; }
.stExpander summary { font-size: 0.875rem !important; font-weight: 600 !important; color: var(--subtle) !important; }

/* ── Alerts ── */
.stAlert { background: var(--surface) !important; border-left: 3px solid var(--accent) !important;
    border-radius: var(--r) !important; font-size: 0.875rem !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: var(--r) !important; overflow: hidden !important; }

/* ── Chat ── */
[data-testid="stChatMessage"] { background: var(--surface) !important; border: 1px solid var(--border) !important;
    border-radius: var(--r-lg) !important; margin-bottom: 0.65rem !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.5rem 0 !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 99px; }

/* ── Page header ── */
.if-page-header { border-bottom: 1px solid var(--border); padding-bottom: 1.25rem; margin-bottom: 2rem; }
.if-page-header .label { font-size: 0.67rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.13em; color: var(--accent); margin-bottom: 0.3rem; }
.if-page-header h1 { margin: 0 0 0.3rem 0 !important; font-size: 1.85rem !important; }
.if-page-header p  { margin: 0 !important; font-size: 0.875rem !important; color: var(--muted) !important; }

/* ── Feature cards ── */
.if-card { background: var(--surface); border: 1px solid var(--border); border-radius: var(--r-lg);
    padding: 1.3rem 1.4rem; transition: border-color 0.2s, transform 0.2s, box-shadow 0.2s; height: 100%; }
.if-card:hover { border-color: var(--border2); transform: translateY(-2px); box-shadow: 0 8px 28px rgba(0,0,0,0.4); }
.if-card .card-icon { width: 38px; height: 38px; background: var(--accent-lo); border-radius: 9px;
    display: flex; align-items: center; justify-content: center; margin-bottom: 0.9rem;
    font-size: 1.1rem; color: var(--accent); }
.if-card .card-title { font-family: var(--display); font-size: 0.9rem; font-weight: 600; color: var(--text); margin-bottom: 0.3rem; }
.if-card .card-desc  { font-size: 0.8rem; color: var(--muted); line-height: 1.55; }

/* ── Image card ── */
.if-img-card { border-radius: var(--r-xl); overflow: hidden; border: 1px solid var(--border); position: relative; }
.if-img-card img { width: 100%; height: 220px; object-fit: cover; display: block;
    filter: brightness(0.75) saturate(0.8); transition: filter 0.3s, transform 0.3s; }
.if-img-card:hover img { filter: brightness(0.9) saturate(1); transform: scale(1.02); }
.if-img-card .overlay { position: absolute; bottom: 0; left: 0; right: 0;
    background: linear-gradient(transparent, rgba(10,15,28,0.92));
    padding: 1.5rem 1.25rem 1rem; }
.if-img-card .overlay-title { font-family: var(--display); font-size: 0.95rem; font-weight: 600; color: var(--text); }
.if-img-card .overlay-sub   { font-size: 0.78rem; color: var(--muted); margin-top: 0.15rem; }

/* ── Hero section ── */
.if-hero {
    position: relative; border-radius: var(--r-xl); overflow: hidden;
    margin-bottom: 0; min-height: 420px;
    background-size: cover; background-position: center;
}
.if-hero-overlay {
    position: absolute; inset: 0;
    background: linear-gradient(105deg, rgba(10,15,28,0.93) 0%, rgba(10,15,28,0.65) 55%, rgba(10,15,28,0.25) 100%);
}
.if-hero-content { position: relative; z-index: 2; padding: 3.5rem 3rem 3rem; }

/* ── Stat strip ── */
.if-stat-strip {
    display: flex; gap: 0; border: 1px solid var(--border); border-radius: var(--r-xl);
    overflow: hidden; background: var(--surface);
}
.if-stat-item { flex: 1; padding: 1.25rem 1.5rem; border-right: 1px solid var(--border); text-align: center; }
.if-stat-item:last-child { border-right: none; }
.if-stat-val  { font-family: var(--display); font-size: 1.6rem; font-weight: 700; color: var(--text); line-height: 1.1; }
.if-stat-lbl  { font-size: 0.68rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; color: var(--muted); margin-top: 0.3rem; }

/* ── Timeline (About page) ── */
.if-timeline { position: relative; padding-left: 2rem; }
.if-timeline::before { content:''; position:absolute; left:0.4rem; top:0; bottom:0;
    width:2px; background:var(--border); border-radius:99px; }
.if-tl-item { position:relative; margin-bottom:2rem; }
.if-tl-dot  { position:absolute; left:-1.62rem; top:0.3rem; width:10px; height:10px;
    background:var(--accent); border-radius:50%; border:2px solid var(--bg); }
.if-tl-label{ font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.12em; color:var(--accent); margin-bottom:0.2rem; }
.if-tl-title{ font-family:var(--display); font-size:1rem; font-weight:600; color:var(--text); margin-bottom:0.3rem; }
.if-tl-body { font-size:0.85rem; color:var(--muted); line-height:1.65; }

/* ── Section label ── */
.section-label { display:block; font-size:0.67rem; font-weight:700; text-transform:uppercase;
    letter-spacing:0.14em; color:var(--accent); margin-bottom:0.65rem; }

/* ── Pill badge ── */
.if-pill { display:inline-flex; align-items:center; gap:0.4rem;
    background:var(--accent-lo); border:1px solid rgba(0,212,255,0.2);
    color:var(--accent); font-size:0.72rem; font-weight:600;
    padding:0.22rem 0.7rem; border-radius:99px; letter-spacing:0.04em; }

/* ── Contact form card ── */
.if-contact-card { background:var(--surface); border:1px solid var(--border); border-radius:var(--r-xl); padding:2rem 2.25rem; }

/* ── Hide chrome ── */
#MainMenu { visibility: hidden; }
footer    { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)


# ── Reusable UI Components ─────────────────────────────────────────────────────

def page_header(label: str, title: str, description: str):
    st.markdown(f"""
<div class="if-page-header">
    <div class="label">{label}</div>
    <h1>{title}</h1>
    <p>{description}</p>
</div>""", unsafe_allow_html=True)


def hero_section(bg_key: str, pill: str, title: str, subtitle: str, extra_html: str = ""):
    """Full-width image-backed hero with gradient overlay."""
    img_url    = PEXELS.get(bg_key, PEXELS["hero_bg"])
    title_html = title.replace("\n", "<br>")
    mb_sub     = "1.8rem" if extra_html else "0"
    html = (
        f'''<div class="if-hero" style="background-image:url(\'{img_url}\'
        );background-size:cover;background-position:center;">'''
        + '''<div class="if-hero-overlay"></div>'''
        + '''<div class="if-hero-content">'''
        + f'''<div class="if-pill" style="margin-bottom:1.1rem;">'''
        + '''<span style="width:5px;height:5px;background:#00D4FF;border-radius:50%;'''
        + '''display:inline-block;margin-right:0.3rem;"></span>'''
        + f'''{pill}</div>'''
        + f'''<div style="font-family:'Space Grotesk',sans-serif;font-size:2.55rem;'''
        + '''font-weight:700;line-height:1.2;margin-bottom:0.85rem;max-width:620px;'''
        + '''background:linear-gradient(135deg,#DDE8F8 0%,#7FBAD8 55%,#00D4FF 100%);'''
        + '''-webkit-background-clip:text;-webkit-text-fill-color:transparent;'''
        + '''background-clip:text;">'''
        + f'''{title_html}</div>'''
        + f'''<p style="font-size:0.96rem;color:#7A9AB8;line-height:1.72;'''
        + f'''max-width:520px;margin:0 0 {mb_sub} 0;">{subtitle}</p>'''
        + f'''{extra_html}'''
        + '''</div></div></div>'''
    )
    st.markdown(html, unsafe_allow_html=True)


def stat_strip(stats: list[tuple]):
    """Render a horizontal strip of stats. stats = [(value, label), ...]"""
    items_html = "".join(
        f'<div class="if-stat-item"><div class="if-stat-val">{v}</div><div class="if-stat-lbl">{l}</div></div>'
        for v, l in stats
    )
    st.markdown(f'<div class="if-stat-strip">{items_html}</div>', unsafe_allow_html=True)


def image_card(img_key: str, title: str, subtitle: str = ""):
    url = PEXELS.get(img_key, PEXELS["analytics"])
    st.markdown(f"""
<div class="if-img-card">
    <img src="{url}" alt="{title}" loading="lazy"/>
    <div class="overlay">
        <div class="overlay-title">{title}</div>
        {'<div class="overlay-sub">' + subtitle + '</div>' if subtitle else ''}
    </div>
</div>""", unsafe_allow_html=True)


def feature_card(icon: str, title: str, desc: str):
    st.markdown(f"""
<div class="if-card">
    <div class="card-icon">{icon}</div>
    <div class="card-title">{title}</div>
    <div class="card-desc">{desc}</div>
</div>""", unsafe_allow_html=True)


def section_label(text: str):
    st.markdown(f'<span class="section-label">{text}</span>', unsafe_allow_html=True)


def divider():
    st.markdown("<hr>", unsafe_allow_html=True)


def dataset_status_badge():
    if "df_clean" in st.session_state and st.session_state.df_clean is not None:
        df = st.session_state.df_clean
        st.sidebar.markdown(f"""
<div style="background:rgba(16,185,129,0.07);border:1px solid rgba(16,185,129,0.22);
     border-radius:10px;padding:0.7rem 1rem;margin:0.5rem 0;">
    <div style="font-size:0.62rem;font-weight:700;text-transform:uppercase;
         letter-spacing:0.1em;color:#10B981;margin-bottom:0.2rem;">Dataset Active</div>
    <div style="font-size:0.82rem;font-weight:600;color:#DDE8F8;">
        {df.shape[0]:,} rows &times; {df.shape[1]} cols
    </div>
</div>""", unsafe_allow_html=True)
    else:
        st.sidebar.markdown("""
<div style="background:rgba(44,63,96,0.15);border:1px solid rgba(44,63,96,0.35);
     border-radius:10px;padding:0.7rem 1rem;margin:0.5rem 0;">
    <div style="font-size:0.62rem;font-weight:700;text-transform:uppercase;
         letter-spacing:0.1em;color:#3A5070;margin-bottom:0.2rem;">No Dataset</div>
    <div style="font-size:0.78rem;color:#3A5070;">Upload a file to begin</div>
</div>""", unsafe_allow_html=True)


def render_footer():
    """Render a consistent footer on every page."""
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    st.markdown("""
<div style="border-top:1px solid #2C3F60;margin-top:2rem;padding:1.5rem 0 0.5rem;text-align:center;">
    <div style="display:flex;align-items:center;justify-content:center;gap:0.6rem;margin-bottom:0.5rem;">
        <div style="width:22px;height:22px;background:linear-gradient(135deg,#00D4FF,#7C3AED);
             border-radius:6px;display:flex;align-items:center;justify-content:center;
             font-size:0.75rem;color:#06101C;font-weight:900;">◈</div>
        <span style="font-family:'Space Grotesk',sans-serif;font-size:0.92rem;
              font-weight:700;color:#DDE8F8;">DecTell AI</span>
    </div>
    <p style="font-size:0.78rem;color:#3A5070;margin:0.2rem 0;">
        AI-Powered Business Analytics &amp; Decision Intelligence Platform
    </p>
    <p style="font-size:0.72rem;color:#2C3F60;margin:0.4rem 0 0;">
        &copy; 2026 DecTell AI &nbsp;·&nbsp; Built with research, analytics, and intelligence.
    </p>
</div>""", unsafe_allow_html=True)

