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


def _primera_url(valor):
    if not valor:
        return ""
    return str(valor).split(" | ")[0].strip()


def _es_url(valor):
    s = str(valor or "").strip()
    return s.startswith("http://") or s.startswith("https://")


CSS_HTML = """
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Arial,sans-serif;color:#333;background:#fff;max-width:960px;margin:auto;padding:32px 16px}
img{max-width:100%;display:block;object-fit:contain}
.cd-hero{display:flex;gap:40px;align-items:center;margin-bottom:48px;flex-wrap:wrap}
.cd-hero img{width:420px;background:#f8f8f8;border:1px solid #eee;padding:8px;border-radius:6px}
.cd-nophoto{width:420px;height:300px;background:#f0f0f0;display:flex;align-items:center;justify-content:center;color:#bbb;font-size:.85rem;border-radius:6px}
.cd-hero-text{flex:1;min-width:220px}
.cd-sku{font-size:.72rem;color:#aaa;letter-spacing:.05em;margin-bottom:10px}
.cd-hero-text h2{font-size:1.4rem;font-weight:700;line-height:1.3;color:#111;margin-bottom:12px}
.cd-hero-text p{font-size:.95rem;line-height:1.7;color:#555}
.cd-row{display:flex;gap:36px;align-items:center;margin-bottom:40px;flex-wrap:wrap}
.cd-row-rev{flex-direction:row-reverse}
.cd-row img{width:45%;min-width:200px;flex-shrink:0;background:#f8f8f8;border:1px solid #eee;padding:8px;border-radius:6px}
.cd-text{flex:1;min-width:200px}
.cd-text p{font-size:.95rem;line-height:1.75;color:#444}
.cd-full{margin-bottom:36px}
.cd-full img{width:100%;background:#f8f8f8;border:1px solid #eee;padding:8px;border-radius:6px;margin-bottom:10px}
.cd-caption{font-size:.9rem;color:#555;line-height:1.6}
.cd-divider{border:none;border-top:1px solid #eee;margin:8px 0 36px}
"""


def _generar_html_fila(fila: dict, layout: list) -> str:
    """
    Genera HTML para Cdiscount según un layout configurable.
    layout: lista de dicts con {tipo, campos:{...}}
    tipos: hero | text-photo | photo-text | photo-full
    """
    sku = escape(str(fila.get("SKU", "")))

    def val(campo):
        if not campo:
            return ""
        v = str(fila.get(campo, "") or "").strip()
        return v

    def val_resuelto(campo, fijo=""):
        """Devuelve fijo si existe, si no el valor del campo del df."""
        if fijo and fijo.strip():
            return fijo.strip()
        return val(campo)

    def url_resuelta(campo, url_fija=""):
        """Para imágenes: url_fija tiene prioridad, luego campo del df."""
        if url_fija and url_fija.strip().startswith("http"):
            return url_fija.strip()
        return _primera_url(val(campo))

    def img_tag(campo, url_fija="", alt="", css=""):
        u = url_resuelta(campo, url_fija)
        if not u:
            return f'<div class="cd-nophoto">Sin imagen</div>'
        return f'<img src="{u}" alt="{escape(alt)}" loading="lazy" {'class="'+css+'"' if css else ""}/> '

    bloques = []
    for bloque in layout:
        tipo   = bloque.get("tipo", "")
        campos = bloque.get("campos", {})

        if tipo == "hero":
            img   = img_tag(campos.get("img",""), campos.get("img",""), sku)
            nom   = escape(val_resuelto(campos.get("nombre",""), campos.get("nombre_fijo",""))) or sku
            desc  = escape(val_resuelto(campos.get("desc",""), campos.get("desc_fijo","")))
            bloques.append(f'''<section class="cd-hero">
  {img}
  <div class="cd-hero-text">
    <h2>{nom}</h2>
    <p>{desc}</p>
  </div>
</section>''')

        elif tipo == "text-photo":
            txt  = escape(val_resuelto(campos.get("texto",""), campos.get("texto_fijo","")))
            img  = img_tag(campos.get("img",""), campos.get("img_fija",""), sku)
            bloques.append(f'''<div class="cd-row">
  <div class="cd-text"><p>{txt}</p></div>
  {img}
</div>''')

        elif tipo == "photo-text":
            img  = img_tag(campos.get("img",""), campos.get("img_fija",""), sku)
            txt  = escape(val_resuelto(campos.get("texto",""), campos.get("texto_fijo","")))
            bloques.append(f'''<div class="cd-row cd-row-rev">
  {img}
  <div class="cd-text"><p>{txt}</p></div>
</div>''')

        elif tipo == "photo-full":
            img   = img_tag(campos.get("img",""), campos.get("img_fija",""), sku)
            extra = escape(val_resuelto(campos.get("extra",""), campos.get("extra_fijo","")))
            cap   = f'<p class="cd-caption">{extra}</p>' if extra else ""
            bloques.append(f'''<div class="cd-full">
  {img}
  {cap}
</div>''')

    cuerpo = '\n<hr class="cd-divider"/>\n'.join(bloques)
    nombre_titulo = escape(val(layout[0].get("campos",{}).get("nombre",""))) if layout else sku

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{nombre_titulo or sku}</title>
<style>{CSS_HTML}</style>
</head>
<body>
{cuerpo}
</body>
</html>"""


def generar_zip_html(df: pd.DataFrame, layout: list) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for _, fila in df.iterrows():
            sku  = str(fila.get("SKU","sin_sku")).strip().replace("/","_").replace(" ","_")
            html = _generar_html_fila(fila.to_dict(), layout)
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

# Colores corporativos Cecotec
CC_TURQUESA = "#3EB1C8"
CC_NEGRO    = "#141413"
CC_FONDO    = "#FAF9F5"

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background: #141413; color: #FAF9F5; }
.stApp { background: #141413; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 3rem !important; max-width: 1400px !important; }

/* Header y banner */
.turaco-header h1 { font-size: 2.2rem; font-weight: 800; color: #FAF9F5; margin: 0 0 0.8rem 0; }
.turaco-banner { background: #1e1e1c; border: 1px solid #2e2e2c; border-radius: 8px; padding: 0.85rem 1.2rem; font-size: 0.9rem; color: #b0b0a8; margin-bottom: 1.2rem; }
.turaco-banner b { color: #FAF9F5; }

/* Cards resumen */
.card-white { background: #FAF9F5; border-radius: 14px; padding: 1.8rem 1.5rem 1.4rem; text-align: center; border: 1px solid #ddddd5; min-height: 160px; }
.card-white .card-icon { font-size: 2.2rem; margin-bottom: 0.7rem; }
.card-white .card-title { font-size: 1rem; font-weight: 700; color: #141413; margin-bottom: 0.4rem; }
.card-white .card-desc { font-size: 0.8rem; color: #555; line-height: 1.4; }

/* Secciones */
.section-dark { background: #1e1e1c; border: 1px solid #2e2e2c; border-radius: 14px; padding: 1.5rem 1.8rem; margin-bottom: 1.2rem; }
.section-dark h3 { color: #FAF9F5 !important; font-size: 1rem; font-weight: 700; margin: 0 0 1rem 0; }

/* Stats */
.stat-row { display: flex; gap: 1rem; margin: 1rem 0; }
.stat-box { background: #1e1e1c; border: 1px solid #2e2e2c; border-radius: 10px; padding: 1rem 1.2rem; flex: 1; text-align: center; }
.stat-box .num { font-size: 2rem; font-weight: 800; color: #3EB1C8; display: block; line-height: 1; }
.stat-box .lbl { font-size: 0.72rem; color: #888; text-transform: uppercase; letter-spacing: 1.5px; margin-top: 0.3rem; display: block; }

/* Badges */
.badge-ecatalog { background: #3EB1C8; color: #141413; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }
.badge-pim { background: #6366f1; color: #fff; padding: 2px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; }

/* Botones */
.stButton > button { background: #3EB1C8 !important; color: #141413 !important; border: none !important; border-radius: 8px !important; font-weight: 700 !important; font-size: 0.85rem !important; padding: 0.55rem 1.4rem !important; transition: all 0.2s !important; width: 100% !important; }
.stButton > button:hover { background: #2d9db3 !important; transform: translateY(-1px) !important; box-shadow: 0 4px 15px rgba(62,177,200,0.35) !important; }
.stButton > button:disabled { background: #2e2e2c !important; color: #666 !important; }

/* Inputs */
.stTextInput > div > div > input, .stTextArea > div > div > textarea { background: #1e1e1c !important; border: 1.5px solid #3a3a38 !important; color: #FAF9F5 !important; border-radius: 8px !important; font-size: 0.9rem !important; }
.stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus { border-color: #3EB1C8 !important; box-shadow: 0 0 0 2px rgba(62,177,200,0.25) !important; }

/* Labels globales */
label { color: #c0c0b8 !important; font-size: 0.82rem !important; font-weight: 600 !important; }

/* File uploader */
[data-testid="stFileUploader"] { background: #1e1e1c !important; border: 2px dashed #3a3a38 !important; border-radius: 12px !important; }

/* Select */
[data-baseweb="select"] > div { background: #1e1e1c !important; border-color: #3a3a38 !important; color: #FAF9F5 !important; }
[data-baseweb="select"] input { background: transparent !important; color: #FAF9F5 !important; caret-color: #3EB1C8 !important; }
[data-baseweb="tag"] { background: #3EB1C8 !important; color: #141413 !important; font-weight: 600 !important; max-width: none !important; white-space: nowrap !important; overflow: visible !important; }
[data-baseweb="tag"] span[data-baseweb="tag-text"] { overflow: visible !important; text-overflow: unset !important; white-space: nowrap !important; max-width: none !important; font-size: 0.78rem !important; }
[data-baseweb="menu"] { background: #1e1e1c !important; border: 1px solid #3a3a38 !important; }
[data-baseweb="menu"] li { color: #FAF9F5 !important; }
[data-baseweb="menu"] li:hover { background: #2e2e2c !important; color: #3EB1C8 !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { background: #1e1e1c; border-radius: 10px; padding: 4px; gap: 4px; border: 1px solid #2e2e2c; }
.stTabs [data-baseweb="tab"] { background: transparent !important; color: #888 !important; border-radius: 7px !important; font-weight: 600 !important; font-size: 0.85rem !important; }
.stTabs [aria-selected="true"] { background: #3EB1C8 !important; color: #141413 !important; }

/* Progress, radio, hr */
.stProgress > div > div > div { background: #3EB1C8 !important; }
.stRadio > div { gap: 1rem !important; }
.stRadio label { color: #FAF9F5 !important; font-size: 0.82rem !important; }
hr { border-color: #2e2e2c !important; margin: 1.5rem 0 !important; }

/* ── Editor de bloques HTML ──────────────────────────────── */
/* Clase .bloque-editor aplicada con st.markdown envolvente */
.bloque-editor { background: #FAF9F5; border-radius: 12px; padding: 16px 20px; margin-bottom: 12px; border: 1.5px solid #d0d0c8; }
.bloque-editor-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; border-bottom: 1px solid #d0d0c8; padding-bottom: 10px; }
.bloque-editor-titulo { font-size: 0.9rem; font-weight: 700; color: #141413; }
.bloque-editor-badge { background: #3EB1C8; color: #141413; font-size: 0.72rem; font-weight: 700; padding: 2px 10px; border-radius: 20px; }
.campo-preview-img { display: inline-block; margin-top: 6px; }
.campo-preview-txt { font-size: 0.8rem; color: #444; margin-top: 5px; background: #eeeee6; border-radius: 6px; padding: 5px 8px; font-style: italic; border-left: 3px solid #3EB1C8; }
.campo-preview-vacio { font-size: 0.78rem; color: #999; margin-top: 5px; font-style: italic; }
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
        # Guardar en session_state para que persista tras cualquier rerender
        buffer_xlsx = io.BytesIO()
        with pd.ExcelWriter(buffer_xlsx, engine="xlsxwriter") as writer:
            df_resultado.to_excel(writer, index=False, sheet_name="Plytix")
        buffer_xlsx.seek(0)
        st.session_state["df_resultado"]   = df_resultado
        st.session_state["xlsx_bytes"]     = buffer_xlsx.getvalue()
        st.session_state["resultado_modo"] = modo
        st.session_state.pop("zip_html_bytes", None)   # limpiar ZIP anterior si había

# ── RESULTADOS (fuera del if iniciar, persiste en session_state) ──
if st.session_state.get("df_resultado") is not None:
    df_resultado = st.session_state["df_resultado"]

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

    st.download_button(
        label="⬇️ DESCARGAR XLSX",
        data=st.session_state["xlsx_bytes"],
        file_name="reporte_plytix.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="dl_xlsx"
    )

    # ── Editor visual de layout HTML Cdiscount ───────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### 🌐 Generador HTML Cdiscount")

    cols_disponibles = [c for c in df_resultado.columns if c != "SKU"]
    # Campos de imagen del banco (ecatalog tiene JPGs directos)
    cols_imagen = [c for c in cols_disponibles if any(k in c.lower() for k in
        ["jpg","png","photo","foto","image","img","banner","enhanced","gallery","1000x","2000x","hq"])]
    cols_texto  = [c for c in cols_disponibles if c not in cols_imagen]
    # Primer producto como muestra para preview
    muestra = df_resultado.iloc[0].to_dict() if len(df_resultado) > 0 else {}

    # Inicializar bloques en session_state
    if "html_bloques" not in st.session_state:
        st.session_state["html_bloques"] = []

    TIPOS_BLOQUE = {
        "hero":       "Hero (foto + nombre + descripción)",
        "text-photo": "Texto izq · Foto dcha",
        "photo-text": "Foto izq · Texto dcha",
        "photo-full": "Foto ancho completo + campo texto",
    }

    # Barra de añadir bloques
    col_btns = st.columns(4)
    for i, (tipo, label) in enumerate(TIPOS_BLOQUE.items()):
        with col_btns[i]:
            if st.button(f"＋ {label}", key=f"add_{tipo}", use_container_width=True):
                st.session_state["html_bloques"].append({"tipo": tipo, "campos": {}})
                st.session_state.pop("zip_html_bytes", None)
                st.rerun()

    if not st.session_state["html_bloques"]:
        st.info("Añade bloques desde los botones de arriba para construir la estructura del HTML.")
    else:
        bloques = st.session_state["html_bloques"]
        to_delete = None
        to_move   = None

        for idx, bloque in enumerate(bloques):
            tipo   = bloque["tipo"]
            campos = bloque.setdefault("campos", {})

            with st.container(border=True):
                # Cabecera del bloque
                hcol1, hcol2, hcol3, hcol4 = st.columns([3, 1, 1, 1])
                with hcol1:
                    badge_color = {"hero":"#3EB1C8","text-photo":"#5bbf3e","photo-text":"#e8a020","photo-full":"#a05ce8"}.get(tipo,"#3EB1C8")
                    st.markdown(
                        f'<p style="font-size:.9rem;font-weight:700;color:#FAF9F5;margin:0">' +
                        f'<span style="background:{badge_color};color:#141413;padding:2px 10px;border-radius:20px;font-size:.75rem;font-weight:700;margin-right:8px">{tipo}</span>' +
                        f'Bloque {idx+1} — {TIPOS_BLOQUE[tipo]}</p>',
                        unsafe_allow_html=True)
                with hcol2:
                    if idx > 0 and st.button("↑", key=f"up_{idx}", use_container_width=True):
                        to_move = (idx, idx-1)
                with hcol3:
                    if idx < len(bloques)-1 and st.button("↓", key=f"dn_{idx}", use_container_width=True):
                        to_move = (idx, idx+1)
                with hcol4:
                    if st.button("🗑", key=f"del_{idx}", use_container_width=True):
                        to_delete = idx

                # Campos según tipo — cada campo tiene 3 modos
                def _prev_html(texto, es_imagen=False, url=""):
                    """Renderiza preview con colores explícitos — no hereda tema oscuro."""
                    if es_imagen and url and _es_url(url):
                        return  # se usa st.image aparte
                    if texto:
                        t = str(texto)[:140].replace("<","&lt;").replace(">","&gt;")
                        st.markdown(f'<div class="campo-preview-txt">↳ {t}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<div class="campo-preview-vacio">↳ sin datos en la muestra</div>', unsafe_allow_html=True)

                def campo_selector(clave, label, es_imagen, idx=idx, campos=campos):
                    clave_fija = "img_fija" if clave == "img" else f"{clave}_fijo"
                    modo_key   = f"modo_{idx}_{clave}"
                    if modo_key not in st.session_state:
                        st.session_state[modo_key] = "campo"

                    modo_opts   = ["campo", "fijo", "banco"] if es_imagen else ["campo", "fijo"]
                    modo_labels = {"campo": "📋 Campo PIM/Ecatalog", "fijo": "✏️ Texto/URL fijo", "banco": "🖼 Banco de imágenes"}

                    st.markdown(f'<p style="font-size:0.82rem;font-weight:700;color:#141413;margin-bottom:4px">{label}</p>', unsafe_allow_html=True)
                    modo = st.radio("",
                        options=modo_opts,
                        format_func=lambda x: modo_labels[x],
                        index=modo_opts.index(st.session_state[modo_key]),
                        key=f"radio_{idx}_{clave}",
                        horizontal=True,
                        label_visibility="collapsed")
                    st.session_state[modo_key] = modo

                    if modo == "campo":
                        opc = ["(ninguno)"] + (cols_imagen if es_imagen else cols_disponibles)
                        val_actual = campos.get(clave, "(ninguno)")
                        if val_actual not in opc:
                            val_actual = "(ninguno)"
                        sel = st.selectbox("", opc,
                            index=opc.index(val_actual),
                            key=f"sel_{idx}_{clave}",
                            label_visibility="collapsed")
                        campos[clave]      = sel
                        campos[clave_fija] = ""
                        val_real = muestra.get(sel, "") if sel != "(ninguno)" else ""
                        url_real = _primera_url(str(val_real)) if val_real else ""
                        if es_imagen and url_real and _es_url(url_real):
                            st.image(url_real, width=160)
                        else:
                            _prev_html(val_real)

                    elif modo == "banco":
                        opc_banco = ["(ninguno)"] + cols_imagen
                        val_actual = campos.get(clave, "(ninguno)")
                        if val_actual not in opc_banco:
                            val_actual = "(ninguno)"
                        sel = st.selectbox("", opc_banco,
                            index=opc_banco.index(val_actual),
                            key=f"banco_{idx}_{clave}",
                            label_visibility="collapsed")
                        campos[clave]      = sel
                        campos[clave_fija] = ""
                        val_real = muestra.get(sel, "") if sel != "(ninguno)" else ""
                        url_real = _primera_url(str(val_real)) if val_real else ""
                        if url_real and _es_url(url_real):
                            st.image(url_real, width=160)
                        else:
                            _prev_html(val_real, es_imagen=True)

                    else:  # fijo
                        placeholder = "https://cdn.cecotec.com/img.jpg" if es_imagen else "Escribe el texto fijo..."
                        fijo_actual = campos.get(clave_fija, "")
                        fijo = st.text_area("", value=fijo_actual,
                            placeholder=placeholder,
                            height=72,
                            key=f"fijo_{idx}_{clave}",
                            label_visibility="collapsed")
                        campos[clave_fija] = fijo
                        campos[clave]      = ""
                        url_fija = fijo.strip().split()[0] if fijo.strip() else ""
                        if es_imagen and _es_url(url_fija):
                            st.image(url_fija, width=160)
                        elif fijo:
                            _prev_html(fijo)

                if tipo == "hero":
                    c1, c2, c3 = st.columns(3)
                    with c1: campo_selector("img",    "Imagen hero",    True)
                    with c2: campo_selector("nombre", "Nombre producto", False)
                    with c3: campo_selector("desc",   "Descripción",    False)

                elif tipo == "text-photo":
                    c1, c2 = st.columns(2)
                    with c1: campo_selector("texto", "Texto (izquierda)", False)
                    with c2: campo_selector("img",   "Foto (derecha)",   True)

                elif tipo == "photo-text":
                    c1, c2 = st.columns(2)
                    with c1: campo_selector("img",   "Foto (izquierda)", True)
                    with c2: campo_selector("texto", "Texto (derecha)",  False)

                elif tipo == "photo-full":
                    c1, c2 = st.columns(2)
                    with c1: campo_selector("img",   "Foto (ancho completo)", True)
                    with c2: campo_selector("extra", "Campo texto debajo",    False)

        # Aplicar reorden / borrado
        if to_delete is not None:
            st.session_state["html_bloques"].pop(to_delete)
            st.session_state.pop("zip_html_bytes", None)
            st.rerun()
        if to_move is not None:
            b = st.session_state["html_bloques"]
            b[to_move[0]], b[to_move[1]] = b[to_move[1]], b[to_move[0]]
            st.session_state.pop("zip_html_bytes", None)
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Preview HTML con el primer producto
        with st.expander("👁 Preview HTML — primer producto", expanded=False):
            layout_actual = [{"tipo": b["tipo"], "campos": b["campos"]}
                             for b in st.session_state["html_bloques"]]
            html_preview = _generar_html_fila(muestra, layout_actual)
            st.components.v1.html(html_preview, height=700, scrolling=True)

        # Generar ZIP
        if st.button("⚡ Generar ZIP de HTMLs", key="btn_html", use_container_width=True):
            layout_final = [{"tipo": b["tipo"], "campos": b["campos"]}
                            for b in st.session_state["html_bloques"]]
            with st.spinner("Generando HTMLs..."):
                st.session_state["zip_html_bytes"] = generar_zip_html(df_resultado, layout_final)
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
