from typing import List, Dict, Any
from datetime import datetime
from io_utils import read_inventory, write_inventory, read_invoices, write_invoices, append_invoice

IVA_RATE = 0.19

def _next_invoice_id(invoices: List[Dict[str, Any]]) -> int:
    return (max((i["id"] for i in invoices), default=0) + 1)

def list_invoices() -> None:
    invoices = read_invoices()
    if not invoices:
        print("No hay facturas registradas.")
        return
    print("\n=== Facturas ===")
    print(f'{"ID":<5} {"Fecha":<20} {"Cliente":<25} {"Total":>12}')
    for inv in invoices:
        print(f'{inv["id"]:<5} {inv["fecha"]:<20} {inv["cliente"]:<25} {inv["total"]:>12.2f}')
    print()

def _print_invoice(inv: Dict[str, Any]) -> None:
    print("\n=== Detalle de Factura ===")
    print(f'ID: {inv["id"]}')
    print(f'Fecha: {inv["fecha"]}')
    print(f'Cliente: {inv["cliente"]}')
    print("\nItems:")
    print(f'{"ProdID":<7} {"Nombre":<25} {"Cant":>5} {"P.Unit":>10} {"Total":>12}')
    for it in inv["items"]:
        print(f'{it["product_id"]:<7} {it["product_name"]:<25} {it["quantity"]:>5} {it["unit_price"]:>10.2f} {it["line_total"]:>12.2f}')
    print(f'\nSubtotal: {inv["subtotal"]:.2f}')
    print(f'IVA (19%): {inv["iva"]:.2f}')
    print(f'Total: {inv["total"]:.2f}\n')

def show_invoice_detail() -> None:
    invoices = read_invoices()
    if not invoices:
        print("No hay facturas.")
        return
    try:
        iid = int(input("ID de la factura: ").strip())
    except ValueError:
        print("ID invalido.")
        return
    inv = next((i for i in invoices if i["id"] == iid), None)
    if not inv:
        print("Factura no encontrada.")
        return
    _print_invoice(inv)

def _calc_totals(items: List[Dict[str, Any]]) -> Dict[str, float]:
    subtotal = sum(it["line_total"] for it in items)
    iva = round(subtotal * IVA_RATE, 2)
    total = round(subtotal + iva, 2)
    return {"subtotal": round(subtotal, 2), "iva": iva, "total": total}

def create_invoice() -> None:
    products = read_inventory()
    if not products:
        print("No hay productos en inventario para facturar.")
        return
    customer = input("Nombre del cliente: ").strip()
    if not customer:
        print("Cliente invalido.")
        return

    # Construcción de items
    cart: List[Dict[str, Any]] = []
    products_by_id = {p["id"]: p for p in products}

    while True:
        code = input("ID de producto (o ENTER para finalizar): ").strip()
        if code == "":
            break
        if not code.isdigit():
            print("ID invalido.")
            continue
        pid = int(code)
        if pid not in products_by_id:
            print("Producto no encontrado.")
            continue
        prod = products_by_id[pid]
        print(f'Seleccionado: {prod["nombre"]} | Precio: {prod["precio"]:.2f} | Stock: {prod["stock"]}')
        try:
            qty = int(input("Cantidad: ").strip())
            if qty <= 0:
                raise ValueError
        except ValueError:
            print("Cantidad invalida.")
            continue
        if qty > prod["stock"]:
            print("Stock insuficiente.")
            continue
        # Agregar al carrito (snapshot de precio)
        line_total = round(prod["precio"] * qty, 2)
        cart.append({
            "product_id": prod["id"],
            "product_name": prod["nombre"],
            "quantity": qty,
            "unit_price": float(prod["precio"]),
            "line_total": line_total
        })

    if not cart:
        print("Factura vacia, cancelada.")
        return

    totals = _calc_totals(cart)
    invoices = read_invoices()
    iid = _next_invoice_id(invoices)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    invoice = {
        "id": iid,
        "fecha": now,
        "cliente": customer,
        "items": cart,
        "subtotal": totals["subtotal"],
        "iva": totals["iva"],
        "total": totals["total"],
    }

    # Descontar stock
    stock_changes = {}
    for it in cart:
        stock_changes[it["product_id"]] = stock_changes.get(it["product_id"], 0) + it["quantity"]

    # Validar de nuevo y aplicar
    for pid, delta in stock_changes.items():
        if products_by_id[pid]["stock"] < delta:
            print("Error de stock durante la confirmacion. Operacion cancelada.")
            return
    for pid, delta in stock_changes.items():
        products_by_id[pid]["stock"] -= delta

    # Persistir
    write_inventory(list(products_by_id.values()))
    append_invoice(invoice)
    print(f"Factura creada con ID {iid}.")
    _print_invoice(invoice)

def delete_invoice() -> None:
    invoices = read_invoices()
    if not invoices:
        print("No hay facturas.")
        return
    try:
        iid = int(input("ID de la factura a eliminar: ").strip())
    except ValueError:
        print("ID invalido.")
        return
    inv = next((i for i in invoices if i["id"] == iid), None)
    if not inv:
        print("Factura no encontrada.")
        return
    confirm = input("Confirmar eliminacion y reversión de stock (S/N): ").strip().lower()
    if confirm != "s":
        print("Operacion cancelada.")
        return

    # Revertir stock
    products = read_inventory()
    by_id = {p["id"]: p for p in products}
    for it in inv["items"]:
        pid = it["product_id"]
        if pid in by_id:
            by_id[pid]["stock"] += it["quantity"]
    write_inventory(list(by_id.values()))

    # Remover factura
    invoices = [i for i in invoices if i["id"] != iid]
    write_invoices(invoices)
    print("Factura eliminada y stock revertido.")

def edit_invoice() -> None:
    invoices = read_invoices()
    if not invoices:
        print("No hay facturas.")
        return
    try:
        iid = int(input("ID de la factura a editar: ").strip())
    except ValueError:
        print("ID invalido.")
        return
    inv = next((i for i in invoices if i["id"] == iid), None)
    if not inv:
        print("Factura no encontrada.")
        return

    print("Editando items. Deje ID vacío para terminar.")
    products = read_inventory()
    by_id = {p["id"]: p for p in products}

    # Construir mapa de cantidades originales
    original_qty = {}
    for it in inv["items"]:
        original_qty[it["product_id"]] = original_qty.get(it["product_id"], 0) + it["quantity"]

    # Mostrar items actuales
    _print_invoice(inv)

    # Nuevo conjunto de items
    new_items: List[Dict[str, Any]] = []

    while True:
        code = input("ID de producto a establecer (ENTER para terminar): ").strip()
        if code == "":
            break
        if not code.isdigit():
            print("ID invalido.")
            continue
        pid = int(code)
        if pid not in by_id:
            print("Producto no encontrado.")
            continue
        prod = by_id[pid]
        try:
            qty = int(input("Nueva cantidad (0 para remover): ").strip())
            if qty < 0:
                raise ValueError
        except ValueError:
            print("Cantidad invalida.")
            continue
        if qty == 0:
            # No lo añadimos
            print(f'{prod["nombre"]} sera removido.')
            continue
        # El precio unitario es el actual del inventario o mantenemos el de la factura?
        # Mantendremos el precio actual del inventario para cambios nuevos.
        unit_price = float(prod["precio"])
        line_total = round(unit_price * qty, 2)
        new_items.append({
            "product_id": prod["id"],
            "product_name": prod["nombre"],
            "quantity": qty,
            "unit_price": unit_price,
            "line_total": line_total
        })

    if not new_items:
        print("La factura quedaria vacia. ¿Desea eliminarla? (S/N)")
        ans = input().strip().lower()
        if ans == "s":
            # Delegar a delete_invoice?
            # Hacemos la eliminación con reversión:
            # Primero revertimos stock del original y no aplicamos nuevos cambios.
            # Luego eliminamos la factura.
            # Revertir stock original:
            products = read_inventory()
            by_id = {p["id"]: p for p in products}
            for it in inv["items"]:
                pid = it["product_id"]
                if pid in by_id:
                    by_id[pid]["stock"] += it["quantity"]
            write_inventory(list(by_id.values()))
            # Eliminar factura
            invoices = [i for i in invoices if i["id"] != iid]
            write_invoices(invoices)
            print("Factura eliminada.")
        else:
            print("Edicion cancelada. Sin cambios.")
        return

    # Calcular deltas de stock: new - original
    new_qty = {}
    for it in new_items:
        new_qty[it["product_id"]] = new_qty.get(it["product_id"], 0) + it["quantity"]

    delta = {}
    all_pids = set(new_qty.keys()).union(set(original_qty.keys()))
    for pid in all_pids:
        delta[pid] = new_qty.get(pid, 0) - original_qty.get(pid, 0)

    # Validar stock para deltas positivos
    products = read_inventory()
    by_id = {p["id"]: p for p in products}
    for pid, d in delta.items():
        if d > 0:
            if pid not in by_id:
                print(f"Producto {pid} ya no existe en inventario. Edicion cancelada.")
                return
            if by_id[pid]["stock"] < d:
                print(f"Stock insuficiente para producto {pid}. Edicion cancelada.")
                return

    # Aplicar deltas
    for pid, d in delta.items():
        if pid in by_id:
            by_id[pid]["stock"] -= d  # si d<0, aumenta stock; si d>0, reduce
    write_inventory(list(by_id.values()))

    # Recalcular totales
    totals = _calc_totals(new_items)
    inv["items"] = new_items
    inv["subtotal"] = totals["subtotal"]
    inv["iva"] = totals["iva"]
    inv["total"] = totals["total"]

    # Persistir facturas
    for i, f in enumerate(invoices):
        if f["id"] == inv["id"]:
            invoices[i] = inv
            break
    write_invoices(invoices)
    print("Factura actualizada.")
    _print_invoice(inv)
