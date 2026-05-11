import requests
import pandas as pd
import os
import warnings
import time

warnings.filterwarnings("ignore")
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

API_KEY    = "S98GV47S10GQ09TN2TPZ".strip()
API_SECRET = "tTpRniVFG=vg7i0lMYWDxbMjQXPzQ5gVmgyQ@RL1".strip()

RUTA_APP      = "/Users/juanignaciomartinez/Applications/DescargaUrlsImagenes"
EXCEL_ENTRADA = "tus_skus.xlsx"
EXCEL_SALIDA  = "reporte_urls_final.xlsx"

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

    # 5. Exportar
    df_out = pd.DataFrame(resultados)
    df_out.to_excel(EXCEL_SALIDA, index=False)
    print(f"\n✅ FINALIZADO → {EXCEL_SALIDA} ({len(resultados)} productos)")


if __name__ == "__main__":
    ejecutar()