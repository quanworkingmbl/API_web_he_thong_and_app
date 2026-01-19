from fastapi import APIRouter
from app.api.v1 import (
    auth,
    users,
    roles,
    permissions,
    organizations,
    dashboard,
    media,
    products,
    payments,
    content,
    complaints,
    contracts,
    stats,
)

api_router = APIRouter()

# Authentication routes
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# API routes
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(roles.router, prefix="/admin/roles", tags=["Roles"])
api_router.include_router(permissions.router, prefix="/admin/permissions", tags=["Permissions"])
api_router.include_router(organizations.router, prefix="/org", tags=["Organizations"])
api_router.include_router(dashboard.router, tags=["Dashboard"])
api_router.include_router(media.router, prefix="/medias", tags=["Media"])
api_router.include_router(products.router, prefix="/products", tags=["Products"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(content.router, prefix="/content", tags=["Content"])
api_router.include_router(complaints.router, prefix="/complaints", tags=["Complaints"])
api_router.include_router(contracts.router, prefix="/contracts", tags=["Contracts"])
api_router.include_router(stats.router, prefix="/stats", tags=["Stats"])
