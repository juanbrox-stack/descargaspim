import requests
import pandas as pd
import os
import warnings
import time
import zipfile
from pathlib import Path
from html import escape

warnings.filterwarnings("ignore")
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

API_KEY    = "".strip()
API_SECRET = "".strip()

RUTA_APP      = "/Users/juanignaciomartinez/Applications/DescargaUrlsImagenes"
EXCEL_ENTRADA = "tus_skus.xlsx"
EXCEL_SALIDA  = "reporte_urls_final.xlsx"
ZIP_SALIDA    = "html_cdiscount.zip"

# ============================================================
# ✅ CONFIGURA AQUÍ LOS CAMPOS QUE QUIERES DESCARGAR
# Usa el nombre exacto del atributo en Plytix (snake_case)
# ============================================================
CAMPOS_DESEADOS = [
    "sku",
    "nombre_producto__modelo",
    "foto_master_producto_main_image_1000x1000_png_01",   # imagen 1000x1000
    "foto_master_producto_main_image_1000x1000_png_02",
    "foto_enriquecida_01",
    "foto_enriquecida_02",
    "foto_enriquecida_03",
    "foto_enriquecida_04",
    "foto_enriquecida_05",
    "foto_enriquecida_06",
    "descripcion_corta_del_producto",
    "descripcion_larga_del_producto",
    "ean_13",
    "familia",
    "subfamilia",
]
# ============================================================

# ============================================================
# ✅ ESPECIFICACIONES TÉCNICAS PARA EL HTML
# Formato: "Etiqueta visible": "nombre_atributo_plytix"
# Deja vacío ({}) si no quieres specs en el HTML
# ============================================================
SPECS_HTML = {
    "EAN": "ean_13",
    "Familia": "familia",
    "Subfamilia": "subfamilia",
    # Añade aquí más atributos técnicos según tu catálogo:
    # "Potencia (W)": "potencia_w",
    # "Color": "color",
}
# ============================================================


def obtener_token():
    r = requests.post(
        "https://auth.plytix.com/auth/api/get-token",
        json={"api_key": API_KEY, "api_password": API_SECRET},
        headers={"Content-Type": "application/json"},
        verify=False, timeout=15
    )
    if r.status_code == 200:
        data = r.json()
        token = data["data"][0].get("access_token") if isinstance(data, dict) else data[0].get("access_token")
        print("✅ Token obtenido.")
        return token
    print(f"❌ Login fallido: {r.status_code} {r.text}")
    return None


def extraer_valor(val):
    """Extrae URL si es imagen/archivo, primera URL si es lista, o el valor directo."""
    if isinstance(val, dict):
        return val.get("url", val.get("thumbnail", str(val)))
    if isinstance(val, list):
        urls = [extraer_valor(v) for v in val if v]
        return " | ".join(str(u) for u in urls if u)
    return val


def buscar_ids_por_lote(skus, headers):
    """Paso 1: obtiene SKU → product_id para todos los SKUs."""
    todos = []
    lotes = [skus[i:i+20] for i in range(0, len(skus), 20)]
    print(f"🔍 Buscando IDs en {len(lotes)} lotes...")

    for i, lote in enumerate(lotes, 1):
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
                    print(f"   Lote {i}/{len(lotes)}: {len(res.json().get('data', []))} productos")
                    break
                else:
                    print(f"   ⚠ Lote {i} error {res.status_code}")
                    break
            except requests.exceptions.ReadTimeout:
                print(f"   ⏱ Timeout lote {i}, intento {intento+1}/3...")
                time.sleep(5)
        time.sleep(1)

    return todos  # lista de {id, sku, ...}


def obtener_atributos_producto(product_id, headers):
    """Paso 2: obtiene todos los atributos de un producto por su ID."""
    for intento in range(3):
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
            print(f"   ⏱ Timeout producto {product_id}, intento {intento+1}/3...")
            time.sleep(3)
    return {}




# ─────────────────────────────────────────────────────────────
# GENERACIÓN HTML CDISCOUNT
# ─────────────────────────────────────────────────────────────

def _url(fila, campo):
    """Devuelve la primera URL de un campo (soporta separador ' | ')."""
    val = fila.get(campo, "") or ""
    return str(val).split(" | ")[0].strip()


def generar_html_producto(fila):
    """
    Genera el HTML enriquecido para Cdiscount de un producto.
    fila: dict con las claves de CAMPOS_DESEADOS ya procesadas.
    """
    sku         = escape(str(fila.get("SKU", "")))
    nombre      = escape(str(fila.get("nombre_producto__modelo", "") or sku))
    desc_corta  = escape(str(fila.get("descripcion_corta_del_producto", "") or ""))
    desc_larga  = escape(str(fila.get("descripcion_larga_del_producto", "") or ""))
    img_hero    = _url(fila, "foto_master_producto_main_image_1000x1000_png_01")

    # ── Fotos enriquecidas (solo las que tienen URL) ──────────
    fotos_enriquecidas = []
    for n in range(1, 7):
        u = _url(fila, f"foto_enriquecida_0{n}")
        if u:
            fotos_enriquecidas.append(u)

    # ── Feature blocks: imagen enriquecida + descripción larga ─
    # Si no hay desc_larga, usamos desc_corta como fallback
    texto_bloques = desc_larga or desc_corta

    feature_cards_html = ""
    for url in fotos_enriquecidas:
        feature_cards_html += f"""
        <div class="cd-feature-card">
          <img src="{url}" alt="{nombre}" loading="lazy" />
        </div>"""

    features_section = f"""
  <section class="cd-features">
    <h4 class="cd-section-title">Détails du produit</h4>
    <div class="cd-feature-grid">{feature_cards_html}
    </div>
  </section>""" if feature_cards_html else ""

    # ── Especificaciones técnicas ─────────────────────────────
    spec_items = ""
    for etiqueta, campo in SPECS_HTML.items():
        val = fila.get(campo, "") or ""
        if val:
            spec_items += f"""
      <li>
        <span class="spec-label">{escape(etiqueta)}</span>
        <span class="spec-value">{escape(str(val))}</span>
      </li>"""

    specs_section = f"""
  <section class="cd-specs">
    <h4 class="cd-section-title">Caractéristiques</h4>
    <ul class="cd-spec-list">{spec_items}
    </ul>
  </section>""" if spec_items else ""

    # ── Imagen hero fallback ──────────────────────────────────
    hero_img_tag = (
        f'<img src="{img_hero}" alt="{nombre}" loading="lazy" />'
        if img_hero
        else '<div class="cd-img-placeholder">Sin imagen</div>'
    )

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{nombre}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: Arial, sans-serif;
    color: #222;
    background: #fff;
    max-width: 960px;
    margin: auto;
    padding: 28px 16px;
  }}

  /* HERO */
  .cd-hero {{
    display: flex;
    gap: 36px;
    align-items: flex-start;
    margin-bottom: 44px;
    flex-wrap: wrap;
  }}
  .cd-hero img {{
    width: 360px;
    max-width: 100%;
    border-radius: 8px;
    object-fit: contain;
    border: 1px solid #e8e8e8;
    background: #fafafa;
  }}
  .cd-img-placeholder {{
    width: 360px;
    height: 260px;
    background: #f0f0f0;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #aaa;
    border-radius: 8px;
    font-size: 0.85rem;
  }}
  .cd-hero-content {{ flex: 1; min-width: 220px; }}
  .cd-hero-content h2 {{
    font-size: 1.45rem;
    font-weight: 700;
    margin-bottom: 10px;
    color: #111;
    line-height: 1.3;
  }}
  .cd-sku {{
    font-size: 0.78rem;
    color: #999;
    margin-bottom: 14px;
    letter-spacing: .03em;
  }}
  .cd-hero-content p {{
    font-size: 0.95rem;
    line-height: 1.65;
    color: #444;
  }}

  /* SECTION TITLE */
  .cd-section-title {{
    font-size: 0.85rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .08em;
    color: #e84e0f;
    margin-bottom: 20px;
    padding-bottom: 8px;
    border-bottom: 2px solid #e84e0f;
  }}

  /* FEATURES GRID */
  .cd-features {{ margin-bottom: 44px; }}
  .cd-feature-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
  }}
  .cd-feature-card {{
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid #eee;
    background: #fafafa;
  }}
  .cd-feature-card img {{
    width: 100%;
    aspect-ratio: 1 / 1;
    object-fit: contain;
    display: block;
    padding: 8px;
  }}

  /* SPECS */
  .cd-specs {{ margin-bottom: 40px; }}
  .cd-spec-list {{ list-style: none; }}
  .cd-spec-list li {{
    display: flex;
    justify-content: space-between;
    padding: 9px 14px;
    font-size: 0.88rem;
    gap: 16px;
    border-bottom: 1px solid #f0f0f0;
  }}
  .cd-spec-list li:nth-child(odd) {{ background: #f9f9f9; }}
  .spec-label {{ color: #555; }}
  .spec-value {{ font-weight: 600; color: #111; text-align: right; }}
</style>
</head>
<body>

  <section class="cd-hero">
    {hero_img_tag}
    <div class="cd-hero-content">
      <p class="cd-sku">SKU: {sku}</p>
      <h2>{nombre}</h2>
      <p>{desc_corta}</p>
    </div>
  </section>
{features_section}
{specs_section}
</body>
</html>"""


def generar_zip_htmls(resultados, ruta_zip):
    """Genera un ZIP con un HTML por SKU."""
    generados = 0
    errores   = 0

    with zipfile.ZipFile(ruta_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for fila in resultados:
            sku = str(fila.get("SKU", "sin_sku")).strip()
            try:
                html = generar_html_producto(fila)
                # Nombre de archivo seguro
                nombre_archivo = f"{sku.replace('/', '_').replace(' ', '_')}.html"
                zf.writestr(nombre_archivo, html.encode("utf-8"))
                generados += 1
            except Exception as e:
                print(f"   ⚠ Error generando HTML para {sku}: {e}")
                errores += 1

    print(f"   ✅ {generados} HTMLs generados — {errores} errores")
    return generados


def ejecutar():
    if not os.path.exists(RUTA_APP):
        print(f"❌ No se encuentra la carpeta: {RUTA_APP}")
        return
    os.chdir(RUTA_APP)

    # 1. Cargar SKUs
    try:
        df = pd.read_excel(EXCEL_ENTRADA)
        col_sku = [c for c in df.columns if 'sku' in c.lower()][0]
        skus = df[col_sku].dropna().astype(str).tolist()
        print(f"📦 {len(skus)} SKUs cargados.")
    except Exception as e:
        print(f"❌ Error leyendo Excel: {e}")
        return

    # 2. Token
    token = obtener_token()
    if not token:
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # 3. Buscar IDs
    productos_base = buscar_ids_por_lote(skus, headers)
    print(f"   → {len(productos_base)} productos encontrados.")

    # 4. Para cada producto, obtener atributos completos
    print(f"\n📥 Descargando atributos de {len(productos_base)} productos...")
    resultados = []

    for idx, p in enumerate(productos_base, 1):
        product_id = p["id"]
        sku        = p.get("sku", "")
        print(f"   [{idx}/{len(productos_base)}] SKU: {sku}")

        attrs = obtener_atributos_producto(product_id, headers)

        fila = {"SKU": sku}
        for campo in CAMPOS_DESEADOS:
            if campo == "sku":
                continue  # ya lo tenemos
            val = attrs.get(campo)
            fila[campo] = extraer_valor(val) if val is not None else ""

        resultados.append(fila)
        time.sleep(0.3)  # respetar rate limit

    # 5. Exportar Excel
    df_out = pd.DataFrame(resultados)
    df_out.to_excel(EXCEL_SALIDA, index=False)
    print(f"\n✅ Excel exportado → {EXCEL_SALIDA} ({len(resultados)} productos)")

    # 6. Generar ZIP con HTMLs para Cdiscount
    print(f"\n🌐 Generando HTMLs para Cdiscount...")
    n = generar_zip_htmls(resultados, ZIP_SALIDA)
    print(f"✅ FINALIZADO → {ZIP_SALIDA} ({n} archivos HTML)")


if __name__ == "__main__":
    ejecutar()
