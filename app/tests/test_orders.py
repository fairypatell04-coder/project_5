import pytest
from sqlalchemy import select

from app.models.order import Order   # ✅ adjust path if needed


@pytest.mark.asyncio
async def test_create_order(session):
    new_order = Order(
        product_name="Mouse",
        price=500,
        quantity=3
    )

    session.add(new_order)
    await session.commit()
    await session.refresh(new_order)

    assert new_order.id is not None


@pytest.mark.asyncio
async def test_read_order(session):
    order = Order(
        product_name="Mouse",
        price=500,
        quantity=3
    )

    session.add(order)
    await session.commit()

    result = await session.execute(
        select(Order).where(Order.product_name == "Mouse")
    )

    fetched = result.scalars().first()

    assert fetched is not None
    assert fetched.price == 500
