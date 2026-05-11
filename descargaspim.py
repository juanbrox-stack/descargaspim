import streamlit as st
import requests
import pandas as pd
import time
import io
import warnings
from urllib3.exceptions import InsecureRequestWarning

warnings.filterwarnings("ignore")
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# ============================================================
# CAMPOS FIJOS A DESCARGAR — edita esta lista para cambiarlos
# ============================================================
CAMPOS_DESEADOS = [
    "nombre_producto__modelo",
    "descripcion_corta_del_producto",
    "descripcion_larga_del_producto",
    "ean_13",
    "referencia en web",
    "familia",
    "subfamilia",
    "foto_master_producto_main_image_1000x1000_png_01",
    "foto_master_producto_main_image_1000x1000_png_02",
    "foto_enriquecida_01",
    "foto_enriquecida_02",
    "foto_enriquecida_03",
    "foto_enriquecida_04",
    "foto_enriquecida_05",
    "foto_enriquecida_06",
    "foto_image_gallery_11_jpg_01",
    "foto_image_gallery_11_jpg_02",
    "foto_image_gallery_11_jpg_03",
    "bulletpoint_1",
    "bulletpoint_2",
    "bulletpoint_3",
    "bulletpoint_4",
    "bulletpoint_5",
    "bulletpoint_1_en",
    "bulletpoint_2_en",
    "bulletpoint_3_en",
    "asin",
    "estado_del_producto",
    "watts",
    "voltaje",
    "product_weight",
    "product_width",
    "product_height",
    "product_depth",
]
# ============================================================


# ── Page config ─────────────────────────────────────────────
st.set_page_config(
    page_title="Plytix Downloader",
    page_icon="⬇️",
    layout="wide",
)

# ── Custom CSS ───────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Background principal oscuro */
.stApp {
    background: #0d0d0d;
    color: #f0f0f0;
}

/* Headings */
h1, h2, h3 {
    font-family: 'Space Mono', monospace !important;
    color: #f0f0f0 !important;
}

/* Header strip */
.header-strip {
    background: linear-gradient(90deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-bottom: 2px solid #e94560;
    padding: 2rem 2.5rem 1.5rem;
    margin: -1rem -1rem 2rem -1rem;
    border-radius: 0 0 12px 12px;
}
.header-strip h1 { font-size: 2rem; letter-spacing: -1px; margin: 0; }
.header-strip p  { color: #aaa; margin: 0.3rem 0 0; font-size: 0.9rem; }

/* Accent */
.accent { color: #e94560; }

/* Stat boxes */
.stat-row { display: flex; gap: 1rem; margin: 1rem 0; }
.stat-box {
    background: #1a1a1a;
    border: 1px solid #333;
    border-radius: 8px;
    padding: 0.8rem 1.2rem;
    flex: 1;
    text-align: center;
}
.stat-box .num {
    font-family: 'Space Mono', monospace;
    font-size: 1.8rem;
    color: #e94560;
    display: block;
}
.stat-box .lbl {
    font-size: 0.75rem;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Buttons */
.stButton > button {
    background: #e94560 !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
    padding: 0.6rem 1.5rem !important;
    letter-spacing: 1px !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: #c73652 !important;
    transform: translateY(-1px) !important;
}

/* ── SIDEBAR: fondo blanco para que los inputs sean legibles ── */
section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 2px solid #e94560 !important;
}
section[data-testid="stSidebar"] * {
    color: #111111 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #111111 !important;
    font-family: 'Space Mono', monospace !important;
}
section[data-testid="stSidebar"] small {
    color: #555 !important;
}
/* Inputs dentro del sidebar */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {
    background: #f5f5f5 !important;
    color: #111 !important;
    border: 1px solid #ccc !important;
    border-radius: 6px !important;
}
section[data-testid="stSidebar"] input:focus,
section[data-testid="stSidebar"] textarea:focus {
    border-color: #e94560 !important;
    box-shadow: 0 0 0 2px rgba(233,69,96,0.15) !important;
}
/* Labels del sidebar */
section[data-testid="stSidebar"] label {
    color: #333 !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
}
/* Multiselect tags en sidebar */
section[data-testid="stSidebar"] [data-baseweb="tag"] {
    background: #e94560 !important;
    color: white !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #f5f5f5 !important;
    border-color: #ccc !important;
    color: #111 !important;
}

/* ── Inputs en zona principal ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #1a1a1a !important;
    border: 1px solid #333 !important;
    color: #f0f0f0 !important;
    border-radius: 8px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #e94560 !important;
    box-shadow: 0 0 0 2px rgba(233,69,96,0.2) !important;
}

/* File uploader */
.stFileUploader > div {
    background: #1a1a1a !important;
    border: 2px dashed #444 !important;
    border-radius: 12px !important;
}

/* Progress */
.stProgress > div > div > div { background: #e94560 !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #1a1a1a;
    border-radius: 8px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #888 !important;
    border-radius: 6px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.8rem !important;
}
.stTabs [aria-selected="true"] {
    background: #e94560 !important;
    color: white !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    color: #f0f0f0 !important;
}

/* Divider en sidebar */
section[data-testid="stSidebar"] hr {
    border-color: #ddd !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helper functions ─────────────────────────────────────────

def obtener_token(api_key, api_secret):
    try:
        r = requests.post(
            "https://auth.plytix.com/auth/api/get-token",
            json={"api_key": api_key, "api_password": api_secret},
            headers={"Content-Type": "application/json"},
            verify=False, timeout=15
        )
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict) and "data" in data:
                return data["data"][0].get("access_token"), None
            elif isinstance(data, list):
                return data[0].get("access_token"), None
        return None, f"Error {r.status_code}: {r.text}"
    except Exception as e:
        return None, str(e)


def extraer_valor(val):
    if isinstance(val, dict):
        return val.get("url", val.get("thumbnail", str(val)))
    if isinstance(val, list):
        urls = [extraer_valor(v) for v in val if v]
        return " | ".join(str(u) for u in urls if u)
    return val if val is not None else ""


def buscar_ids(skus, headers, progress_cb=None):
    todos = []
    lotes = [skus[i:i+20] for i in range(0, len(skus), 20)]
    for i, lote in enumerate(lotes):
        if progress_cb:
            progress_cb(i / len(lotes) * 0.3, f"Buscando IDs — lote {i+1}/{len(lotes)}")
        payload = {
            "filters": [[{"field": "sku", "operator": "in", "value": lote}]],
            "pagination": {"page": 1, "page_size": 100}
        }
        for intento in range(3):
            try:
                res = requests.post(
                    "https://pim.plytix.com/api/v1/products/search",
                    json=payload, headers=headers, verify=False, timeout=60
                )
                if res.status_code == 200:
                    todos.extend(res.json().get("data", []))
                    break
            except requests.exceptions.ReadTimeout:
                time.sleep(5)
        time.sleep(0.5)
    return todos


def obtener_atributos(product_id, headers):
    for _ in range(3):
        try:
            res = requests.get(
                f"https://pim.plytix.com/api/v1/products/{product_id}",
                headers=headers, verify=False, timeout=60
            )
            if res.status_code == 200:
                data = res.json().get("data", [])
                producto = data[0] if isinstance(data, list) else data
                return producto.get("attributes", {})
        except requests.exceptions.ReadTimeout:
            time.sleep(3)
    return {}


def ejecutar_descarga(skus, api_key, api_secret, progress_bar, status_text):
    # 1. Token
    status_text.markdown("🔑 Autenticando...")
    token, err = obtener_token(api_key, api_secret)
    if not token:
        return None, f"Error de autenticación: {err}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # 2. Buscar IDs
    def update_progress(pct, msg):
        progress_bar.progress(pct)
        status_text.markdown(f"🔍 {msg}")

    productos_base = buscar_ids(skus, headers, update_progress)
    if not productos_base:
        return None, "No se encontraron productos para los SKUs proporcionados."

    # 3. Descargar atributos
    resultados = []
    total = len(productos_base)
    for idx, p in enumerate(productos_base):
        pct = 0.3 + (idx / total) * 0.7
        progress_bar.progress(pct)
        status_text.markdown(f"📥 Descargando atributos — {idx+1}/{total}: `{p.get('sku', '')}`")

        attrs = obtener_atributos(p["id"], headers)
        fila = {"SKU": p.get("sku", "")}
        for campo in CAMPOS_DESEADOS:
            fila[campo] = extraer_valor(attrs.get(campo))
        resultados.append(fila)
        time.sleep(0.2)

    progress_bar.progress(1.0)
    status_text.markdown("✅ Descarga completada")
    return pd.DataFrame(resultados), None


# ── UI ────────────────────────────────────────────────────────

# Header
st.markdown("""
<div class="header-strip">
    <h1>⬇ PLYTIX <span class="accent">DOWNLOADER</span></h1>
    <p>Extracción masiva de atributos de producto desde Plytix PIM</p>
</div>
""", unsafe_allow_html=True)

# Sidebar — credenciales + selección de campos
with st.sidebar:
    st.markdown("## 🔐 Credenciales API")
    st.markdown("<small>Encuéntralas en Plytix → Admin → API</small>", unsafe_allow_html=True)
    st.markdown("")
    api_key    = st.text_input("API Key",    type="default",  placeholder="Ej: S98GV47S10GQ09TN2TPZ")
    api_secret = st.text_input("API Secret", type="password", placeholder="Tu API secret")

    if api_key and api_secret:
        st.success("✅ Credenciales introducidas")
    else:
        st.warning("⚠️ Introduce tus credenciales")

    st.markdown("---")
    st.markdown("## 📋 Campos a descargar")
    st.markdown("<small>Selecciona qué atributos quieres en el Excel final</small>", unsafe_allow_html=True)
    st.markdown("")

    campos_seleccionados = st.multiselect(
        "Campos seleccionados",
        options=TODOS_LOS_CAMPOS,
        default=CAMPOS_DESEADOS,
        help="Busca y selecciona los campos que quieres descargar"
    )

    st.markdown(f"**{len(campos_seleccionados)}** campos seleccionados")

    st.markdown("---")
    st.markdown("<small style='color:#888'>Plytix Downloader v1.0 · Cecotec</small>", unsafe_allow_html=True)

# Main — tabs
tab1, tab2 = st.tabs(["📂  SUBIR EXCEL", "✏️  ESCRIBIR SKUS"])

skus_finales = []

# Tab 1 — Excel upload
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Arrastra aquí tu Excel con SKUs",
        type=["xlsx", "xls"],
        help="El archivo debe tener una columna con 'sku' en el nombre"
    )
    if uploaded:
        try:
            df_in = pd.read_excel(uploaded)
            col_sku = next((c for c in df_in.columns if 'sku' in c.lower()), None)
            if col_sku:
                skus_from_excel = df_in[col_sku].dropna().astype(str).tolist()
                st.markdown(f"""
                <div class="stat-row">
                    <div class="stat-box"><span class="num">{len(skus_from_excel)}</span><span class="lbl">SKUs cargados</span></div>
                    <div class="stat-box"><span class="num">{len(df_in.columns)}</span><span class="lbl">Columnas en Excel</span></div>
                </div>
                """, unsafe_allow_html=True)
                with st.expander("Vista previa", expanded=False):
                    st.dataframe(df_in.head(10), use_container_width=True)
                skus_finales = skus_from_excel
            else:
                st.error("No se encontró una columna con 'sku' en el nombre.")
        except Exception as e:
            st.error(f"Error leyendo el archivo: {e}")

# Tab 2 — Manual input
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    texto_skus = st.text_area(
        "Pega los SKUs (uno por línea)",
        height=200,
        placeholder="A01_EU01_100185\nA01_EU01_100184\nA01_EU01_100183\n..."
    )
    if texto_skus.strip():
        skus_manual = [s.strip() for s in texto_skus.strip().splitlines() if s.strip()]
        st.markdown(f"<small style='color:#888'>{len(skus_manual)} SKUs detectados</small>", unsafe_allow_html=True)
        if st.button("Usar estos SKUs"):
            skus_finales = skus_manual
            st.success(f"✅ {len(skus_finales)} SKUs listos para descargar")

# ── Download section ──────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    if skus_finales:
        st.markdown(f"<small style='color:#888'>🟢 <b style='color:#e94560'>{len(skus_finales)}</b> SKUs listos · <b style='color:#e94560'>{len(CAMPOS_DESEADOS)}</b> campos · Estimado: ~{max(1, len(skus_finales) // 10)} min</small>", unsafe_allow_html=True)
    else:
        st.markdown("<small style='color:#555'>Carga SKUs en una de las pestañas de arriba</small>", unsafe_allow_html=True)

with col2:
    iniciar = st.button("▶ INICIAR DESCARGA", disabled=not skus_finales or not api_key or not api_secret)

with col3:
    if not api_key or not api_secret:
        st.markdown("<small style='color:#e94560'>⚠ Introduce las credenciales en el panel lateral</small>", unsafe_allow_html=True)

# ── Run download ──────────────────────────────────────────────
if iniciar and skus_finales:
    st.markdown("<br>", unsafe_allow_html=True)
    progress_bar = st.progress(0.0)
    status_text  = st.empty()

    df_resultado, error = ejecutar_descarga(
        skus_finales, api_key, api_secret,
        progress_bar, status_text
    )

    if error:
        st.error(f"❌ {error}")
    else:
        st.success(f"✅ {len(df_resultado)} productos descargados correctamente")

        # Stats
        campos_con_datos = sum(1 for c in df_resultado.columns if df_resultado[c].astype(str).str.strip().ne("").any())
        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-box"><span class="num">{len(df_resultado)}</span><span class="lbl">Productos</span></div>
            <div class="stat-box"><span class="num">{len(df_resultado.columns)}</span><span class="lbl">Columnas</span></div>
            <div class="stat-box"><span class="num">{campos_con_datos}</span><span class="lbl">Campos con datos</span></div>
        </div>
        """, unsafe_allow_html=True)

        # Preview
        with st.expander("Vista previa del resultado", expanded=True):
            st.dataframe(df_resultado.head(20), use_container_width=True)

        # Download button
        buffer = io.BytesIO()
        df_resultado.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)

        st.download_button(
            label="⬇ DESCARGAR EXCEL",
            data=buffer,
            file_name="reporte_plytix.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )