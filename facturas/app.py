from io_utils import ensure_files_exist
import inventory as inv
import invoices as fac

def menu_inventory():
    while True:
        print("\n=== Menu del Inventario ===")
        print("1. Añadir producto")
        print("2. Listar productos")
        print("3. Buscar producto")
        print("4. Actualizar precio o stock")
        print("5. Eliminar producto")
        print("0. Volver")
        opt = input("Opcion: ").strip()
        if opt == "1":
            inv.add_product()
        elif opt == "2":
            inv.list_products()
        elif opt == "3":
            inv.search_product()
        elif opt == "4":
            inv.update_product()
        elif opt == "5":
            inv.delete_product()
        elif opt == "0":
            break
        else:
            print("Opcion invalida.")

def menu_invoices():
    while True:
        print("\n=== Menu Facturas ===")
        print("1. Crear nueva factura")
        print("2. Listar facturas")
        print("3. Mostrar detalle de factura")
        print("4. Editar elementos de factura")
        print("5. Eliminar una factura")
        print("0. Volver")
        opt = input("Opcion: ").strip()
        if opt == "1":
            fac.create_invoice()
        elif opt == "2":
            fac.list_invoices()
        elif opt == "3":
            fac.show_invoice_detail()
        elif opt == "4":
            fac.edit_invoice()
        elif opt == "5":
            fac.delete_invoice()
        elif opt == "0":
            break
        else:
            print("Opcion invalida.")

def main():
    ensure_files_exist()
    while True:
        print("\n=== Sistema de Inventario y Facturacion ===")
        print("1. Inventario")
        print("2. Facturas")
        print("0. Salir")
        opt = input("Opcion: ").strip()
        if opt == "1":
            menu_inventory()
        elif opt == "2":
            menu_invoices()
        elif opt == "0":
            print("Hasta luego.")
            break
        else:
            print("Opcion invalida.")

if __name__ == "__main__":
    main()
