from fastapi import APIRouter, Query, HTTPException
from app.schemas.product_schema import ProductCreate
from app.db.connection import db
from bson import ObjectId

router = APIRouter()

@router.post("/", status_code=201)
async def create_product(product: ProductCreate):
    try:
        product_data = product.dict()
        result = await db.products.insert_one(product_data)
        return {"id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting product: {str(e)}")


@router.get("/")
async def list_products(
    name: str = Query(None),
    size: str = Query(None),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0)
):
    try:
        query = {}
        if name:
            query["name"] = {"$regex": name, "$options": "i"}  # case-insensitive search
        if size:
            query["sizes.size"] = size

        cursor = db.products.find(query, {"sizes": 0}).skip(offset).limit(limit)

        products = []
        async for doc in cursor:
            doc["id"] = str(doc["_id"])
            doc.pop("_id", None)
            products.append(doc)

        return {
            "data": products,
            "page": {
                "next": offset + limit,
                "limit": limit,
                "previous": max(offset - limit, 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")
