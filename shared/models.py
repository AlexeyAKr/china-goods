from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.db import Base


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True)
    parent_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url_1688: Mapped[str | None] = mapped_column(String(500))
    rating: Mapped[float | None] = mapped_column(Float)
    min_order_qty: Mapped[int] = mapped_column(Integer, default=1)
    contacts: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categories.id"), nullable=True
    )
    supplier_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("suppliers.id"), nullable=True
    )

    price_cny: Mapped[float | None] = mapped_column(Float)
    price_rub: Mapped[float | None] = mapped_column(Float)
    weight_kg: Mapped[float | None] = mapped_column(Float)
    markup_percent: Mapped[float] = mapped_column(Float, default=30)
    min_order_qty: Mapped[int] = mapped_column(Integer, default=1)

    source_url: Mapped[str | None] = mapped_column(String(500))
    sku_1688: Mapped[str | None] = mapped_column(String(100))
    parsed_at: Mapped[datetime | None] = mapped_column(DateTime)

    attributes: Mapped[dict] = mapped_column(JSONB, default=dict)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    category: Mapped["Category | None"] = relationship(back_populates="products")
    supplier: Mapped["Supplier | None"] = relationship()