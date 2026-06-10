import streamlit as st
import requests
import pandas as pd
import time
import io
import zipfile
from html import escape
import warnings
from urllib3.exceptions import InsecureRequestWarning

warnings.filterwarnings("ignore")
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# ============================================================
# FUENTE DE DATOS
# ============================================================
# MODO_PIM    → campos del PIM directos (snake_case, ej: foto_enriquecida_01)
# MODO_ECATALOG → campos del ecatalog/channel (con espacios, ej: "1000x1000 JPG (Marketplace) 01")
#                 incluye URLs JPG ya convertidas correctamente por Plytix

ECATALOG_ID = "6531422065345fbf54877ad5"

# ============================================================
# CAMPOS ECATALOG — nombres exactos del channel
# ============================================================
CAMPOS_ECATALOG_DEFECTO = [
    "Reference",
    "Product / Model Name",
    "1000x1000 JPG (Marketplace) 01",
    "1000x1000 JPG (Marketplace) 02",
  "1000x1000 JPG (Marketplace) 03","1000x1000 JPG (Marketplace) 04","1000x1000 JPG (Marketplace) 05",
    "Enhanced Photo 01",
    "Enhanced Photo 02",
    "Enhanced Photo 03",
    "Enhanced Photo 04",
    "Enhanced Photo 05",
    "Foto Image Gallery 1:1 JPG 01",
    "Foto Image Gallery 1:1 JPG 02",
    "Foto Image Gallery 1:1 JPG 03",
    "Foto Image Gallery 1:1 JPG 04",
    "Foto Image Gallery 1:1 JPG 05","Enhanced Photo INT",
    "Enhanced Photo TEXT ESP"
    
]

TODOS_CAMPOS_ECATALOG = sorted([
    "1000x1000 JPG (Marketplace) 01", "1000x1000 JPG (Marketplace) 02",
    "1000x1000 JPG (Marketplace) 03", "1000x1000 JPG (Marketplace) 04",
    "1000x1000 JPG (Marketplace) 05", "1000x1000 JPG (Marketplace) 06",
    "1000x1000 JPG (Marketplace) 07", "1000x1000 JPG (Marketplace) 08",
    "1000x1000 PNG (Web) 01", "1000x1000 PNG (Web) 02",
    "1000x1000 PNG (Web) 03", "1000x1000 PNG (Web) 04",
    "1000x1500 JPG 01", "1000x1500 JPG 02", "1000x1500 JPG 03", "1000x1500 JPG 04",
    "1000x1500 PNG 01", "1000x1500 PNG 02",
    "2000x2000 JPG 01", "2000x2000 JPG 02", "2000x2000 JPG 03", "2000x2000 JPG 04",
    "2000x2000 JPG 05", "2000x2000 JPG 06", "2000x2000 JPG 07", "2000x2000 JPG 08",
    "2000x2000 PNG 01", "2000x2000 PNG 02",
    "2000x3000 JPG 01", "2000x3000 JPG 02",
    "2000x3000 PNG 01", "2000x3000 PNG 02",
    "250x250 JPG 01", "250x250 JPG 02",
    "250x250 PNG 01", "250x250 PNG 02",
    "450x450 JPG 01", "450x450 JPG 02",
    "450x450 PNG 01", "450x450 PNG 02",
    "488x700 JPG A+P Comparativa 01", "488x700 JPG A+P Comparativa 02",
    "488x700 PNG A+P Comparativa 01", "488x700 PNG A+P Comparativa 02",
    "600x450 JPG A+P Comparativa 01", "600x450 JPG A+P Comparativa 02",
    "600x450 PNG A+P Comparativa 01", "600x450 PNG A+P Comparativa 02",
    "650x650 JPG 01", "650x650 JPG 02",
    "650x650 PNG 01", "650x650 PNG 02",
    "Banner A+",
    "Banners RRSS ESP",
    "Banners Social Media INT",
    "Enhanced Photo 01", "Enhanced Photo 02", "Enhanced Photo 03", "Enhanced Photo 04",
    "Enhanced Photo 05", "Enhanced Photo 06", "Enhanced Photo 07", "Enhanced Photo 08",
    "Enhanced Photo 09", "Enhanced Photo 10", "Enhanced Photo 11", "Enhanced Photo 12",
    "Enhanced Photo 2000x2000 JPG 01", "Enhanced Photo 2000x2000 JPG 02",
    "Enhanced Photo 2000x2000 JPG 03", "Enhanced Photo 2000x2000 JPG 04",
    "Enhanced Photo 2000x2000 JPG 05", "Enhanced Photo 2000x2000 JPG 06",
    "Enhanced Photo 2000x2000 JPG 07", "Enhanced Photo 2000x2000 JPG 08",
    "Enhanced Photo ENG 01", "Enhanced Photo ENG 02", "Enhanced Photo ENG 03",
    "Enhanced Photo ENG 04", "Enhanced Photo ENG 05", "Enhanced Photo ENG 06",
    "Enhanced Photo INT",
    "Enhanced Photo TEXT ESP", "Enhanced Photo TEXT ESP 2000x2000",
    "Foto Image Gallery 16:9 JPG 01", "Foto Image Gallery 16:9 JPG 02",
    "Foto Image Gallery 16:9 JPG 03", "Foto Image Gallery 16:9 JPG 04",
    "Foto Image Gallery 16:9 JPG 05", "Foto Image Gallery 16:9 JPG 06",
    "Foto Image Gallery 16:9 JPG 07", "Foto Image Gallery 16:9 JPG 08",
    "Foto Image Gallery 1:1 JPG 01", "Foto Image Gallery 1:1 JPG 02",
    "Foto Image Gallery 1:1 JPG 03", "Foto Image Gallery 1:1 JPG 04",
    "Foto Image Gallery 1:1 JPG 05", "Foto Image Gallery 1:1 JPG 06",
    "Foto Image Gallery 1:1 JPG 07", "Foto Image Gallery 1:1 JPG 08",
    "HQ JPG 01", "HQ JPG 02", "HQ JPG 03", "HQ JPG 04",
    "HQ PNG 01", "HQ PNG 02", "HQ PNG 03", "HQ PNG 04",
    "Image Gallery 16:9 JPG",
    "Image Highlight Banner 16:9 2400x1258 JPG",
    "Instruction manual",
    "Language Launch Videos",
    "Launch Videos",
    "Product / Model Name",
    "Reference",
    "Technical Data Sheet (Product Data)",
])

# ============================================================
# CAMPOS PIM (snake_case, API directa)
# ============================================================
CAMPOS_PIM_DEFECTO = [
    "nombre_producto__modelo",
    "descripcion_corta_del_producto",
    "descripcion_larga_del_producto",
    "ean_13", "ean_14",
    "familia", "subfamilia",
    "foto_master_producto_main_image_1000x1000_png_01",
    "foto_master_producto_main_image_1000x1000_png_02",
    "foto_enriquecida_01", "foto_enriquecida_02", "foto_enriquecida_03",
    "foto_enriquecida_04", "foto_enriquecida_05", "foto_enriquecida_06",
    "foto_image_gallery_11_jpg_01", "foto_image_gallery_11_jpg_02",
    "bulletpoint_1", "bulletpoint_2", "bulletpoint_3", "bulletpoint_4", "bulletpoint_5",
    "bulletpoint_1_en", "bulletpoint_2_en", "bulletpoint_3_en",
    "asin", "estado_del_producto", "watts", "voltaje",
    "product_weight", "product_width", "product_height", "product_depth",
    "referencia_en_web",
]

TODOS_CAMPOS_PIM = sorted(list(dict.fromkeys([
    "altura_cm", "anchura_cm", "apilabilidad", "apto_para_todo_tipo_de_gas", "asin",
    "banner_a", "banners_lanzamiento", "banners_lanzamiento_en", "basicos_logistica",
    "briefing_de_comunicacion",
    "bulletpoint_1", "bulletpoint_1_cz", "bulletpoint_1_de", "bulletpoint_1_en",
    "bulletpoint_1_fr", "bulletpoint_1_hu", "bulletpoint_1_it", "bulletpoint_1_nl",
    "bulletpoint_1_pl", "bulletpoint_1_pt",
    "bulletpoint_2", "bulletpoint_2_cz", "bulletpoint_2_de", "bulletpoint_2_en",
    "bulletpoint_2_fr", "bulletpoint_2_hu", "bulletpoint_2_it", "bulletpoint_2_nl",
    "bulletpoint_2_pl", "bulletpoint_2_pt",
    "bulletpoint_3", "bulletpoint_3_cz", "bulletpoint_3_de", "bulletpoint_3_en",
    "bulletpoint_3_fr", "bulletpoint_3_it", "bulletpoint_3_nl", "bulletpoint_3_pl", "bulletpoint_3_pt",
    "bulletpoint_4", "bulletpoint_4_de", "bulletpoint_4_en", "bulletpoint_4_fr",
    "bulletpoint_4_it", "bulletpoint_4_nl", "bulletpoint_4_pl", "bulletpoint_4_pt",
    "bulletpoint_5", "bulletpoint_5_de", "bulletpoint_5_en", "bulletpoint_5_fr",
    "bulletpoint_5_it", "bulletpoint_5_nl", "bulletpoint_5_pl", "bulletpoint_5_pt", "bulletpoint_5_tr",
    "bulletpoint_6", "bulletpoint_6_cat", "bulletpoint_6_de", "bulletpoint_6_en",
    "bulletpoint_6_fr", "bulletpoint_6_it", "bulletpoint_6_nl", "bulletpoint_6_pl", "bulletpoint_6_pt",
    "caracteristicas", "caracteristicas_de", "caracteristicas_en", "caracteristicas_fr",
    "caracteristicas_it", "caracteristicas_nl", "caracteristicas_pl", "caracteristicas_pt",
    "catalogo_general", "categoria_web", "channel", "cluster_customer", "clusterizacion",
    "codigo_proveedor", "codigo_taric",
    "contenido_de_la_caja", "contenido_de_la_caja_de", "contenido_de_la_caja_en",
    "contenido_de_la_caja_fr", "contenido_de_la_caja_it", "contenido_de_la_caja_nl",
    "contenido_de_la_caja_pl", "contenido_de_la_caja_pt",
    "descripcion_corta_del_producto", "descripcion_corta_del_producto_de",
    "descripcion_corta_del_producto_en", "descripcion_corta_del_producto_fr",
    "descripcion_corta_del_producto_it",
    "descripcion_highlight_1", "descripcion_highlight_1_de", "descripcion_highlight_1_en",
    "descripcion_highlight_1_fr", "descripcion_highlight_1_it",
    "descripcion_highlight_2", "descripcion_highlight_2_en",
    "descripcion_highlight_3", "descripcion_highlight_3_en",
    "descripcion_highlight_4", "descripcion_highlight_4_en",
    "descripcion_highlight_5", "descripcion_highlight_5_en",
    "descripcion_highlight_6", "descripcion_highlight_6_en",
    "descripcion_highlight_7", "descripcion_highlight_7_en",
    "descripcion_highlight_8", "descripcion_highlight_8_en",
    "descripcion_larga_del_producto", "descripcion_larga_del_producto_de",
    "descripcion_larga_del_producto_en", "descripcion_larga_del_producto_fr",
    "descripcion_larga_del_producto_it", "descripcion_larga_del_producto_nl",
    "descripcion_larga_del_producto_pl", "descripcion_larga_del_producto_pt",
    "ean_13", "ean_14", "embarcado", "en_almacen", "encendido_electronico", "estado_del_producto",
    "familia", "familia_de", "familia_en", "familia_fr", "familia_it", "familia_nl",
    "familia_pl", "familia_pt", "familia_padre", "familia_padre_en",
    "foto_enriquecida_01", "foto_enriquecida_02", "foto_enriquecida_03",
    "foto_enriquecida_04", "foto_enriquecida_05", "foto_enriquecida_06",
    "foto_enriquecida_no_text",
    "foto_image_gallery_11_jpg_01", "foto_image_gallery_11_jpg_02",
    "foto_image_gallery_11_jpg_03", "foto_image_gallery_11_jpg_04",
    "foto_image_gallery_11_jpg_05", "foto_image_gallery_11_jpg_06",
    "foto_image_gallery_169_jpg_01", "foto_image_gallery_169_jpg_02",
    "foto_image_gallery_169_jpg_03", "foto_image_gallery_169_jpg_04",
    "foto_master_main_image_png_03", "foto_master_main_image_png_04",
    "foto_master_producto_main_image_1000x1000_png_01",
    "foto_master_producto_main_image_1000x1000_png_02",
    "highlight_corto_producto_1", "highlight_corto_producto_2", "highlight_corto_producto_3",
    "highlight_corto_producto_4", "highlight_corto_producto_5", "highlight_corto_producto_6",
    "highlight_largo_1", "highlight_largo_1_de", "highlight_largo_1_en", "highlight_largo_1_fr",
    "highlight_largo_2", "highlight_largo_2_en", "highlight_largo_3", "highlight_largo_3_en",
    "highlight_largo_4", "highlight_largo_4_en", "highlight_largo_5", "highlight_largo_5_en",
    "highlight_largo_6", "highlight_largo_6_en",
    "highlights_cortos_agrupacion_es",
    "manual_de_instrucciones_arte_final", "manual_de_instrucciones_comercial",
    "masterbox_height", "masterbox_length", "masterbox_width",
    "material_de_la_superficie",
    "medidas_alto_encastre_cm", "medidas_ancho_encastre_cm", "medidas_largo_encastre_cm",
    "nombre_producto__modelo", "nombre_producto__modelo_de", "nombre_producto__modelo_en",
    "nombre_producto__modelo_fr", "nombre_producto__modelo_it", "nombre_upc",
    "pallet_height_storage", "pallet_weight_storage",
    "peso_caja_color_kg", "peso_caja_master_kg", "peso_facturable_internacional",
    "peso_facturable_nacional", "peso_producto_y_accesorios_principales",
    "plazo_garantia", "potencia_calorifica_kw",
    "product_depth", "product_height", "product_weight", "product_width", "profundidad_cm",
    "propietario", "range_version", "referencia_en_web",
    "sistema", "soporte_para_wok",
    "subfamilia", "subfamilia_de", "subfamilia_en", "subfamilia_fr", "subfamilia_it",
    "subfamilia_nl", "subfamilia_pl", "subfamilia_pt",
    "tipologia_de_producto", "tipologia_de_producto_en",
    "titulo_highlight_1", "titulo_highlight_1_de", "titulo_highlight_1_en",
    "titulo_highlight_2", "titulo_highlight_2_en",
    "titulo_highlight_3", "titulo_highlight_3_en",
    "titulo_highlight_4", "titulo_highlight_4_en",
    "titulo_highlight_5", "titulo_highlight_5_en",
    "titulo_highlight_6", "titulo_highlight_6_en",
    "titulo_highlight_7", "titulo_highlight_7_en",
    "titulo_highlight_8", "titulo_highlight_8_en",
    "units_per_masterbox", "units_per_pallet",
    "videos_lanzamiento", "voltaje", "watts", "zonas_de_coccion",
])))



# ── Generador HTML Cdiscount ──────────────────────────────────

# Campos imagen hero (modo PIM y ecatalog respectivamente)
_HERO_PIM      = "foto_master_producto_main_image_1000x1000_png_01"
_HERO_ECATALOG = "1000x1000 JPG (Marketplace) 01"
_ENHANCED_PIM      = ["foto_enriquecida_0" + str(n) for n in range(1, 7)]
_ENHANCED_ECATALOG = ["Enhanced Photo 0" + str(n) for n in range(1, 7)]
_NOMBRE_PIM      = "nombre_producto__modelo"
_NOMBRE_ECATALOG = "Product / Model Name"
_DESC_PIM        = "descripcion_corta_del_producto"
_DESC_FR_ECATALOG = "Enhanced Photo TEXT ESP"   # fallback; usa desc_corta si no existe

# Specs que se muestran en el HTML cuando el campo está en el df
_SPECS_ETIQUETAS = {
    "EAN": ["ean_13", "Reference"],
    "Famille": ["familia", "familia_fr"],
    "Sous-famille": ["subfamilia", "subfamilia_fr"],
    "Watts": ["watts"],
    "Peso (kg)": ["product_weight"],
}


def _primera_url(valor):
    """Devuelve la primera URL de un campo (puede ser 'url1 | url2 | ...')."""
    if not valor:
        return ""
    return str(valor).split(" | ")[0].strip()


def _generar_html_fila(fila: dict, modo: str) -> str:
    """Genera HTML enriquecido Cdiscount para una fila del DataFrame."""
    sku    = escape(str(fila.get("SKU", "")))
    nombre = escape(str(fila.get(_NOMBRE_ECATALOG if modo == "ecatalog" else _NOMBRE_PIM, "") or sku))
    desc   = escape(str(fila.get(_DESC_PIM, "") or ""))

    # Imagen hero
    campo_hero = _HERO_ECATALOG if modo == "ecatalog" else _HERO_PIM
    img_hero = _primera_url(fila.get(campo_hero, ""))

    hero_img_tag = (
        f'<img src="{img_hero}" alt="{nombre}" loading="lazy" />'
        if img_hero else
        '<div class="cd-img-placeholder">Sin imagen</div>'
    )

    # Fotos enriquecidas
    campos_enhanced = _ENHANCED_ECATALOG if modo == "ecatalog" else _ENHANCED_PIM
    fotos = [_primera_url(fila.get(c, "")) for c in campos_enhanced]
    fotos = [u for u in fotos if u]

    feature_cards = "".join(
        f'<div class="cd-feature-card"><img src="{u}" alt="{nombre}" loading="lazy" /></div>'
        for u in fotos
    )
    features_section = f"""
  <section class="cd-features">
    <h4 class="cd-section-title">Détails du produit</h4>
    <div class="cd-feature-grid">{feature_cards}</div>
  </section>""" if feature_cards else ""

    # Especificaciones técnicas
    spec_items = ""
    for etiqueta, campos_posibles in _SPECS_ETIQUETAS.items():
        for campo in campos_posibles:
            val = fila.get(campo, "")
            if val:
                spec_items += f'<li><span class="spec-label">{escape(etiqueta)}</span><span class="spec-value">{escape(str(val))}</span></li>'
                break

    specs_section = f"""
  <section class="cd-specs">
    <h4 class="cd-section-title">Caractéristiques</h4>
    <ul class="cd-spec-list">{spec_items}</ul>
  </section>""" if spec_items else ""

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{nombre}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:Arial,sans-serif;color:#222;background:#fff;max-width:960px;margin:auto;padding:28px 16px}}
.cd-hero{{display:flex;gap:36px;align-items:flex-start;margin-bottom:44px;flex-wrap:wrap}}
.cd-hero img{{width:360px;max-width:100%;border-radius:8px;object-fit:contain;border:1px solid #e8e8e8;background:#fafafa}}
.cd-img-placeholder{{width:360px;height:260px;background:#f0f0f0;display:flex;align-items:center;justify-content:center;color:#aaa;border-radius:8px;font-size:.85rem}}
.cd-hero-content{{flex:1;min-width:220px}}
.cd-hero-content h2{{font-size:1.45rem;font-weight:700;margin-bottom:10px;color:#111;line-height:1.3}}
.cd-sku{{font-size:.78rem;color:#999;margin-bottom:14px;letter-spacing:.03em}}
.cd-hero-content p{{font-size:.95rem;line-height:1.65;color:#444}}
.cd-section-title{{font-size:.85rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#e84e0f;margin-bottom:20px;padding-bottom:8px;border-bottom:2px solid #e84e0f}}
.cd-features{{margin-bottom:44px}}
.cd-feature-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:16px}}
.cd-feature-card{{border-radius:8px;overflow:hidden;border:1px solid #eee;background:#fafafa}}
.cd-feature-card img{{width:100%;aspect-ratio:1/1;object-fit:contain;display:block;padding:8px}}
.cd-specs{{margin-bottom:40px}}
.cd-spec-list{{list-style:none}}
.cd-spec-list li{{display:flex;justify-content:space-between;padding:9px 14px;font-size:.88rem;gap:16px;border-bottom:1px solid #f0f0f0}}
.cd-spec-list li:nth-child(odd){{background:#f9f9f9}}
.spec-label{{color:#555}}
.spec-value{{font-weight:600;color:#111;text-align:right}}
</style>
</head>
<body>
  <section class="cd-hero">
    {hero_img_tag}
    <div class="cd-hero-content">
      <p class="cd-sku">SKU: {sku}</p>
      <h2>{nombre}</h2>
      <p>{desc}</p>
    </div>
  </section>
{features_section}
{specs_section}
</body>
</html>"""


def generar_zip_html(df: pd.DataFrame, modo: str) -> bytes:
    """Devuelve un ZIP en memoria con un HTML por fila del DataFrame."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for _, fila in df.iterrows():
            sku = str(fila.get("SKU", "sin_sku")).strip().replace("/", "_").replace(" ", "_")
            html = _generar_html_fila(fila.to_dict(), modo)
            zf.writestr(f"{sku}.html", html.encode("utf-8"))
    buf.seek(0)
    return buf.getvalue()


# ── Page config ──────────────────────────────────────────────
st.set_page_config(page_title="Plytix Downloader · Cecotec", page_icon="⬇️", layout="wide")

if "skus_finales" not in st.session_state:
    st.session_state.skus_finales = []
if "campos" not in st.session_state:
    st.session_state.campos = CAMPOS_ECATALOG_DEFECTO[:]
if "modo" not in st.session_state:
    st.session_state.modo = "ecatalog"

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background: #0a0a0a; color: #ffffff; }
.stApp { background: #0a0a0a; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 3rem !important; max-width: 1400px !important; }
.turaco-header h1 { font-size: 2.2rem; font-weight: 800; color: #ffffff; margin: 0 0 0.8rem 0; }
.turaco-banner { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 8px; padding: 0.85rem 1.2rem; font-size: 0.9rem; color: #cccccc; margin-bottom: 1.2rem; }
.turaco-banner b { color: #ffffff; }
.card-white { background: #f5f5f5; border-radius: 14px; padding: 1.8rem 1.5rem 1.4rem; text-align: center; border: 1px solid #e0e0e0; min-height: 160px; }
.card-white .card-icon { font-size: 2.2rem; margin-bottom: 0.7rem; }
.card-white .card-title { font-size: 1rem; font-weight: 700; color: #111; margin-bottom: 0.4rem; }
.card-white .card-desc { font-size: 0.8rem; color: #666; line-height: 1.4; }
.section-dark { background: #111111; border: 1px solid #222; border-radius: 14px; padding: 1.5rem 1.8rem; margin-bottom: 1.2rem; }
.section-dark h3 { color: #ffffff !important; font-size: 1rem; font-weight: 700; margin: 0 0 1rem 0; }
.stat-row { display: flex; gap: 1rem; margin: 1rem 0; }
.stat-box { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 10px; padding: 1rem 1.2rem; flex: 1; text-align: center; }
.stat-box .num { font-size: 2rem; font-weight: 800; color: #22d3c5; display: block; line-height: 1; }
.stat-box .lbl { font-size: 0.72rem; color: #888; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 0.3rem; display: block; }
.badge-ecatalog { background: #22d3c5; color: #000; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
.badge-pim { background: #6366f1; color: #fff; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
.stButton > button { background: #22d3c5 !important; color: #000000 !important; border: none !important; border-radius: 8px !important; font-weight: 700 !important; font-size: 0.85rem !important; padding: 0.55rem 1.4rem !important; transition: all 0.2s !important; width: 100% !important; }
.stButton > button:hover { background: #1ab5a8 !important; transform: translateY(-1px) !important; box-shadow: 0 4px 15px rgba(34,211,197,0.3) !important; }
.stButton > button:disabled { background: #333 !important; color: #666 !important; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea { background: #1a1a1a !important; border: 1.5px solid #333 !important; color: #ffffff !important; border-radius: 8px !important; font-size: 0.9rem !important; }
.stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus { border-color: #22d3c5 !important; box-shadow: 0 0 0 2px rgba(34,211,197,0.2) !important; }
label { color: #aaaaaa !important; font-size: 0.82rem !important; font-weight: 600 !important; }
[data-testid="stFileUploader"] { background: #111 !important; border: 2px dashed #333 !important; border-radius: 12px !important; }
[data-baseweb="select"] > div { background: #1a1a1a !important; border-color: #333 !important; color: #fff !important; }
[data-baseweb="select"] input { background: transparent !important; color: #ffffff !important; caret-color: #22d3c5 !important; }
[data-baseweb="tag"] {
    background: #22d3c5 !important;
    color: #000 !important;
    font-weight: 600 !important;
    max-width: none !important;
    white-space: nowrap !important;
    overflow: visible !important;
}
[data-baseweb="tag"] span[data-baseweb="tag-text"] {
    overflow: visible !important;
    text-overflow: unset !important;
    white-space: nowrap !important;
    max-width: none !important;
    font-size: 0.78rem !important;
}
[data-baseweb="menu"] { background: #1a1a1a !important; border: 1px solid #333 !important; }
[data-baseweb="menu"] li { color: #ffffff !important; }
[data-baseweb="menu"] li:hover { background: #2a2a2a !important; color: #22d3c5 !important; }
.stTabs [data-baseweb="tab-list"] { background: #111; border-radius: 10px; padding: 4px; gap: 4px; border: 1px solid #222; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #888 !important; border-radius: 7px !important; font-weight: 600 !important; font-size: 0.85rem !important; }
.stTabs [aria-selected="true"] { background: #22d3c5 !important; color: #000 !important; }
.stProgress > div > div > div { background: #22d3c5 !important; }
.stRadio > div { gap: 1rem !important; }
hr { border-color: #222 !important; margin: 1.5rem 0 !important; }
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
    """Extrae URL o valor de un campo. Para listas devuelve URLs separadas por |"""
    if val is None:
        return ""
    if isinstance(val, dict):
        return val.get("url", val.get("original_url", str(val)))
    if isinstance(val, list):
        urls = []
        for v in val:
            if isinstance(v, dict):
                urls.append(v.get("url", v.get("original_url", "")))
            elif v:
                urls.append(str(v))
        return " | ".join(u for u in urls if u)
    return str(val) if val else ""


# ── MODO ECATALOG ─────────────────────────────────────────────

def buscar_producto_ecatalog(sku_o_ref, token):
    """Busca un producto en el ecatalog por referencia/SKU."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    # Primero buscar el product_id en PIM
    payload = {
        "filters": [[{"field": "sku", "operator": "eq", "value": sku_o_ref}]],
        "pagination": {"page": 1, "page_size": 1}
    }
    r = requests.post(
        "https://pim.plytix.com/api/v1/products/search",
        json=payload, headers=headers, verify=False, timeout=30
    )
    if r.status_code != 200:
        return None
    data = r.json().get("data", [])
    if not data:
        return None
    product_id = data[0]["id"]

    # Luego obtener datos del ecatalog
    r2 = requests.get(
        f"https://pim.plytix.com/api/v1/public/e-catalogs/{ECATALOG_ID}/products/{product_id}",
        headers=headers, verify=False, timeout=30
    )
    if r2.status_code == 200:
        result = r2.json().get("data", [])
        if result and isinstance(result, list):
            return result[0].get("attributes", {})
        elif isinstance(result, dict):
            return result.get("attributes", {})
    return None


def ejecutar_descarga_ecatalog(skus, api_key, api_secret, campos, progress_bar, status_text):
    status_text.markdown("🔑 Autenticando...")
    token, err = obtener_token(api_key, api_secret)
    if not token:
        return None, f"Error de autenticación: {err}"

    resultados = []
    total = len(skus)
    for idx, sku in enumerate(skus):
        progress_bar.progress(0.1 + (idx / total) * 0.9)
        status_text.markdown(f"📥 Descargando {idx+1}/{total}: `{sku}`")
        attrs = buscar_producto_ecatalog(sku, token)
        fila = {"SKU": sku}
        if attrs:
            for campo in campos:
                fila[campo] = extraer_valor(attrs.get(campo))
        else:
            for campo in campos:
                fila[campo] = ""
        resultados.append(fila)
        time.sleep(0.3)

    progress_bar.progress(1.0)
    status_text.markdown("✅ Descarga completada")
    return pd.DataFrame(resultados), None


# ── MODO PIM ──────────────────────────────────────────────────

def buscar_ids_pim(skus, headers, progress_cb=None):
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


def obtener_atributos_pim(product_id, headers):
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


def ejecutar_descarga_pim(skus, api_key, api_secret, campos, progress_bar, status_text):
    status_text.markdown("🔑 Autenticando...")
    token, err = obtener_token(api_key, api_secret)
    if not token:
        return None, f"Error de autenticación: {err}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    productos_base = buscar_ids_pim(
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
        attrs = obtener_atributos_pim(p["id"], headers)
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
<div class="turaco-header">
    <h1>⬇️ Plytix Downloader</h1>
    <div class="turaco-banner">
        Descarga masiva de atributos desde <b>Plytix PIM</b> o desde el <b>Ecatalog/Channel</b>
        (incluye URLs JPG ya convertidas en los tamaños correctos).
    </div>
</div>
""", unsafe_allow_html=True)

# Cards resumen
c1, c2, c3, c4 = st.columns(4)
for col, icon, title, desc in [
    (c1, "🔐", "Credenciales API", "Introduce tu API Key y Secret de Plytix"),
    (c2, "🗄️", "Fuente de datos", "Elige entre PIM directo o Ecatalog/Channel con JPGs"),
    (c3, "📂", "Carga tus SKUs", "Sube un Excel o pega los SKUs manualmente"),
    (c4, "⬇️", "Descarga Excel", "Obtén el reporte con todos los atributos seleccionados"),
]:
    with col:
        st.markdown(f"""
        <div class="card-white">
            <div class="card-icon">{icon}</div>
            <div class="card-title">{title}</div>
            <div class="card-desc">{desc}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── PASO 1: CREDENCIALES ──────────────────────────────────────
col_izq, col_der = st.columns(2, gap="large")

with col_izq:
    st.markdown('<div class="section-dark"><h3>🔐 Paso 1 — Credenciales API</h3>', unsafe_allow_html=True)
    api_key    = st.text_input("API Key",    type="default",  placeholder="Ej: S98GV47S10GQ09TN2TPZ", key="apikey")
    api_secret = st.text_input("API Secret", type="password", placeholder="Tu API secret", key="apisecret")
    if api_key and api_secret:
        st.success("✅ Credenciales introducidas")
    else:
        st.warning("⚠️ Plytix → Admin → API → Tu usuario")
    st.markdown('</div>', unsafe_allow_html=True)

# ── PASO 2: FUENTE + CAMPOS ───────────────────────────────────
with col_der:
    st.markdown('<div class="section-dark"><h3>🗄️ Paso 2 — Fuente de datos y campos</h3>', unsafe_allow_html=True)

    modo = st.radio(
        "Fuente de datos:",
        options=["ecatalog", "pim"],
        format_func=lambda x: "📦 Ecatalog/Channel — JPGs convertidos (recomendado)" if x == "ecatalog" else "🗃️ PIM directo — todos los atributos",
        horizontal=True,
        key="modo"
    )

    todos_campos = TODOS_CAMPOS_ECATALOG if modo == "ecatalog" else TODOS_CAMPOS_PIM
    defecto_campos = CAMPOS_ECATALOG_DEFECTO if modo == "ecatalog" else CAMPOS_PIM_DEFECTO

    if "ultimo_modo" not in st.session_state or st.session_state.ultimo_modo != modo:
        st.session_state.campos = defecto_campos[:]
        st.session_state.ultimo_modo = modo

    col_all, col_none, col_default = st.columns(3)
    with col_all:
        if st.button("☑️ Seleccionar todos", key="btn_sel_todos", use_container_width=True):
            st.session_state.campos = todos_campos[:]
            st.rerun()
    with col_none:
        if st.button("🗑️ Limpiar todos", key="btn_limpiar_todos", use_container_width=True):
            st.session_state.campos = []
            st.rerun()
    with col_default:
        if st.button("↩️ Restaurar defecto", key="btn_restaurar_defecto", use_container_width=True):
            st.session_state.campos = defecto_campos[:]
            st.rerun()

    campos_seleccionados = st.multiselect(
        label=f"Campos a descargar ({len(todos_campos)} disponibles):",
        options=todos_campos,
        default=st.session_state.campos,
        help="Escribe para filtrar. Selecciona varios antes de cerrar el desplegable.",
        key="campos"
    )

    if campos_seleccionados:
        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-box"><span class="num">{len(campos_seleccionados)}</span><span class="lbl">Seleccionados</span></div>
            <div class="stat-box"><span class="num">{len(todos_campos)}</span><span class="lbl">Disponibles</span></div>
        </div>""", unsafe_allow_html=True)
    else:
        st.warning("⚠️ Selecciona al menos un campo")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── PASO 3: SKUS ─────────────────────────────────────────────
st.markdown('<div class="section-dark"><h3>📂 Paso 3 — Carga tus SKUs</h3>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📂  Subir Excel", "✏️  Escribir SKUs"])

with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Arrastra aquí tu Excel con SKUs",
        type=["xlsx", "xls", "csv"],
        help="Columna con 'sku' en el nombre"
    )
    if uploaded:
        try:
            if uploaded.name.endswith(".csv"):
                df_in = pd.read_csv(uploaded)
            else:
                df_in = pd.read_excel(uploaded)
            col_sku = next((c for c in df_in.columns if "sku" in c.lower()), None)
            if col_sku is None:
                st.error("❌ No se encontró columna con 'sku'.")
            else:
                skus_excel = [s.strip() for s in df_in[col_sku].dropna().astype(str).tolist() if s.strip()]
                st.markdown(f"""
                <div class="stat-row">
                    <div class="stat-box"><span class="num">{len(skus_excel)}</span><span class="lbl">SKUs cargados</span></div>
                    <div class="stat-box"><span class="num">{len(df_in.columns)}</span><span class="lbl">Columnas</span></div>
                </div>""", unsafe_allow_html=True)
                with st.expander("👁 Vista previa", expanded=False):
                    st.write(skus_excel[:15])
                st.session_state.skus_finales = skus_excel
                st.success(f"✅ {len(skus_excel)} SKUs listos")
        except Exception as e:
            st.error(f"❌ Error: {e}")

with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    texto_skus = st.text_area(
        "Pega los SKUs, uno por línea",
        height=180,
        placeholder="A01_EU01_100185\nA01_EU01_100184\n..."
    )
    if texto_skus.strip():
        skus_manual = [s.strip() for s in texto_skus.strip().splitlines() if s.strip()]
        st.caption(f"{len(skus_manual)} SKUs detectados")
        if st.button("✓ Usar estos SKUs"):
            st.session_state.skus_finales = skus_manual
            st.rerun()
    if st.session_state.skus_finales:
        st.success(f"✅ {len(st.session_state.skus_finales)} SKUs en memoria")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ── PASO 4: DESCARGA ─────────────────────────────────────────
st.markdown('<div class="section-dark"><h3>⬇️ Paso 4 — Iniciar descarga</h3>', unsafe_allow_html=True)

col_info, col_btn = st.columns([3, 1], gap="large")

with col_info:
    if st.session_state.skus_finales and campos_seleccionados:
        est = max(1, len(st.session_state.skus_finales) // 10)
        fuente_label = "Ecatalog/Channel" if modo == "ecatalog" else "PIM directo"
        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-box"><span class="num">{len(st.session_state.skus_finales)}</span><span class="lbl">SKUs</span></div>
            <div class="stat-box"><span class="num">{len(campos_seleccionados)}</span><span class="lbl">Campos</span></div>
            <div class="stat-box"><span class="num">~{est}m</span><span class="lbl">Estimado</span></div>
        </div>""", unsafe_allow_html=True)
        st.caption(f"Fuente: **{fuente_label}**")
    else:
        st.info("ℹ️ Completa los pasos anteriores para habilitar la descarga")

with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    can_run = bool(st.session_state.skus_finales) and bool(api_key) and bool(api_secret) and bool(campos_seleccionados)
    iniciar = st.button("⬇️ INICIAR DESCARGA", disabled=not can_run)

st.markdown('</div>', unsafe_allow_html=True)

# ── EJECUCIÓN ─────────────────────────────────────────────────
if iniciar and st.session_state.skus_finales:
    progress_bar = st.progress(0.0)
    status_text  = st.empty()

    if modo == "ecatalog":
        df_resultado, error = ejecutar_descarga_ecatalog(
            st.session_state.skus_finales, api_key, api_secret,
            campos_seleccionados, progress_bar, status_text
        )
    else:
        df_resultado, error = ejecutar_descarga_pim(
            st.session_state.skus_finales, api_key, api_secret,
            campos_seleccionados, progress_bar, status_text
        )

    if error:
        st.error(f"❌ {error}")
    else:
        st.success(f"✅ {len(df_resultado)} productos descargados")

        campos_con_datos = sum(1 for c in df_resultado.columns if df_resultado[c].astype(str).str.strip().ne("").any())
        st.markdown(f"""
        <div class="stat-row">
            <div class="stat-box"><span class="num">{len(df_resultado)}</span><span class="lbl">Productos</span></div>
            <div class="stat-box"><span class="num">{len(df_resultado.columns)}</span><span class="lbl">Columnas</span></div>
            <div class="stat-box"><span class="num">{campos_con_datos}</span><span class="lbl">Con datos</span></div>
        </div>""", unsafe_allow_html=True)

        with st.expander("👁 Vista previa", expanded=True):
            st.dataframe(df_resultado.head(20), use_container_width=True)

        buffer_xlsx = io.BytesIO()
        with pd.ExcelWriter(buffer_xlsx, engine="xlsxwriter") as writer:
            df_resultado.to_excel(writer, index=False, sheet_name="Plytix")
        buffer_xlsx.seek(0)

        st.download_button(
            label="⬇️ DESCARGAR XLSX",
            data=buffer_xlsx,
            file_name="reporte_plytix.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        # ── Botón ZIP HTMLs Cdiscount ─────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        st.markdown("#### 🌐 Generar HTMLs para Cdiscount")
        st.caption("Un archivo `.html` por SKU, con Hero · Fotos enriquecidas · Specs técnicas.")

        if st.button("⚡ Generar ZIP de HTMLs", key="btn_html"):
            with st.spinner("Generando HTMLs..."):
                st.session_state["zip_html_bytes"] = generar_zip_html(df_resultado, modo)
                st.session_state["zip_html_count"] = len(df_resultado)

        if st.session_state.get("zip_html_bytes"):
            st.success(f"✅ {st.session_state['zip_html_count']} HTMLs listos")
            st.download_button(
                label="⬇️ DESCARGAR ZIP (HTMLs Cdiscount)",
                data=st.session_state["zip_html_bytes"],
                file_name="html_cdiscount.zip",
                mime="application/zip",
                key="dl_html_zip"
            )
