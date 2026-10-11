"""Расчёт себестоимости, розничной цены и маржи для товаров из Китая."""
from dataclasses import dataclass

from shared.config import CNY_RUB_RATE, DELIVERY_PER_KG


@dataclass
class MarginBreakdown:
    """Полный расчёт по товару."""
    price_cny: float
    weight_kg: float
    rate: float
    delivery_per_kg: float
    markup_percent: float

    @property
    def price_rub(self) -> float:
        """Себестоимость товара в рублях (без доставки)."""
        return round(self.price_cny * self.rate, 2)

    @property
    def delivery_cost(self) -> float:
        """Стоимость доставки по весу."""
        return round(self.weight_kg * self.delivery_per_kg, 2)

    @property
    def total_cost(self) -> float:
        """Полная себестоимость: товар + доставка."""
        return round(self.price_rub + self.delivery_cost, 2)

    @property
    def retail_price(self) -> float:
        """Розничная цена с наценкой."""
        return round(self.total_cost * (1 + self.markup_percent / 100), 2)

    @property
    def margin_rub(self) -> float:
        """Маржа в рублях."""
        return round(self.retail_price - self.total_cost, 2)

    @property
    def margin_percent(self) -> float:
        """Маржа в процентах (равна наценке)."""
        return round(self.markup_percent, 2)


def calculate(
    price_cny: float,
    weight_kg: float,
    markup_percent: float = 30,
    rate: float | None = None,
    delivery_per_kg: float | None = None,
) -> MarginBreakdown:
    """Рассчитать маржу для товара.

    Args:
        price_cny: цена в юанях (с 1688)
        weight_kg: вес в килограммах
        markup_percent: наценка в % (по умолчанию 30)
        rate: курс юаня к рублю (по умолчанию из .env)
        delivery_per_kg: тариф доставки ₽/кг (по умолчанию из .env)
    """
    return MarginBreakdown(
        price_cny=price_cny,
        weight_kg=weight_kg,
        rate=rate if rate is not None else CNY_RUB_RATE,
        delivery_per_kg=delivery_per_kg if delivery_per_kg is not None else DELIVERY_PER_KG,
        markup_percent=markup_percent,
    )