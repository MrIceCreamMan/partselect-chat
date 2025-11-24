import React, { useState, useEffect } from "react";
import "./ProductCard.css";

const FALLBACK_IMG =
    "data:image/svg+xml;utf8," +
    encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="150" height="150">
      <rect width="100%" height="100%" fill="#eee"/>
      <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle"
        fill="#999" font-family="sans-serif" font-size="14">
        No Image
      </text>
    </svg>
  `);

function ProductCard({ product }) {
    const [src, setSrc] = useState(product?.image_url || FALLBACK_IMG);

    useEffect(() => {
        setSrc(product?.image_url || FALLBACK_IMG);
    }, [product?.image_url]);

    const handleAddToCart = () => {
        alert(`Added ${product.name} to cart!`);
    };

    const handleImgError = (e) => {
        // prevent infinite loops if fallback also fails
        if (e.currentTarget.src.endsWith(FALLBACK_IMG)) return;
        setSrc(FALLBACK_IMG);
    };

    return (
        <div className="product-card">
            <div className="product-image">
                <img
                    src={src}
                    alt={product?.name || "product"}
                    onError={handleImgError}
                    loading="lazy"
                />
            </div>

            <div className="product-details">
                <div className="product-header">
                    <span className="product-part-number">{product.part_number}</span>
                    {product.in_stock && <span className="in-stock-badge">In Stock</span>}
                </div>

                <h4 className="product-name">{product.name}</h4>
                <p className="product-description">{product.description}</p>

                <div className="product-footer">
                    <span className="product-price">
                        ${Number(product.price || 0).toFixed(2)}
                    </span>
                    <button className="add-to-cart-btn" onClick={handleAddToCart}>
                        Add to Cart
                    </button>
                </div>
            </div>
        </div>
    );
}

export default ProductCard;