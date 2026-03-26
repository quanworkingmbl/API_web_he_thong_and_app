from fastapi import APIRouter
from app.api.v1 import (
    auth,
    users,
    roles,
    organizations,
    dashboard,
    media,
    products,
    payments,
    content,
    complaints,
    contracts,
    stats,
    orders,
    categories,
    regions,
    mobile_app,
    cart,
    seller,
    shipping,
    reviews,
    returns,
    settlement,
    traceability,
    seller_onboarding,
    promotions,
)

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# API routes
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(roles.router, prefix="/admin/roles", tags=["Roles"])
api_router.include_router(organizations.router, prefix="/org", tags=["Organizations"])
api_router.include_router(dashboard.router, tags=["Dashboard"])
api_router.include_router(media.router, prefix="/medias", tags=["Media"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(content.router, prefix="/content", tags=["Content"])
api_router.include_router(complaints.router, prefix="/complaints", tags=["Complaints"])
api_router.include_router(contracts.router, prefix="/contracts", tags=["Contracts"])
api_router.include_router(stats.router, tags=["Stats"])

# E-commerce core routes
api_router.include_router(orders.router, prefix="/orders", tags=["Orders"])
api_router.include_router(categories.router, prefix="/categories", tags=["Categories"])
api_router.include_router(regions.router, prefix="/regions", tags=["Regions"])

# Cart
api_router.include_router(cart.router, prefix="/cart", tags=["🛒 Cart"])

# Seller API
api_router.include_router(seller.router, prefix="/seller", tags=["🏪 Seller"])
api_router.include_router(seller_onboarding.router, prefix="/seller", tags=["🏪 Seller Onboarding"])

# Shipping
api_router.include_router(shipping.router, prefix="/shipping", tags=["🚚 Shipping"])

# Reviews & Returns
api_router.include_router(reviews.router, prefix="/reviews", tags=["⭐ Reviews"])
api_router.include_router(returns.router, prefix="/returns", tags=["↩️ Returns"])

# Settlement / Payout
api_router.include_router(settlement.router, prefix="/settlement", tags=["💰 Settlement"])

# Traceability / Certificate
api_router.include_router(traceability.router, prefix="/traceability", tags=["🔍 Traceability"])

# Promotions
api_router.include_router(promotions.router, prefix="/promotions", tags=["🎁 Promotions"])

# Mobile App API
api_router.include_router(mobile_app.router, prefix="/mobile", tags=["Mobile App"])

