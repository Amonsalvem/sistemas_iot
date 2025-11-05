# ================= MQTT Control de Luces — UI negro/blanco =================
import json
import platform
import time
import paho.mqtt.client as paho
import streamlit as st

# -------------------- Config de página --------------------
st.set_page_config(
    page_title="Control de Luces (MQTT)",
    page_icon="💡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# -------------------- Estilos globales --------------------
st.markdown(
    """
    <style>
      :root { --bg:#0b0b0b; --fg:#f5f5f5; --muted:#cfcfcf; --chip:#151515; --chip-b:#2a2a2a; }
      html, body, [data-testid="stAppViewContainer"] { background: var(--bg) !important; color: var(--fg) !important; }
      [data-testid="stMarkdownContainer"] h1, h2, h3, h4, h5, h6 { color: var(--fg) !important; }
      .stAlert div{ color: var(--fg) !important; }
      input, textarea { background:#0f0f0f !important; color:var(--fg) !important; border:1px solid #2a2a2a !important; }
      .stNumberInput input { background:#0f0f0f !important; color:var(--fg) !important; }
      .chip {
        display:inline-flex; gap:.5rem; align-items:center; padding:.35rem .7rem;
        border:1px solid var(--chip-b); background:var(--chip); color:var(--muted);
        border-radius:999px; font-size:.85rem;
      }
      .chip b{ color:var(--fg); }
      div.stButton > button {
        width: 100% !important; border-radius: 12px; padding:.8rem 1rem;
        border:1px solid #2a2a2a; background:#111; color:#fff; font-weight:600;
      }
      div.stButton > button:hover { background:#1a1a1a; }
      .stSlider > div[data-baseweb="slider"] > div { color:var(--fg) !important; }
      .stMetric { border:1px solid #2a2a2a; border-radius:12px; padding:10px; background:#0f0f0f; }
      hr { border-top:1px solid #2a2a2a !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------- Estado --------------------
if "last_payload" not in st.session_state:
    st.session_state.last_payload = None
if "publish_status" not in st.session_state:
    st.session_state.publish_status = None

# -------------------- Sidebar (conexión) --------------------
with st.sidebar:
    st.subheader("⚙️ Conexión MQTT")
    broker = st.text_input("Broker", value="157.230.214.127")
    port = st.number_input("Puerto", value=1883, min_value=1, max_value=65535, step=1)
    client_id = st.text_input("Client ID", value="streamlit-pub")
    topic_switch = st.text_input("Tópico ON/OFF", value="cmqtt_s")
    topic_analog = st.text_input("Tópico analógico", value="cmqtt_a")

# -------------------- Cabecera --------------------
st.caption("PUBLICACIÓN MQTT")
st.markdown("## 💡 Control de Luces")

st.write(
    f"""
    <span class="chip"><b>Broker</b> {broker}</span>
    &nbsp;&nbsp;
    <span class="chip"><b>Puerto</b> {port}</span>
    &nbsp;&nbsp;
    <span class="chip"><b>Python</b> {platform.python_version()}</span>
    """,
    unsafe_allow_html=True,
)

st.divider()

# -------------------- Helper de publicación --------------------
def publish_message(broker: str, port: int, client_id: str, topic: str, payload: dict, qos: int = 0, keepalive: int = 60):
    """
    Publica un payload JSON en un tópico MQTT. Devuelve (ok: bool, detalle: str).
    """
    try:
        client = paho.Client(client_id=client_id, clean_session=True)
        client.connect(broker, port, keepalive)
        msg = json.dumps(payload)
        res = client.publish(topic, msg, qos=qos)
        # Esperar confirmación de envío (no garantía de recepción)
        res.wait_for_publish(timeout=2.0)
        client.disconnect()
        return True, f"Publicado en '{topic}': {msg}"
    except Exception as e:
        return False, f"Error publicando en '{topic}': {e}"

# -------------------- Controles principales --------------------
col1, col2 = st.columns(2)
with col1:
    if st.button("🔼 Encender (ON)"):
        ok, detail = publish_message(broker.strip(), int(port), client_id.strip(), topic_switch.strip(), {"Act1": "ON"})
        st.session_state.publish_status = (ok, detail)
with col2:
    if st.button("🔽 Apagar (OFF)"):
        ok, detail = publish_message(broker.strip(), int(port), client_id.strip(), topic_switch.strip(), {"Act1": "OFF"})
        st.session_state.publish_status = (ok, detail)

st.divider()

# Slider y envío analógico
value = st.slider("Selecciona valor analógico", 0.0, 100.0, 50.0, 1.0)
if st.button("📤 Enviar valor analógico"):
    ok, detail = publish_message(
        broker.strip(), int(port), client_id.strip(), topic_analog.strip(), {"Analog": float(value)}
    )
    st.session_state.publish_status = (ok, detail)
    st.session_state.last_payload = {"Analog": float(value)}

# -------------------- Feedback --------------------
if st.session_state.publish_status is not None:
    ok, detail = st.session_state.publish_status
    if ok:
        st.success(f"✅ {detail}")
    else:
        st.error(f"❌ {detail}")

if st.session_state.last_payload is not None:
    st.divider()
    st.subheader("📦 Último payload enviado")
    st.json(st.session_state.last_payload)
