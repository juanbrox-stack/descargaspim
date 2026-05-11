import subprocess
import sys
subprocess.run([sys.executable, "-m", "pip", "install", "openpyxl", "xlrd", "--quiet"], check=False)

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
# CAMPOS POR DEFECTO (preseleccionados al abrir la app)
# ============================================================
CAMPOS_DESEADOS = [
    "nombre_producto__modelo",
    "descripcion_corta_del_producto",
    "descripcion_larga_del_producto",
    "ean_13", "ean_14","referencia en web",
    "familia", "subfamilia",
    "foto_master_producto_main_image_1000x1000_png_01",
    "foto_master_producto_main_image_1000x1000_png_02",
    "foto_enriquecida_01", "foto_enriquecida_02", "foto_enriquecida_03",
    "foto_enriquecida_04", "foto_enriquecida_05", "foto_enriquecida_06",
    "foto_image_gallery_11_jpg_01", "foto_image_gallery_11_jpg_02", "foto_image_gallery_11_jpg_03",
    "bulletpoint_1", "bulletpoint_2", "bulletpoint_3", "bulletpoint_4", "bulletpoint_5",
    "bulletpoint_1_en", "bulletpoint_2_en", "bulletpoint_3_en",
    "asin", "estado_del_producto", "watts", "voltaje",
    "product_weight", "product_width", "product_height", "product_depth",
]

# ============================================================
# LISTA COMPLETA DE ATRIBUTOS DISPONIBLES EN PLYTIX
# ============================================================
TODOS_LOS_CAMPOS = sorted(list(dict.fromkeys([
    "altura_cm", "altura_pallet_140_cm", "altura_pallet_170", "altura_pallet_180",
    "altura_pallet_190", "altura_pallet_200", "altura_pallet_210", "altura_pallet_240",
    "ancho_pallet_170", "ancho_pallet_180", "ancho_pallet_190", "ancho_pallet_210",
    "ancho_pallet_240", "anchura_cm", "apilabilidad", "apto_para_todo_tipo_de_gas",
    "asin", "banner_a", "banners_lanzamiento", "banners_lanzamiento_en",
    "basicos_logistica", "briefing_de_comunicacion",
    "bulletpoint_1", "bulletpoint_1_cz", "bulletpoint_1_de", "bulletpoint_1_en",
    "bulletpoint_1_fr", "bulletpoint_1_hu", "bulletpoint_1_it", "bulletpoint_1_nl",
    "bulletpoint_1_pl", "bulletpoint_1_pt",
    "bulletpoint_2", "bulletpoint_2_cz", "bulletpoint_2_de", "bulletpoint_2_en",
    "bulletpoint_2_fr", "bulletpoint_2_hu", "bulletpoint_2_it", "bulletpoint_2_nl",
    "bulletpoint_2_pl", "bulletpoint_2_pt",
    "bulletpoint_3", "bulletpoint_3_cz", "bulletpoint_3_de", "bulletpoint_3_en",
    "bulletpoint_3_fr", "bulletpoint_3_hu", "bulletpoint_3_it", "bulletpoint_3_nl",
    "bulletpoint_3_pl", "bulletpoint_3_pt",
    "bulletpoint_4", "bulletpoint_4_cz", "bulletpoint_4_de", "bulletpoint_4_en",
    "bulletpoint_4_fr", "bulletpoint_4_hu", "bulletpoint_4_it", "bulletpoint_4_nl",
    "bulletpoint_4_pl", "bulletpoint_4_pt",
    "bulletpoint_5", "bulletpoint_5_cz", "bulletpoint_5_de", "bulletpoint_5_en",
    "bulletpoint_5_fr", "bulletpoint_5_hu", "bulletpoint_5_it", "bulletpoint_5_nl",
    "bulletpoint_5_pl", "bulletpoint_5_pt", "bulletpoint_5_tr",
    "bulletpoint_6", "bulletpoint_6_cat", "bulletpoint_6_cz", "bulletpoint_6_de",
    "bulletpoint_6_en", "bulletpoint_6_fr", "bulletpoint_6_gr", "bulletpoint_6_it",
    "bulletpoint_6_nl", "bulletpoint_6_pl", "bulletpoint_6_pt", "bulletpoint_6_tr",
    "bultos_expedicion", "bultos_por_pallet_140", "bultos_por_pallet_170",
    "bultos_por_pallet_180", "bultos_por_pallet_190", "bultos_por_pallet_200",
    "bultos_por_pallet_210", "bultos_por_pallet_240",
    "capas_por_pallet_140", "capas_por_pallet_170", "capas_por_pallet_180",
    "capas_por_pallet_190", "capas_por_pallet_200", "capas_por_pallet_210", "capas_por_pallet_240",
    "caracteristicas", "caracteristicas_cz", "caracteristicas_de", "caracteristicas_en",
    "caracteristicas_fr", "caracteristicas_it", "caracteristicas_nl", "caracteristicas_pl",
    "caracteristicas_pt", "caracteristicas_tr",
    "catalogo_general", "categoria_web", "channel", "cluster_customer", "clusterizacion",
    "codigo_proveedor", "codigo_taric",
    "contenido_de_la_caja", "contenido_de_la_caja_cz", "contenido_de_la_caja_de",
    "contenido_de_la_caja_en", "contenido_de_la_caja_fr", "contenido_de_la_caja_gr",
    "contenido_de_la_caja_hu", "contenido_de_la_caja_it", "contenido_de_la_caja_nl",
    "contenido_de_la_caja_pl", "contenido_de_la_caja_pt", "contenido_de_la_caja_tr",
    "descripcion_corta_del_producto", "descripcion_corta_del_producto_de",
    "descripcion_corta_del_producto_en", "descripcion_corta_del_producto_fr",
    "descripcion_corta_del_producto_it",
    "descripcion_highlight_1", "descripcion_highlight_1_cz", "descripcion_highlight_1_de",
    "descripcion_highlight_1_en", "descripcion_highlight_1_fr", "descripcion_highlight_1_hu",
    "descripcion_highlight_1_it", "descripcion_highlight_1_nl", "descripcion_highlight_1_pl",
    "descripcion_highlight_1_pt",
    "descripcion_highlight_2", "descripcion_highlight_2_en", "descripcion_highlight_2_de",
    "descripcion_highlight_3", "descripcion_highlight_3_en",
    "descripcion_highlight_4", "descripcion_highlight_4_en",
    "descripcion_highlight_5", "descripcion_highlight_5_en",
    "descripcion_highlight_6", "descripcion_highlight_6_en",
    "descripcion_highlight_7", "descripcion_highlight_7_en",
    "descripcion_highlight_8", "descripcion_highlight_8_en",
    "descripcion_larga_del_producto", "descripcion_larga_del_producto_cz",
    "descripcion_larga_del_producto_de", "descripcion_larga_del_producto_en",
    "descripcion_larga_del_producto_fr", "descripcion_larga_del_producto_gr",
    "descripcion_larga_del_producto_hu", "descripcion_larga_del_producto_it",
    "descripcion_larga_del_producto_nl", "descripcion_larga_del_producto_pl",
    "descripcion_larga_del_producto_pt", "descripcion_larga_del_producto_tr",
    "ean_13", "ean_14", "embarcado", "en_almacen", "encendido_electronico", "estado_del_producto",
    "familia", "familia_cz", "familia_de", "familia_en", "familia_fr", "familia_gr",
    "familia_hu", "familia_it", "familia_nl", "familia_pl", "familia_pt", "familia_tr",
    "familia_padre", "familia_padre_de", "familia_padre_en", "familia_padre_fr",
    "familia_padre_gr", "familia_padre_it", "familia_padre_nl", "familia_padre_pl",
    "familia_padre_pt", "familia_padre_tr",
    "ficha_pesos_detallados",
    "foto_enriquecida_01", "foto_enriquecida_02", "foto_enriquecida_03",
    "foto_enriquecida_04", "foto_enriquecida_05", "foto_enriquecida_06",
    "foto_enriquecida_no_text",
    "foto_image_gallery_11_jpg_01", "foto_image_gallery_11_jpg_02", "foto_image_gallery_11_jpg_03",
    "foto_image_gallery_11_jpg_04", "foto_image_gallery_11_jpg_05", "foto_image_gallery_11_jpg_06",
    "foto_image_gallery_11_jpg_07",
    "foto_image_gallery_169_jpg_01", "foto_image_gallery_169_jpg_02", "foto_image_gallery_169_jpg_03",
    "foto_image_gallery_169_jpg_04", "foto_image_gallery_169_jpg_05", "foto_image_gallery_169_jpg_06",
    "foto_image_gallery_169_jpg_07",
    "foto_master_main_image_png_03", "foto_master_main_image_png_04",
    "foto_master_main_image_png_05", "foto_master_main_image_png_06",
    "foto_master_producto_main_image_1000x1000_png_01",
    "foto_master_producto_main_image_1000x1000_png_02",
    "foto_video_placeholder_1920x1080_jpg",
    "highlight_corto_producto_1", "highlight_corto_producto_2", "highlight_corto_producto_3",
    "highlight_corto_producto_4", "highlight_corto_producto_5", "highlight_corto_producto_6",
    "highlight_largo_1", "highlight_largo_1_de", "highlight_largo_1_en", "highlight_largo_1_fr",
    "highlight_largo_1_gr", "highlight_largo_1_hu", "highlight_largo_1_it",
    "highlight_largo_1_nl", "highlight_largo_1_pl", "highlight_largo_1_pt", "highlight_largo_1_tr",
    "highlight_largo_2", "highlight_largo_2_en", "highlight_largo_3", "highlight_largo_3_en",
    "highlight_largo_4", "highlight_largo_4_en", "highlight_largo_5", "highlight_largo_5_en",
    "highlight_largo_6", "highlight_largo_6_en",
    "highlights_cortos_agrupacion_01", "highlights_cortos_agrupacion_02",
    "highlights_cortos_agrupacion_03", "highlights_cortos_agrupacion_04",
    "highlights_cortos_agrupacion_05", "highlights_cortos_agrupacion_06",
    "highlights_cortos_agrupacion_es",
    "iconografia_colorbox", "iconografia_masterbox",
    "iconografia_pie_de_aspiracion", "iconografia_rating_label",
    "manual_de_instrucciones_arte_final", "manual_de_instrucciones_comercial",
    "masterbox_height", "masterbox_length", "masterbox_per_layer",
    "masterbox_per_pallet_storage", "masterbox_width",
    "material_de_la_superficie",
    "medidas_alto_encastre_cm", "medidas_ancho_encastre_cm", "medidas_largo_encastre_cm",
    "nombre_producto__modelo", "nombre_producto__modelo_cz", "nombre_producto__modelo_de",
    "nombre_producto__modelo_en", "nombre_producto__modelo_fr", "nombre_producto__modelo_gr",
    "nombre_producto__modelo_hu", "nombre_producto__modelo_it", "nombre_producto__modelo_nl",
    "nombre_producto__modelo_pl", "nombre_producto__modelo_pt", "nombre_producto__modelo_tr",
    "nombre_upc",
    "pallet_height_storage", "pallet_length_storage", "pallet_volume_storage",
    "pallet_weight_storage", "pallet_width_storage",
    "peso_caja_color_kg", "peso_caja_master_kg", "peso_facturable_internacional",
    "peso_facturable_nacional", "peso_producto_y_accesorios_principales",
    "plazo_garantia", "potencia_calorifica_kw",
    "product_depth", "product_height", "product_weight", "product_width", "profundidad_cm",
    "propietario", "propiedad_intelectual", "range_version","referencia en web", "rating_label_del_producto_text",
    "sistema", "soporte_para_wok",
    "subfamilia", "subfamilia_cz", "subfamilia_de", "subfamilia_en", "subfamilia_fr",
    "subfamilia_gr", "subfamilia_hu", "subfamilia_it", "subfamilia_nl", "subfamilia_pl",
    "subfamilia_pt", "subfamilia_tr",
    "tipologia_de_producto", "tipologia_de_producto_en",
    "titulo_highlight_1", "titulo_highlight_1_cz", "titulo_highlight_1_de",
    "titulo_highlight_1_en", "titulo_highlight_1_fr", "titulo_highlight_1_hu",
    "titulo_highlight_1_it", "titulo_highlight_1_nl", "titulo_highlight_1_pl", "titulo_highlight_1_pt",
    "titulo_highlight_2", "titulo_highlight_2_en",
    "titulo_highlight_3", "titulo_highlight_3_en",
    "titulo_highlight_4", "titulo_highlight_4_en",
    "titulo_highlight_5", "titulo_highlight_5_en",
    "titulo_highlight_6", "titulo_highlight_6_en",
    "titulo_highlight_7", "titulo_highlight_7_en",
    "titulo_highlight_8", "titulo_highlight_8_en",
    "unidades_por_pallet_140", "unidades_por_pallet_170", "unidades_por_pallet_180",
    "unidades_por_pallet_190", "unidades_por_pallet_200", "unidades_por_pallet_210",
    "unidades_por_pallet_240", "units_per_masterbox", "units_per_pallet",
    "videos_lanzamiento", "voltaje", "watts", "zonas_de_coccion",
])))


# ── Page config ──────────────────────────────────────────────
st.set_page_config(page_title="Plytix Downloader", page_icon="⬇️", layout="wide")

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0d0d0d; color: #f0f0f0; }
h1, h2, h3 { font-family: 'Space Mono', monospace !important; color: #f0f0f0 !important; }

.header-strip {
    background: linear-gradient(90deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    border-bottom: 2px solid #e94560;
    padding: 2rem 2.5rem 1.5rem;
    margin: -1rem -1rem 2rem -1rem;
    border-radius: 0 0 12px 12px;
}
.header-strip h1 { font-size: 2rem; letter-spacing: -1px; margin: 0; color: #f0f0f0; }
.header-strip p { color: #aaa; margin: 0.3rem 0 0; font-size: 0.9rem; }
.accent { color: #e94560; }

.stat-row { display: flex; gap: 1rem; margin: 1rem 0; }
.stat-box {
    background: #1a1a1a; border: 1px solid #333; border-radius: 8px;
    padding: 0.8rem 1.2rem; flex: 1; text-align: center;
}
.stat-box .num { font-family: 'Space Mono', monospace; font-size: 1.8rem; color: #e94560; display: block; }
.stat-box .lbl { font-size: 0.75rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }

.stButton > button {
    background: #e94560 !important; color: white !important; border: none !important;
    border-radius: 8px !important; font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important; padding: 0.6rem 1.5rem !important;
    letter-spacing: 1px !important; transition: all 0.2s !important;
}
.stButton > button:hover { background: #c73652 !important; transform: translateY(-1px) !important; }

/* SIDEBAR — fondo blanco para que inputs sean legibles */
section[data-testid="stSidebar"] {
    background: #f8f9fa !important;
    border-right: 2px solid #e94560 !important;
}
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] small,
section[data-testid="stSidebar"] div { color: #222 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #111 !important; font-family: 'Space Mono', monospace !important;
}
section[data-testid="stSidebar"] input {
    background: #ffffff !important; color: #111 !important;
    border: 1.5px solid #ccc !important; border-radius: 6px !important;
}
section[data-testid="stSidebar"] input:focus {
    border-color: #e94560 !important; box-shadow: 0 0 0 2px rgba(233,69,96,0.2) !important;
}
section[data-testid="stSidebar"] [data-baseweb="tag"] {
    background-color: #e94560 !important; color: white !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: #ffffff !important; border-color: #ccc !important; color: #111 !important;
}
section[data-testid="stSidebar"] [data-baseweb="menu"] {
    background: #ffffff !important; color: #111 !important;
}
section[data-testid="stSidebar"] hr { border-color: #ddd !important; }
section[data-testid="stSidebar"] .stAlert { background: #fff3cd !important; color: #333 !important; }
section[data-testid="stSidebar"] .stSuccess { background: #d4edda !important; color: #155724 !important; }

/* Main inputs */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #1a1a1a !important; border: 1px solid #333 !important;
    color: #f0f0f0 !important; border-radius: 8px !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #e94560 !important; box-shadow: 0 0 0 2px rgba(233,69,96,0.2) !important;
}

.stFileUploader > div {
    background: #1a1a1a !important; border: 2px dashed #444 !important; border-radius: 12px !important;
}
.stProgress > div > div > div { background: #e94560 !important; }

.stTabs [data-baseweb="tab-list"] { background: #1a1a1a; border-radius: 8px; padding: 4px; gap: 4px; }
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: #888 !important;
    border-radius: 6px !important; font-family: 'Space Mono', monospace !important; font-size: 0.8rem !important;
}
.stTabs [aria-selected="true"] { background: #e94560 !important; color: white !important; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ──────────────────────────────────────────────────

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
        return " | ".join(extraer_valor(v) for v in val if v)
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
        for _ in range(3):
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


def ejecutar_descarga(skus, api_key, api_secret, campos, progress_bar, status_text):
    status_text.markdown("🔑 Autenticando...")
    token, err = obtener_token(api_key, api_secret)
    if not token:
        return None, f"Error de autenticación: {err}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    productos_base = buscar_ids(
        skus, headers,
        lambda pct, msg: (progress_bar.progress(pct), status_text.markdown(f"🔍 {msg}"))
    )
    if not productos_base:
        return None, "No se encontraron productos para los SKUs proporcionados."

    resultados = []
    total = len(productos_base)
    for idx, p in enumerate(productos_base):
        progress_bar.progress(0.3 + (idx / total) * 0.7)
        status_text.markdown(f"📥 Descargando {idx+1}/{total}: `{p.get('sku', '')}`")
        attrs = obtener_atributos(p["id"], headers)
        fila = {"SKU": p.get("sku", "")}
        for campo in campos:
            fila[campo] = extraer_valor(attrs.get(campo))
        resultados.append(fila)
        time.sleep(0.2)

    progress_bar.progress(1.0)
    status_text.markdown("✅ Descarga completada")
    return pd.DataFrame(resultados), None


# ── UI ────────────────────────────────────────────────────────

st.markdown("""
<div class="header-strip">
    <h1>⬇ PLYTIX <span class="accent">DOWNLOADER</span></h1>
    <p>Extracción masiva de atributos de producto desde Plytix PIM</p>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔐 Credenciales API")
    st.caption("Plytix → Admin → API → Tu usuario")

    api_key    = st.text_input("API Key",    type="default",  placeholder="Ej: S98GV47S10GQ09TN2TPZ")
    api_secret = st.text_input("API Secret", type="password", placeholder="Tu API secret")

    if api_key and api_secret:
        st.success("✅ Credenciales listas")
    else:
        st.warning("Introduce tus credenciales para continuar")

    st.markdown("---")
    st.markdown("## 📋 Campos a descargar")
    st.caption(f"{len(TODOS_LOS_CAMPOS)} atributos disponibles — escribe para filtrar")

    campos_seleccionados = st.multiselect(
        label="Selecciona campos",
        options=TODOS_LOS_CAMPOS,
        default=[c for c in CAMPOS_DESEADOS if c in TODOS_LOS_CAMPOS],
        help="Escribe para buscar. Los campos marcados se incluirán en el Excel."
    )

    if campos_seleccionados:
        st.info(f"**{len(campos_seleccionados)}** campos seleccionados")
    else:
        st.warning("Selecciona al menos un campo")

    st.markdown("---")
    st.caption("Plytix Downloader v1.1 · Cecotec Internal Tool")


# ── TABS ─────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📂  SUBIR EXCEL", "✏️  ESCRIBIR SKUS"])

skus_finales = []

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

with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    texto_skus = st.text_area(
        "Pega los SKUs (uno por línea)",
        height=200,
        placeholder="A01_EU01_100185\nA01_EU01_100184\nA01_EU01_100183\n..."
    )
    if texto_skus.strip():
        skus_manual = [s.strip() for s in texto_skus.strip().splitlines() if s.strip()]
        st.caption(f"{len(skus_manual)} SKUs detectados")
        if st.button("Usar estos SKUs"):
            skus_finales = skus_manual
            st.success(f"✅ {len(skus_finales)} SKUs listos")

# ── DESCARGA ─────────────────────────────────────────────────
st.markdown("---")
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    if skus_finales:
        est = max(1, len(skus_finales) // 10)
        st.markdown(f"🟢 **{len(skus_finales)}** SKUs · **{len(campos_seleccionados)}** campos · ~{est} min estimado")
    else:
        st.caption("Carga SKUs en una de las pestañas de arriba")

with col2:
    can_run = bool(skus_finales) and bool(api_key) and bool(api_secret) and bool(campos_seleccionados)
    iniciar = st.button("▶ INICIAR DESCARGA", disabled=not can_run)

with col3:
    if not api_key or not api_secret:
        st.warning("⚠ Introduce credenciales")
    elif not campos_seleccionados:
        st.warning("⚠ Selecciona campos")

if iniciar and skus_finales:
    progress_bar = st.progress(0.0)
    status_text  = st.empty()

    df_resultado, error = ejecutar_descarga(
        skus_finales, api_key, api_secret,
        campos_seleccionados, progress_bar, status_text
    )

    if error:
        st.error(f"❌ {error}")
    else:
        st.success(f"✅ {len(df_resultado)} productos descargados correctamente")

        campos_con_datos = sum(
            1 for c in df_resultado.columns
            if df_resultado[c].astype(str).str.strip().ne("").any()
        )
        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-box"><span class="num">{len(df_resultado)}</span><span class="lbl">Productos</span></div>
            <div class="stat-box"><span class="num">{len(df_resultado.columns)}</span><span class="lbl">Columnas</span></div>
            <div class="stat-box"><span class="num">{campos_con_datos}</span><span class="lbl">Campos con datos</span></div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Vista previa del resultado", expanded=True):
            st.dataframe(df_resultado.head(20), use_container_width=True)

        buffer = io.BytesIO()
        df_resultado.to_excel(buffer, index=False, engine="openpyxl")
        buffer.seek(0)

        st.download_button(
            label="⬇ DESCARGAR EXCEL",
            data=buffer,
            file_name="reporte_plytix.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )