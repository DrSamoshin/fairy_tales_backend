from uuid import UUID
from datetime import datetime, timezone
from app.db.db_sessions import get_point_db

from app.schemas.category import CategoryCreate
from app.schemas.employee import EmployeeCreate
from app.schemas.product import ProductCreate
from app.schemas.supplier import SupplierCreate
from app.schemas.supply import SupplyCreate
from app.schemas.item import ItemCreate

from app.crud import category as crud_category
from app.crud import employee as crud_employee
from app.crud import product as crud_product
from app.crud.warehouse import supply as crud_supply, supplier as crud_supplier
from app.crud import item as crud_item


def fill_db(user_id: UUID):
    db_gen = get_point_db(user_id=user_id)
    db = next(db_gen)
    try:
        category = CategoryCreate(name="coffee")
        db_category = crud_category.create_category(db, category)

        employee_name = "Vladislav"
        db_employee = crud_employee.get_employee_by_name(db, name=employee_name)
        if not db_employee:
            employee = EmployeeCreate(name=employee_name, position="barista")
            db_employee = crud_employee.create_employee(db, employee)

        product = ProductCreate(
            name="Americano", category_id=db_category.id, price="5.0", online_shop=True
        )
        db_product = crud_product.create_product(db, product)

        supplier = SupplierCreate(name="Sorso")
        db_supplier = crud_supplier.create_supplier(db, supplier)

        supply = SupplyCreate(
            date=datetime.now(timezone.utc), supplier_id=db_supplier.id
        )
        db_supply = crud_supply.create_supply(db, supply)

        item = ItemCreate(
            name="Sugar",
            measurement="kg",
        )
        db_item = crud_item.create_item(db, item)

    finally:
        db.close()


if __name__ == "__main__":
    # user_id = input("user_id: ")
    user_id = "5d7b0071-40a5-454b-bc44-555e7859f055"
    fill_db(UUID(user_id.strip()))
