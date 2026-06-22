"""Display helpers for making database output readable in Streamlit.

The database keeps original PostgreSQL/Olist column names for reproducibility.
These helpers only rename columns and category values in the Streamlit UI.
"""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

COLUMN_LABELS = {
    "table_name": "Table Name",
    "total_rows": "Total Rows",
    "customer_id": "Customer ID",
    "customer_unique_id": "Customer Unique ID",
    "customer_city": "Customer City",
    "customer_state": "Customer State",
    "seller_id": "Seller ID",
    "seller_city": "Seller City",
    "seller_state": "Seller State",
    "product_id": "Product ID",
    "product_category_name": "Product Category",
    "order_id": "Order ID",
    "order_status": "Order Status",
    "payment_type": "Payment Type",
    "review_score": "Review Score",
    "total_orders": "Total Orders",
    "total_items": "Total Items",
    "total_item_value": "Total Item Value",
    "total_items_sold": "Total Items Sold",
    "total_units_sold": "Total Units Sold",
    "total_revenue": "Total Revenue",
    "avg_price": "Average Price",
    "avg_payment_value": "Average Payment Value",
    "total_payment_value": "Total Payment Value",
    "total_payments": "Total Payments",
    "total_reviews": "Total Reviews",
    "similar_customer_count": "Similar Customer Count",
    "similar_purchase_count": "Similar Purchase Count",
    "recommendation_score": "Recommendation Score",
    "recommendation_rank": "Recommendation Rank",
    "query": "Query",
    "before_index_ms": "Before Index (ms)",
    "after_index_ms": "After Index (ms)",
    "change": "Change",
    "main_plan_change": "Main Plan Change",
}

TABLE_LABELS = {
    "customers": "Customers",
    "sellers": "Sellers",
    "products": "Products",
    "orders": "Orders",
    "order_items": "Order Items",
    "order_payments": "Order Payments",
    "order_reviews": "Order Reviews",
}

# Product category translations from the Olist Portuguese category slugs to readable English.
CATEGORY_LABELS = {
    "agro_industria_e_comercio": "Agro Industry and Commerce",
    "alimentos": "Food",
    "alimentos_bebidas": "Food and Drinks",
    "artes": "Art",
    "artes_e_artesanato": "Arts and Craftsmanship",
    "artigos_de_festas": "Party Supplies",
    "artigos_de_natal": "Christmas Supplies",
    "audio": "Audio",
    "automotivo": "Automotive",
    "bebes": "Baby Products",
    "bebidas": "Drinks",
    "beleza_saude": "Health and Beauty",
    "brinquedos": "Toys",
    "cama_mesa_banho": "Bed, Bath and Table",
    "casa_conforto": "Home Comfort",
    "casa_conforto_2": "Home Comfort 2",
    "casa_construcao": "Home Construction",
    "cds_dvds_musicais": "Music CDs and DVDs",
    "cine_foto": "Film and Photography",
    "climatizacao": "Air Conditioning",
    "consoles_games": "Consoles and Games",
    "construcao_ferramentas_construcao": "Construction Tools",
    "construcao_ferramentas_ferramentas": "Construction Tools and Hardware",
    "construcao_ferramentas_iluminacao": "Construction Lighting",
    "construcao_ferramentas_jardim": "Construction and Garden Tools",
    "construcao_ferramentas_seguranca": "Construction Safety Tools",
    "cool_stuff": "Cool Stuff",
    "dvds_blu_ray": "DVDs and Blu-ray",
    "eletrodomesticos": "Home Appliances",
    "eletrodomesticos_2": "Home Appliances 2",
    "eletronicos": "Electronics",
    "eletroportateis": "Small Appliances",
    "esporte_lazer": "Sports and Leisure",
    "fashion_bolsas_e_acessorios": "Fashion Bags and Accessories",
    "fashion_calcados": "Fashion Shoes",
    "fashion_esporte": "Fashion Sports",
    "fashion_roupa_feminina": "Women's Fashion Clothing",
    "fashion_roupa_infanto_juvenil": "Children's Fashion Clothing",
    "fashion_roupa_masculina": "Men's Fashion Clothing",
    "fashion_underwear_e_moda_praia": "Underwear and Beach Fashion",
    "ferramentas_jardim": "Garden Tools",
    "flores": "Flowers",
    "fraldas_higiene": "Diapers and Hygiene",
    "industria_comercio_e_negocios": "Industry, Commerce and Business",
    "informatica_acessorios": "Computer Accessories",
    "instrumentos_musicais": "Musical Instruments",
    "la_cuisine": "La Cuisine",
    "livros_importados": "Imported Books",
    "livros_interesse_geral": "General Interest Books",
    "livros_tecnicos": "Technical Books",
    "malas_acessorios": "Luggage and Accessories",
    "market_place": "Marketplace",
    "moveis_colchao_e_estofado": "Mattresses and Upholstery",
    "moveis_cozinha_area_de_servico_jantar_e_jardim": "Kitchen, Dining, Laundry and Garden Furniture",
    "moveis_decoracao": "Furniture and Decoration",
    "moveis_escritorio": "Office Furniture",
    "moveis_quarto": "Bedroom Furniture",
    "moveis_sala": "Living Room Furniture",
    "musica": "Music",
    "papelaria": "Stationery",
    "pcs": "Computers",
    "perfumaria": "Perfumery",
    "pet_shop": "Pet Shop",
    "portateis_casa_forno_e_cafe": "Portable Home, Oven and Coffee",
    "relogios_presentes": "Watches and Gifts",
    "seguros_e_servicos": "Security and Services",
    "sinalizacao_e_seguranca": "Signage and Security",
    "tablets_impressao_imagem": "Tablets, Printing and Image",
    "telefonia": "Telephony",
    "telefonia_fixa": "Fixed Telephony",
    "unknown": "Unknown",
    None: "Unknown",
}

PAYMENT_LABELS = {
    "credit_card": "Credit Card",
    "boleto": "Boleto / Bank Slip",
    "voucher": "Voucher",
    "debit_card": "Debit Card",
    "not_defined": "Not Defined",
}


def _title_from_snake(name: Any) -> str:
    text = str(name).replace("_", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text.title()


def translate_category(value: Any) -> str:
    if pd.isna(value):
        return "Unknown"
    text = str(value)
    return CATEGORY_LABELS.get(text, _title_from_snake(text))


def translate_table(value: Any) -> str:
    if pd.isna(value):
        return "Unknown"
    text = str(value)
    return TABLE_LABELS.get(text, _title_from_snake(text))


def translate_payment(value: Any) -> str:
    if pd.isna(value):
        return "Unknown"
    text = str(value)
    return PAYMENT_LABELS.get(text, _title_from_snake(text))


def translate_values(df: pd.DataFrame) -> pd.DataFrame:
    """Translate Portuguese/category slugs and internal table names into display text."""
    out = df.copy()
    for col in ["product_category_name", "Product Category"]:
        if col in out.columns:
            out[col] = out[col].map(translate_category)
    for col in ["table_name", "Table Name"]:
        if col in out.columns:
            out[col] = out[col].map(translate_table)
    for col in ["payment_type", "Payment Type"]:
        if col in out.columns:
            out[col] = out[col].map(translate_payment)
    return out


def to_display_df(df: pd.DataFrame) -> pd.DataFrame:
    """Return a UI-ready dataframe with English column labels and translated values."""
    out = translate_values(df)
    out = out.rename(columns={col: COLUMN_LABELS.get(col, _title_from_snake(col)) for col in out.columns})
    out = translate_values(out)
    return out
