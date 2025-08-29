import os
import json
from typing import List, Dict, Any

INVENTORY_FILE = "inventario.txt"
INVOICES_FILE = "facturas.txt"

INVENTORY_HEADER = "id|nombre|precio|stock"

def ensure_files_exist() -> None:
    
    # Inventario con encabezado
    if not os.path.exists(INVENTORY_FILE):
        with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
            f.write(INVENTORY_HEADER + "\n")
    else:
        # Garantizar que tenga encabezado
        with open(INVENTORY_FILE, "r+", encoding="utf-8") as f:
            content = f.read()
            if not content.strip():
                f.seek(0)
                f.write(INVENTORY_HEADER + "\n")
            elif not content.splitlines()[0].strip().lower().startswith("id|nombre|precio|stock"):
                f.seek(0, 0)
                f.write(INVENTORY_HEADER + "\n" + content)

    # Facturas como JSON Lines
    if not os.path.exists(INVOICES_FILE):
        with open(INVOICES_FILE, "w", encoding="utf-8") as f:
            f.write("")

def _parse_inventory_line(line: str) -> Dict[str, Any]:
    parts = [p.strip() for p in line.split("|")]
    if len(parts) != 4:
        raise ValueError("Linea de inventario invalida")
    pid, nombre, precio, stock = parts
    return {
        "id": int(pid),
        "nombre": nombre,
        "precio": float(precio),
        "stock": int(stock),
    }

def read_inventory() -> List[Dict[str, Any]]:
    ensure_files_exist()
    products: List[Dict[str, Any]] = []
    with open(INVENTORY_FILE, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            if i == 0 and line.lower().startswith("id|nombre|precio|stock"):
                continue
            try:
                products.append(_parse_inventory_line(line))
            except Exception:

                # Ignorar líneas corruptas
                continue
    return products

def write_inventory(products: List[Dict[str, Any]]) -> None:
    ensure_files_exist()
    lines = [INVENTORY_HEADER]
    for p in products:
        lines.append(f'{p["id"]}|{p["nombre"]}|{p["precio"]}|{p["stock"]}')
    with open(INVENTORY_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def read_invoices() -> List[Dict[str, Any]]:
    ensure_files_exist()
    invoices: List[Dict[str, Any]] = []
    with open(INVOICES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                invoices.append(json.loads(line))
            except Exception:
                
                # Ignorar líneas corruptas
                continue
    return invoices

def write_invoices(invoices: List[Dict[str, Any]]) -> None:
    ensure_files_exist()
    with open(INVOICES_FILE, "w", encoding="utf-8") as f:
        for inv in invoices:
            f.write(json.dumps(inv, ensure_ascii=False) + "\n")

def append_invoice(invoice: Dict[str, Any]) -> None:
    ensure_files_exist()
    with open(INVOICES_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(invoice, ensure_ascii=False) + "\n")
