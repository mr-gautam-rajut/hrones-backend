from fastapi import APIRouter, HTTPException, Query
from app.schemas.order_schema import OrderCreate
from app.db.connection import db
from bson import ObjectId
from typing import List

router = APIRouter()

# ---------- CREATE ORDER ----------
@router.post("/", status_code=201)
async def create_order(order: OrderCreate):
    try:
        order_doc = order.dict()
        result = await db.orders.insert_one(order_doc)
        return {"id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating order: {str(e)}")


# ---------- LIST ORDERS FOR A USER ----------
@router.get("/{user_id}")
async def list_orders(
    user_id: str,
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0)
):
    try:
        query = {"userId": user_id}
        cursor = db.orders.find(query).skip(offset).limit(limit)
        orders = []

        async for order in cursor:
            items = []
            total = 0

            for item in order.get("items", []):
                try:
                    product = await db.products.find_one({"_id": ObjectId(item["productId"])})
                    if not product:
                        continue

                    product_info = {
                        "name": product.get("name", "Unknown"),
                        "id": str(product["_id"])
                    }

                    quantity = item.get("qty", 0)
                    price = product.get("price", 0)

                    items.append({
                        "productDetails": product_info,
                        "qty": quantity
                    })

                    total += quantity * price

                except Exception:
                    continue  # Skip problematic item

            orders.append({
                "id": str(order["_id"]),
                "items": items,
                "total": total
            })

        return {
            "data": orders,
            "page": {
                "next": offset + limit,
                "limit": limit,
                "previous": max(offset - limit, 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching orders: {str(e)}")


# ---------- UPDATE ORDER ----------
@router.put("/{order_id}")
async def update_order(order_id: str, updated_order: OrderCreate):
    try:
        result = await db.orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": updated_order.dict()}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Order not found or nothing was changed.")
        return {"message": "Order updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating order: {str(e)}")


# ---------- DELETE ORDER ----------
@router.delete("/{order_id}")
async def delete_order(order_id: str):
    try:
        result = await db.orders.delete_one({"_id": ObjectId(order_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Order not found.")
        return {"message": "Order deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting order: {str(e)}")
