"""
Centralized Permission Management System

This module provides reusable permission check functions for API endpoints.
Replaces scattered inline permission checks with consistent, maintainable helpers.

Usage:
    from app.core.permissions import require_admin, require_seller, check_ownership

    @router.get("/admin/users")
    async def get_users(current_user: User = Depends(get_current_user)):
        require_admin(current_user)
        # ... rest of endpoint logic
"""

from fastapi import HTTPException, status
from app.models.user import User
from typing import Optional


# ==============================================================================
# ROLE-BASED PERMISSION CHECKS
# ==============================================================================

def require_admin(user: User) -> None:
    """
    Requires user type to be 'admin'.

    Raises:
        HTTPException 403: If user is not an admin

    Usage:
        require_admin(current_user)
    """
    if user.type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


def require_seller(user: User, allow_admin: bool = False) -> None:
    """
    Requires user type to be 'producer' or 'seller'.

    Args:
        user: Current authenticated user
        allow_admin: If True, also allows admin users (default: False)

    Raises:
        HTTPException 403: If user is not a seller/producer (or admin if allowed)

    Usage:
        require_seller(current_user)  # Only seller/producer
        require_seller(current_user, allow_admin=True)  # Seller/producer/admin
    """
    allowed_types = {"producer", "seller"}
    if allow_admin:
        allowed_types.add("admin")

    if user.type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seller access required"
        )


def require_seller_or_admin(user: User) -> None:
    """
    Allows both sellers (producer/seller) and admin users.
    Commonly used when admin needs to access seller endpoints for support.

    Raises:
        HTTPException 403: If user is neither seller nor admin

    Usage:
        require_seller_or_admin(current_user)
    """
    if user.type not in {"producer", "seller", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seller or admin access required"
        )


def require_consumer(user: User) -> None:
    """
    Requires user type to be 'consumer'.

    Raises:
        HTTPException 403: If user is not a consumer

    Usage:
        require_consumer(current_user)
    """
    if user.type != "consumer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Consumer access required"
        )


def require_content_manager(user: User, allow_admin: bool = True) -> None:
    """
    Requires user to be a content manager (or admin if allowed).
    Used for content approval endpoints.

    Args:
        user: Current authenticated user
        allow_admin: If True, also allows admin users (default: True)

    Raises:
        HTTPException 403: If user is not content_manager (or admin if allowed)

    Usage:
        require_content_manager(current_user)  # Content manager or admin
        require_content_manager(current_user, allow_admin=False)  # Only content manager
    """
    allowed_types = {"content_manager"}
    if allow_admin:
        allowed_types.add("admin")

    if user.type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Content manager access required"
        )


# ==============================================================================
# OWNERSHIP CHECKS
# ==============================================================================

def check_ownership(
    resource_user_id: int,
    current_user: User,
    allow_admin: bool = True
) -> None:
    """
    Check if user owns the resource or is admin.

    Args:
        resource_user_id: The user_id who owns the resource
        current_user: Current authenticated user
        allow_admin: If True, admin can access any resource (default: True)

    Raises:
        HTTPException 403: If user doesn't own the resource and is not admin

    Usage:
        check_ownership(product.producer_id, current_user)
        check_ownership(order.customer_id, current_user, allow_admin=False)
    """
    is_owner = resource_user_id == current_user.id
    is_admin = (current_user.type == "admin") and allow_admin

    if not (is_owner or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this resource"
        )


def check_seller_ownership(
    seller_id: int,
    current_user: User,
    allow_admin: bool = True
) -> None:
    """
    Check if seller owns the resource (product, order, etc.).
    Specifically for seller/producer resources.

    Args:
        seller_id: The seller_id or producer_id who owns the resource
        current_user: Current authenticated user
        allow_admin: If True, admin can access any resource (default: True)

    Raises:
        HTTPException 403: If user is not the seller and not admin

    Usage:
        check_seller_ownership(order.seller_id, current_user)
    """
    # First check if user is a seller
    if current_user.type not in {"producer", "seller", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Seller access required"
        )

    # Then check ownership
    is_owner = seller_id == current_user.id
    is_admin = (current_user.type == "admin") and allow_admin

    if not (is_owner or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this seller's resource"
        )


# ==============================================================================
# CONTENT APPROVAL PERMISSIONS
# ==============================================================================

def check_content_approve_access(user: User) -> None:
    """
    Check if user can approve content (posts, articles).
    Allows: admin, content_manager

    Raises:
        HTTPException 403: If user cannot approve content

    Usage:
        check_content_approve_access(current_user)
    """
    if user.type not in {"admin", "content_manager"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Content approval permission required"
        )


def check_product_approve_access(user: User) -> None:
    """
    Check if user can approve products.
    Allows: admin, content_manager

    Raises:
        HTTPException 403: If user cannot approve products

    Usage:
        check_product_approve_access(current_user)
    """
    if user.type not in {"admin", "content_manager"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Product approval permission required"
        )


# ==============================================================================
# FINANCIAL/SETTLEMENT PERMISSIONS
# ==============================================================================

def check_settlement_manage_access(user: User) -> None:
    """
    Check if user can manage settlements (create, approve, payout).
    Only admin should have this permission.

    Raises:
        HTTPException 403: If user is not admin

    Usage:
        check_settlement_manage_access(current_user)
    """
    if user.type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Settlement management permission required (admin only)"
        )


def check_payment_config_access(user: User) -> None:
    """
    Check if user can modify payment configurations (fees, cycles, etc.).
    Only admin should have this permission.

    Raises:
        HTTPException 403: If user is not admin

    Usage:
        check_payment_config_access(current_user)
    """
    if user.type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Payment configuration permission required (admin only)"
        )


# ==============================================================================
# COMPLAINT & CONTRACT MANAGEMENT
# ==============================================================================

def check_complaint_handle_access(user: User) -> None:
    """
    Check if user can handle/resolve complaints.
    Allows: admin

    Raises:
        HTTPException 403: If user cannot handle complaints

    Usage:
        check_complaint_handle_access(current_user)
    """
    if user.type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Complaint handling permission required (admin only)"
        )


def check_contract_manage_access(user: User) -> None:
    """
    Check if user can manage contracts (approve, verify).
    Allows: admin

    Raises:
        HTTPException 403: If user cannot manage contracts

    Usage:
        check_contract_manage_access(current_user)
    """
    if user.type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Contract management permission required (admin only)"
        )


# ==============================================================================
# SYSTEM CONFIGURATION & MANAGEMENT
# ==============================================================================

def check_category_manage_access(user: User) -> None:
    """
    Check if user can create/update/delete categories.
    Only admin should manage categories.

    Raises:
        HTTPException 403: If user is not admin

    Usage:
        check_category_manage_access(current_user)
    """
    if user.type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Category management permission required (admin only)"
        )


def check_region_manage_access(user: User) -> None:
    """
    Check if user can create/update/delete regions.
    Only admin should manage regions.

    Raises:
        HTTPException 403: If user is not admin

    Usage:
        check_region_manage_access(current_user)
    """
    if user.type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Region management permission required (admin only)"
        )


def check_user_manage_access(user: User) -> None:
    """
    Check if user can create/update/delete other users.
    Only admin should manage users.

    Raises:
        HTTPException 403: If user is not admin

    Usage:
        check_user_manage_access(current_user)
    """
    if user.type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User management permission required (admin only)"
        )


def check_dashboard_access(user: User) -> None:
    """
    Check if user can access admin dashboard with analytics.
    Only admin should see full system analytics.

    Raises:
        HTTPException 403: If user is not admin

    Usage:
        check_dashboard_access(current_user)
    """
    if user.type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dashboard access permission required (admin only)"
        )


def check_product_label_access(user: User) -> None:
    """
    Check if user can assign product labels (HOT, BEST_SELLER, TRENDING).
    Only admin should assign labels manually.

    Raises:
        HTTPException 403: If user is not admin

    Usage:
        check_product_label_access(current_user)
    """
    if user.type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Product label management permission required (admin only)"
        )


def check_role_manage_access(user: User) -> None:
    """
    Check if user can create/update/delete roles.
    Only admin should manage roles.

    Raises:
        HTTPException 403: If user is not admin

    Usage:
        check_role_manage_access(current_user)
    """
    if user.type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Role management permission required (admin only)"
        )


def check_organization_manage_access(user: User) -> None:
    """
    Check if user can create/update/delete organizations.
    Only admin should manage organizations.

    Raises:
        HTTPException 403: If user is not admin

    Usage:
        check_organization_manage_access(current_user)
    """
    if user.type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization management permission required (admin only)"
        )


def check_media_manage_access(user: User) -> None:
    """
    Check if user can delete media files.
    Only admin or the uploader should delete media.

    Raises:
        HTTPException 403: If user is not admin

    Usage:
        check_media_manage_access(current_user)
    """
    if user.type != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Media management permission required (admin only)"
        )


# ==============================================================================
# HELPER UTILITIES
# ==============================================================================

def is_admin(user: User) -> bool:
    """Check if user is admin (non-raising version)"""
    return user.type == "admin"


def is_seller(user: User) -> bool:
    """Check if user is seller/producer (non-raising version)"""
    return user.type in {"producer", "seller"}


def is_consumer(user: User) -> bool:
    """Check if user is consumer (non-raising version)"""
    return user.type == "consumer"


def is_content_manager(user: User) -> bool:
    """Check if user is content manager (non-raising version)"""
    return user.type == "content_manager"


# ==============================================================================
# KYC VERIFICATION CHECK
# ==============================================================================

def check_seller_kyc_verified(user: User, db) -> None:
    """
    Check if seller has completed KYC verification.
    Blocks unverified sellers from creating/publishing products.
    
    Args:
        user: Current authenticated user
        db: Database session
    
    Raises:
        HTTPException 403: If seller is not KYC verified
    
    Usage:
        check_seller_kyc_verified(current_user, db)
    """
    # Admin bypasses KYC check
    if user.type == "admin":
        return
    
    # Only check for seller/producer types
    if user.type not in {"producer", "seller"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only sellers can perform this action"
        )
    
    # Import here to avoid circular import
    from app.models.seller_profile import SellerProfile, VerificationStatus
    
    seller_profile = db.query(SellerProfile).filter(
        SellerProfile.user_id == user.id
    ).first()
    
    if not seller_profile:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn chưa có hồ sơ kinh doanh. Vui lòng hoàn tất đăng ký seller trước khi tạo sản phẩm hoặc nội dung."
        )
    
    if seller_profile.verification_status == VerificationStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hồ sơ kinh doanh đang chờ xét duyệt. Vui lòng chờ admin phê duyệt trước khi tạo sản phẩm hoặc nội dung."
        )
    
    if seller_profile.verification_status == VerificationStatus.REJECTED:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Hồ sơ kinh doanh đã bị từ chối. Lý do: {seller_profile.rejection_reason or 'Không có lý do'}. Vui lòng cập nhật hồ sơ và gửi lại."
        )
