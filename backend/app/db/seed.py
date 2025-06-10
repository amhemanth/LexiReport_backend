from sqlalchemy.orm import Session
from app.models.core.permission import Role, Permission, RolePermission
import uuid

def seed_roles_and_permissions(db: Session):
    """Seed initial roles and permissions."""
    
    # Create permissions
    permissions = {
        # User management permissions
        "user:create": "Create new users",
        "user:read": "View user details",
        "user:update": "Update user information",
        "user:delete": "Delete users",
        
        # Role management permissions
        "role:create": "Create new roles",
        "role:read": "View role details",
        "role:update": "Update role information",
        "role:delete": "Delete roles",
        
        # Permission management permissions
        "permission:assign": "Assign permissions to roles",
        "permission:revoke": "Revoke permissions from roles",
        
        # System management permissions
        "system:settings": "Manage system settings",
        "system:logs": "View system logs",
        
        # Content management permissions
        "content:create": "Create content",
        "content:read": "View content",
        "content:update": "Update content",
        "content:delete": "Delete content",
        
        # Analytics permissions
        "analytics:view": "View analytics",
        "analytics:export": "Export analytics data",
    }
    
    # Create roles
    roles = {
        "superadmin": {
            "description": "Super Administrator with full system access",
            "permissions": list(permissions.keys())
        },
        "admin": {
            "description": "Administrator with system management capabilities",
            "permissions": [
                "user:create", "user:read", "user:update",
                "role:read",
                "permission:assign", "permission:revoke",
                "system:settings", "system:logs",
                "content:create", "content:read", "content:update", "content:delete",
                "analytics:view", "analytics:export"
            ]
        },
        "manager": {
            "description": "Manager with team and content management capabilities",
            "permissions": [
                "user:read",
                "content:create", "content:read", "content:update", "content:delete",
                "analytics:view"
            ]
        },
        "user": {
            "description": "Regular user with basic access",
            "permissions": [
                "content:read",
                "analytics:view"
            ]
        }
    }
    
    # Create permissions in database
    permission_objects = {}
    for name, description in permissions.items():
        permission = Permission(
            id=uuid.uuid4(),
            name=name,
            description=description,
            is_active=True
        )
        db.add(permission)
        permission_objects[name] = permission
    
    # Create roles and assign permissions
    role_objects = {}
    for name, data in roles.items():
        role = Role(
            id=uuid.uuid4(),
            name=name,
            description=data["description"],
            is_active=True
        )
        db.add(role)
        role_objects[name] = role
        
        # Create role-permission relationships
        for perm_name in data["permissions"]:
            role_permission = RolePermission(
                id=uuid.uuid4(),
                role_id=role.id,
                permission_id=permission_objects[perm_name].id
            )
            db.add(role_permission)
    
    db.commit() 