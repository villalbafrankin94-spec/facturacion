from typing import List, Dict, Any, Optional
from io_utils import read_inventory, write_inventory

def _next_product_id(products: List[Dict[str, Any]]) -> int:
    return (max((p["id"] for p in products), default=0) + 1)

def list_products() -> None:
    products = read_inventory()
    if not products:
        print("No hay productos en el inventario.")
        return
    print("\n=== Inventario ===")
    print(f'{"ID":<5} {"Nombre":<25} {"Precio":>10} {"Stock":>8}')
    for p in products:
        print(f'{p["id"]:<5} {p["nombre"]:<25} {p["precio"]:>10.2f} {p["stock"]:>8}')
    print()

def add_product() -> None:
    products = read_inventory()
    pid = _next_product_id(products)
    nombre = input("Nombre del producto: ").strip()
    if not nombre:
        print("Nombre invalido.")
        return
    
    # Validar precio
    try:
        precio = float(input("Precio (ej: 12000.0): ").strip())
        if precio < 0:
            raise ValueError
    except ValueError:
        print("Precio invalido.")
        return
    
    # Validar stock
    try:
        stock = int(input("Stock (entero ≥ 0): ").strip())
        if stock < 0:
            raise ValueError
    except ValueError:
        print("Stock invalido.")
        return

    # Evitar duplicados por nombre (opcional, sensible a minúsculas)
    if any(p["nombre"].lower() == nombre.lower() for p in products):
        print("Ya existe un producto con ese nombre.")
        return

    products.append({"id": pid, "nombre": nombre, "precio": precio, "stock": stock})
    write_inventory(products)
    print(f"Producto agregado con ID {pid}.")

def _find_product(products: List[Dict[str, Any]], term: str) -> List[Dict[str, Any]]:
    term_lower = term.lower()
    matches = []

    # Buscar por ID exacto si es dígito
    if term.isdigit():
        pid = int(term)
        matches.extend([p for p in products if p["id"] == pid])
        return matches
    
    # Buscar por nombre contiene
    matches.extend([p for p in products if term_lower in p["nombre"].lower()])
    return matches

def search_product() -> None:
    products = read_inventory()
    term = input("Buscar por ID o nombre: ").strip()
    if not term:
        print("Busqueda vacia.")
        return
    results = _find_product(products, term)
    if not results:
        print("Sin resultados.")
        return
    print("\n=== Resultados ===")
    for p in results:
        print(f'ID {p["id"]}: {p["nombre"]} | Precio: {p["precio"]:.2f} | Stock: {p["stock"]}')
    print()

def update_product() -> None:
    products = read_inventory()
    term = input("ID o nombre del producto a actualizar: ").strip()
    matches = _find_product(products, term)
    if not matches:
        print("Producto no encontrado.")
        return
    
    # Si hay varios, elegir por ID
    if len(matches) > 1:
        print("Multiples coincidencias. Especifique el ID.")
        for p in matches:
            print(f'ID {p["id"]}: {p["nombre"]}')
        return
    p = matches[0]
    print(f'Seleccionado: ID {p["id"]} - {p["nombre"]} (Precio: {p["precio"]:.2f}, Stock: {p["stock"]})')
    print("¿Qué desea actualizar?")
    print("1. Precio")
    print("2. Stock")
    choice = input("Opción: ").strip()
    if choice == "1":
        try:
            new_price = float(input("Nuevo precio: ").strip())
            if new_price < 0:
                raise ValueError
        except ValueError:
            print("Precio invalido.")
            return
        p["precio"] = new_price
    elif choice == "2":
        try:
            new_stock = int(input("Nuevo stock (≥ 0): ").strip())
            if new_stock < 0:
                raise ValueError
        except ValueError:
            print("Stock invalido.")
            return
        p["stock"] = new_stock
    else:
        print("Opción invalida.")
        return

    # Persistir
    for i, pr in enumerate(products):
        if pr["id"] == p["id"]:
            products[i] = p
            break
    write_inventory(products)
    print("Producto actualizado.")

def delete_product() -> None:
    products = read_inventory()
    term = input("ID o nombre del producto a eliminar: ").strip()
    matches = _find_product(products, term)
    if not matches:
        print("Producto no encontrado.")
        return
    if len(matches) > 1:
        print("Multiples coincidencias. Especifique el ID.")
        for p in matches:
            print(f'ID {p["id"]}: {p["nombre"]}')
        return
    p = matches[0]
    confirm = input(f'Confirmar eliminación de "{p["nombre"]}" (S/N): ').strip().lower()
    if confirm != "s":
        print("Operacion cancelada.")
        return
    products = [pr for pr in products if pr["id"] != p["id"]]
    write_inventory(products)
    print("Producto eliminado.")
