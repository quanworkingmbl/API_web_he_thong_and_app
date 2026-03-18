"""
Permission and Role-Based Access Control (RBAC) utilities
"""
from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.role import Role, RolePermission
from app.models.permission import Permission

# Role constants based on permission matrix
class RoleType:
    ADMIN = "admin"  # Admin hệ thống
    OPERATION_COORDINATOR = "operation_coordinator"  # Điều phối vận hành
    CONTENT_MANAGER = "content_manager"  # Quản lý nội dung
    COOPERATIVE_STAFF = "cooperative_staff"  # Cán bộ Hợp tác xã

# Permission constants
class PermissionName:
    # Product Management
    PRODUCT_VIEW = "product_view"
    PRODUCT_APPROVE = "product_approve"
    PRODUCT_EDIT = "product_edit"
    PRODUCT_LABEL = "product_label"
    
    # Payment Management
    PAYMENT_VIEW = "payment_view"
    PAYMENT_CONFIG = "payment_config"
    PAYMENT_RECONCILIATION = "payment_reconciliation"
    PAYMENT_REFUND = "payment_refund"
    
    # Content Management
    CONTENT_VIEW = "content_view"
    CONTENT_APPROVE = "content_approve"
    
    # Contract Management
    CONTRACT_VIEW = "contract_view"
    CONTRACT_MANAGE = "contract_manage"
    
    # Complaint Management
    COMPLAINT_VIEW = "complaint_view"
    COMPLAINT_HANDLE = "complaint_handle"
    
    # System Control
    SYSTEM_CONTROL = "system_control"

def get_user_roles(user: User, db: Session) -> List[str]:
    """Get list of role names for a user"""
    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    roles = []
    for user_role in user_roles:
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
        if role:
            roles.append(role.role_name.lower())
    return roles

def get_user_permissions(user: User, db: Session) -> List[str]:
    """Get list of permission names for a user"""
    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    permission_ids = set()
    
    for user_role in user_roles:
        role_permissions = db.query(RolePermission).filter(
            RolePermission.role_id == user_role.role_id
        ).all()
        for rp in role_permissions:
            permission_ids.add(rp.permission_id)
    
    permissions = []
    for perm_id in permission_ids:
        perm = db.query(Permission).filter(Permission.id == perm_id).first()
        if perm:
            permissions.append(perm.name.lower())
    
    return permissions

def has_role(user: User, role_name: str, db: Session) -> bool:
    """Check if user has a specific role"""
    roles = get_user_roles(user, db)
    return role_name.lower() in roles

def has_permission(user: User, permission_name: str, db: Session) -> bool:
    """Check if user has a specific permission"""
    permissions = get_user_permissions(user, db)
    return permission_name.lower() in permissions

def has_any_role(user: User, role_names: List[str], db: Session) -> bool:
    """Check if user has any of the specified roles"""
    user_roles = get_user_roles(user, db)
    return any(role.lower() in user_roles for role in role_names)

def has_any_permission(user: User, permission_names: List[str], db: Session) -> bool:
    """Check if user has any of the specified permissions"""
    user_permissions = get_user_permissions(user, db)
    return any(perm.lower() in user_permissions for perm in permission_names)

def require_role(role_name: str):
    """Decorator to require a specific role"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Find current_user and db in kwargs
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            
            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication required"
                )
            
            if not has_role(current_user, role_name, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires role: {role_name}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_permission(permission_name: str):
    """Decorator to require a specific permission"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            
            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication required"
                )
            
            if not has_permission(current_user, permission_name, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires permission: {permission_name}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_any_role(role_names: List[str]):
    """Decorator to require any of the specified roles"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            
            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication required"
                )
            
            if not has_any_role(current_user, role_names, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires one of these roles: {', '.join(role_names)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_any_permission(permission_names: List[str]):
    """Decorator to require any of the specified permissions"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            db = kwargs.get('db')
            
            if not current_user or not db:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Authentication required"
                )
            
            if not has_any_permission(current_user, permission_names, db):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires one of these permissions: {', '.join(permission_names)}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Permission checkers based on permission matrix
def check_product_approve_access(user: User, db: Session) -> bool:
    """Check if user can approve products"""
    roles = get_user_roles(user, db)
    # Admin, Content Manager have full access
    return RoleType.ADMIN in roles or RoleType.CONTENT_MANAGER in roles

def check_payment_config_access(user: User, db: Session) -> bool:
    """Check if user can configure payment settings"""
    roles = get_user_roles(user, db)
    # Only Admin has full access
    return RoleType.ADMIN in roles

def check_payment_reconciliation_access(user: User, db: Session) -> bool:
    """Check if user can access payment reconciliation"""
    roles = get_user_roles(user, db)
    # Admin can view, Operation Coordinator has full access
    return RoleType.ADMIN in roles or RoleType.OPERATION_COORDINATOR in roles

def check_content_approve_access(user: User, db: Session) -> bool:
    """Check if user can approve content"""
    roles = get_user_roles(user, db)
    # Admin and Content Manager have full access
    return RoleType.ADMIN in roles or RoleType.CONTENT_MANAGER in roles

def check_contract_manage_access(user: User, db: Session) -> bool:
    """Check if user can manage contracts"""
    roles = get_user_roles(user, db)
    # Admin and Operation Coordinator have full access
    return RoleType.ADMIN in roles or RoleType.OPERATION_COORDINATOR in roles

def check_complaint_handle_access(user: User, db: Session) -> bool:
    """Check if user can handle complaints"""
    roles = get_user_roles(user, db)
    # Admin and Operation Coordinator have full access
    return RoleType.ADMIN in roles or RoleType.OPERATION_COORDINATOR in roles

def check_system_control_access(user: User, db: Session) -> bool:
    """Check if user has system control access"""
    roles = get_user_roles(user, db)
    # Only Admin has full access
    return RoleType.ADMIN in roles

