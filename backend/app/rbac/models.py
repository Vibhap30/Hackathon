"""
Role-Based Access Control (RBAC) System for PowerShare Platform
==============================================================

This module implements comprehensive RBAC with different user roles:
- Prosumer: Users who both produce and consume energy
- Consumer: Energy buyers looking for renewable sources
- Community Manager: Local network administration
- Grid Operator: System monitoring and load balancing
- Regulator: Compliance monitoring and audit trails
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from enum import Enum
from dataclasses import dataclass
import uuid
from functools import wraps
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

Base = declarative_base()

class UserRole(Enum):
    PROSUMER = "prosumer"              # Produces and consumes energy
    CONSUMER = "consumer"              # Only consumes energy
    COMMUNITY_MANAGER = "community_manager"  # Manages local communities
    GRID_OPERATOR = "grid_operator"    # System monitoring and control
    REGULATOR = "regulator"            # Compliance and auditing
    ADMIN = "admin"                    # Platform administration

class Permission(Enum):
    # Energy Trading Permissions
    CREATE_ENERGY_OFFER = "create_energy_offer"
    VIEW_ENERGY_OFFERS = "view_energy_offers"
    PURCHASE_ENERGY = "purchase_energy"
    MANAGE_OWN_TRADES = "manage_own_trades"
    VIEW_TRADING_HISTORY = "view_trading_history"
    
    # Community Permissions
    JOIN_COMMUNITY = "join_community"
    CREATE_COMMUNITY = "create_community"
    MANAGE_COMMUNITY = "manage_community"
    MODERATE_COMMUNITY = "moderate_community"
    
    # Analytics and Monitoring
    VIEW_PERSONAL_ANALYTICS = "view_personal_analytics"
    VIEW_COMMUNITY_ANALYTICS = "view_community_analytics"
    VIEW_GRID_ANALYTICS = "view_grid_analytics"
    VIEW_MARKET_ANALYTICS = "view_market_analytics"
    
    # IoT and Device Management
    REGISTER_IOT_DEVICE = "register_iot_device"
    MANAGE_OWN_DEVICES = "manage_own_devices"
    VIEW_DEVICE_DATA = "view_device_data"
    CONTROL_GRID_DEVICES = "control_grid_devices"
    
    # System Administration
    MANAGE_USERS = "manage_users"
    SYSTEM_CONFIGURATION = "system_configuration"
    VIEW_SYSTEM_LOGS = "view_system_logs"
    EMERGENCY_CONTROLS = "emergency_controls"
    
    # Compliance and Auditing
    AUDIT_TRANSACTIONS = "audit_transactions"
    GENERATE_REPORTS = "generate_reports"
    REGULATORY_OVERSIGHT = "regulatory_oversight"
    
    # Gamification
    VIEW_LEADERBOARDS = "view_leaderboards"
    PARTICIPATE_CHALLENGES = "participate_challenges"
    EARN_ACHIEVEMENTS = "earn_achievements"

# Association table for many-to-many relationship between roles and permissions
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permissions.id'), primary_key=True)
)

# Association table for many-to-many relationship between users and roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('roles.id'), primary_key=True),
    Column('assigned_at', DateTime, default=datetime.utcnow),
    Column('assigned_by', Integer, ForeignKey('users.id'))
)

class Role(Base):
    __tablename__ = "roles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text)
    is_system_role = Column(Boolean, default=False)  # System roles cannot be deleted
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    permissions = relationship("PermissionModel", secondary=role_permissions, back_populates="roles")
    users = relationship("User", secondary=user_roles, back_populates="roles")

class PermissionModel(Base):
    __tablename__ = "permissions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(150), nullable=False)
    description = Column(Text)
    category = Column(String(50))  # Group related permissions
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")

class UserRoleAssignment(Base):
    __tablename__ = "user_role_assignments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    assigned_by = Column(Integer, ForeignKey("users.id"))
    assigned_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)  # Optional expiration for temporary roles
    is_active = Column(Boolean, default=True)
    context_data = Column(JSONB)  # Additional context (e.g., community_id for community manager)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    role = relationship("Role")
    assigned_by_user = relationship("User", foreign_keys=[assigned_by])

class AccessLog(Base):
    __tablename__ = "access_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"))
    endpoint = Column(String(255))
    method = Column(String(10))
    permission_required = Column(String(100))
    access_granted = Column(Boolean)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

@dataclass
class UserPermissions:
    user_id: int
    roles: List[str]
    permissions: Set[str]
    context_data: Dict[str, Any]

class RBACService:
    """Service for managing roles, permissions, and access control"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self._initialize_system_roles()
    
    def _initialize_system_roles(self):
        """Initialize default system roles and permissions"""
        # Define role-permission mappings
        role_permissions_map = {
            UserRole.PROSUMER: [
                Permission.CREATE_ENERGY_OFFER,
                Permission.VIEW_ENERGY_OFFERS,
                Permission.PURCHASE_ENERGY,
                Permission.MANAGE_OWN_TRADES,
                Permission.VIEW_TRADING_HISTORY,
                Permission.JOIN_COMMUNITY,
                Permission.CREATE_COMMUNITY,
                Permission.VIEW_PERSONAL_ANALYTICS,
                Permission.REGISTER_IOT_DEVICE,
                Permission.MANAGE_OWN_DEVICES,
                Permission.VIEW_DEVICE_DATA,
                Permission.VIEW_LEADERBOARDS,
                Permission.PARTICIPATE_CHALLENGES,
                Permission.EARN_ACHIEVEMENTS,
            ],
            UserRole.CONSUMER: [
                Permission.VIEW_ENERGY_OFFERS,
                Permission.PURCHASE_ENERGY,
                Permission.MANAGE_OWN_TRADES,
                Permission.VIEW_TRADING_HISTORY,
                Permission.JOIN_COMMUNITY,
                Permission.VIEW_PERSONAL_ANALYTICS,
                Permission.REGISTER_IOT_DEVICE,
                Permission.MANAGE_OWN_DEVICES,
                Permission.VIEW_DEVICE_DATA,
                Permission.VIEW_LEADERBOARDS,
                Permission.PARTICIPATE_CHALLENGES,
                Permission.EARN_ACHIEVEMENTS,
            ],
            UserRole.COMMUNITY_MANAGER: [
                Permission.VIEW_ENERGY_OFFERS,
                Permission.PURCHASE_ENERGY,
                Permission.MANAGE_OWN_TRADES,
                Permission.VIEW_TRADING_HISTORY,
                Permission.JOIN_COMMUNITY,
                Permission.CREATE_COMMUNITY,
                Permission.MANAGE_COMMUNITY,
                Permission.MODERATE_COMMUNITY,
                Permission.VIEW_PERSONAL_ANALYTICS,
                Permission.VIEW_COMMUNITY_ANALYTICS,
                Permission.REGISTER_IOT_DEVICE,
                Permission.MANAGE_OWN_DEVICES,
                Permission.VIEW_DEVICE_DATA,
                Permission.VIEW_LEADERBOARDS,
                Permission.PARTICIPATE_CHALLENGES,
                Permission.EARN_ACHIEVEMENTS,
            ],
            UserRole.GRID_OPERATOR: [
                Permission.VIEW_ENERGY_OFFERS,
                Permission.VIEW_TRADING_HISTORY,
                Permission.VIEW_COMMUNITY_ANALYTICS,
                Permission.VIEW_GRID_ANALYTICS,
                Permission.VIEW_MARKET_ANALYTICS,
                Permission.VIEW_DEVICE_DATA,
                Permission.CONTROL_GRID_DEVICES,
                Permission.EMERGENCY_CONTROLS,
                Permission.GENERATE_REPORTS,
            ],
            UserRole.REGULATOR: [
                Permission.VIEW_TRADING_HISTORY,
                Permission.VIEW_GRID_ANALYTICS,
                Permission.VIEW_MARKET_ANALYTICS,
                Permission.AUDIT_TRANSACTIONS,
                Permission.GENERATE_REPORTS,
                Permission.REGULATORY_OVERSIGHT,
                Permission.VIEW_SYSTEM_LOGS,
            ],
            UserRole.ADMIN: list(Permission),  # Admin has all permissions
        }
        
        # Create permissions if they don't exist
        for permission in Permission:
            existing_perm = self.db.query(PermissionModel).filter(
                PermissionModel.name == permission.value
            ).first()
            
            if not existing_perm:
                perm = PermissionModel(
                    name=permission.value,
                    display_name=permission.value.replace('_', ' ').title(),
                    description=f"Permission to {permission.value.replace('_', ' ')}",
                    category=self._get_permission_category(permission)
                )
                self.db.add(perm)
        
        # Create roles if they don't exist
        for role_enum, perms in role_permissions_map.items():
            existing_role = self.db.query(Role).filter(
                Role.name == role_enum.value
            ).first()
            
            if not existing_role:
                role = Role(
                    name=role_enum.value,
                    display_name=role_enum.value.replace('_', ' ').title(),
                    description=f"System role for {role_enum.value.replace('_', ' ')}",
                    is_system_role=True
                )
                
                # Add permissions to role
                for perm_enum in perms:
                    perm = self.db.query(PermissionModel).filter(
                        PermissionModel.name == perm_enum.value
                    ).first()
                    if perm:
                        role.permissions.append(perm)
                
                self.db.add(role)
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            print(f"Error initializing system roles: {e}")
    
    def _get_permission_category(self, permission: Permission) -> str:
        """Categorize permissions for better organization"""
        if 'energy' in permission.value or 'trading' in permission.value:
            return 'Energy Trading'
        elif 'community' in permission.value:
            return 'Community Management'
        elif 'analytics' in permission.value:
            return 'Analytics & Reporting'
        elif 'device' in permission.value or 'iot' in permission.value:
            return 'IoT & Devices'
        elif 'system' in permission.value or 'admin' in permission.value:
            return 'System Administration'
        elif 'audit' in permission.value or 'regulatory' in permission.value:
            return 'Compliance & Auditing'
        else:
            return 'General'
    
    async def assign_role_to_user(self, user_id: int, role_name: str, assigned_by: int = None, 
                                 context_data: Dict[str, Any] = None, expires_at: datetime = None) -> bool:
        """Assign a role to a user"""
        try:
            role = self.db.query(Role).filter(Role.name == role_name).first()
            if not role:
                return False
            
            # Check if user already has this role
            existing = self.db.query(UserRoleAssignment).filter(
                UserRoleAssignment.user_id == user_id,
                UserRoleAssignment.role_id == role.id,
                UserRoleAssignment.is_active == True
            ).first()
            
            if existing:
                return False
            
            assignment = UserRoleAssignment(
                user_id=user_id,
                role_id=role.id,
                assigned_by=assigned_by,
                expires_at=expires_at,
                context_data=context_data
            )
            
            self.db.add(assignment)
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"Error assigning role: {e}")
            return False
    
    async def remove_role_from_user(self, user_id: int, role_name: str) -> bool:
        """Remove a role from a user"""
        try:
            role = self.db.query(Role).filter(Role.name == role_name).first()
            if not role:
                return False
            
            assignment = self.db.query(UserRoleAssignment).filter(
                UserRoleAssignment.user_id == user_id,
                UserRoleAssignment.role_id == role.id,
                UserRoleAssignment.is_active == True
            ).first()
            
            if assignment:
                assignment.is_active = False
                self.db.commit()
                return True
            
            return False
            
        except Exception as e:
            self.db.rollback()
            print(f"Error removing role: {e}")
            return False
    
    async def get_user_permissions(self, user_id: int) -> UserPermissions:
        """Get all permissions for a user based on their roles"""
        assignments = self.db.query(UserRoleAssignment).filter(
            UserRoleAssignment.user_id == user_id,
            UserRoleAssignment.is_active == True
        ).join(Role).all()
        
        roles = []
        permissions = set()
        context_data = {}
        
        for assignment in assignments:
            # Check if role is not expired
            if assignment.expires_at and assignment.expires_at < datetime.utcnow():
                assignment.is_active = False
                continue
            
            role = assignment.role
            roles.append(role.name)
            
            # Collect permissions from this role
            for perm in role.permissions:
                permissions.add(perm.name)
            
            # Merge context data
            if assignment.context_data:
                context_data.update(assignment.context_data)
        
        return UserPermissions(
            user_id=user_id,
            roles=roles,
            permissions=permissions,
            context_data=context_data
        )
    
    async def check_permission(self, user_id: int, permission: Permission, 
                             context: Dict[str, Any] = None) -> bool:
        """Check if a user has a specific permission"""
        user_perms = await self.get_user_permissions(user_id)
        
        if permission.value not in user_perms.permissions:
            return False
        
        # Context-specific checks
        if context and permission in [Permission.MANAGE_COMMUNITY, Permission.MODERATE_COMMUNITY]:
            # Community-specific permissions
            community_id = context.get('community_id')
            if community_id:
                # Check if user is manager of this specific community
                managed_communities = user_perms.context_data.get('managed_communities', [])
                return community_id in managed_communities
        
        return True
    
    async def log_access_attempt(self, user_id: int, endpoint: str, method: str, 
                                permission_required: str, access_granted: bool,
                                ip_address: str = None, user_agent: str = None):
        """Log access attempts for auditing"""
        try:
            log_entry = AccessLog(
                user_id=user_id,
                endpoint=endpoint,
                method=method,
                permission_required=permission_required,
                access_granted=access_granted,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            self.db.add(log_entry)
            self.db.commit()
            
        except Exception as e:
            print(f"Error logging access attempt: {e}")

# FastAPI Dependencies and Decorators

security = HTTPBearer()

def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """Extract user ID from JWT token"""
    try:
        # This would integrate with your existing JWT authentication
        # For now, return a mock user ID
        token = credentials.credentials
        # payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        # return payload.get("user_id")
        return 1  # Mock user ID
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def require_permission(permission: Permission, context_key: str = None):
    """Decorator to require specific permission for API endpoints"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user_id from dependencies
            user_id = kwargs.get('current_user_id') or get_current_user_id()
            
            # Get RBAC service from dependencies
            rbac_service = kwargs.get('rbac_service')
            if not rbac_service:
                # Initialize RBAC service if not provided
                from app.core.database import get_db
                db = next(get_db())
                rbac_service = RBACService(db)
            
            # Extract context if needed
            context = {}
            if context_key and context_key in kwargs:
                context[context_key] = kwargs[context_key]
            
            # Check permission
            has_permission = await rbac_service.check_permission(user_id, permission, context)
            
            if not has_permission:
                await rbac_service.log_access_attempt(
                    user_id=user_id,
                    endpoint=func.__name__,
                    method="API",
                    permission_required=permission.value,
                    access_granted=False
                )
                
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient permissions. Required: {permission.value}"
                )
            
            # Log successful access
            await rbac_service.log_access_attempt(
                user_id=user_id,
                endpoint=func.__name__,
                method="API",
                permission_required=permission.value,
                access_granted=True
            )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

def require_role(role: UserRole):
    """Decorator to require specific role for API endpoints"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get('current_user_id') or get_current_user_id()
            
            rbac_service = kwargs.get('rbac_service')
            if not rbac_service:
                from app.core.database import get_db
                db = next(get_db())
                rbac_service = RBACService(db)
            
            user_perms = await rbac_service.get_user_permissions(user_id)
            
            if role.value not in user_perms.roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. Required role: {role.value}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator

# Role-specific dashboard configurations
class DashboardConfig:
    """Configuration for role-specific dashboards"""
    
    @staticmethod
    def get_dashboard_config(role: UserRole) -> Dict[str, Any]:
        """Get dashboard configuration for a specific role"""
        configs = {
            UserRole.PROSUMER: {
                'sections': [
                    'energy_production',
                    'energy_consumption', 
                    'trading_activity',
                    'earnings_summary',
                    'device_status',
                    'community_overview',
                    'achievements',
                    'market_opportunities'
                ],
                'widgets': [
                    'production_chart',
                    'consumption_chart',
                    'earnings_widget',
                    'trading_widget',
                    'device_grid',
                    'weather_widget',
                    'leaderboard_widget'
                ],
                'permissions': [p.value for p in [
                    Permission.CREATE_ENERGY_OFFER,
                    Permission.VIEW_ENERGY_OFFERS,
                    Permission.PURCHASE_ENERGY,
                    Permission.VIEW_PERSONAL_ANALYTICS
                ]]
            },
            UserRole.CONSUMER: {
                'sections': [
                    'energy_consumption',
                    'trading_activity',
                    'cost_savings',
                    'device_status',
                    'community_overview',
                    'achievements',
                    'market_browse'
                ],
                'widgets': [
                    'consumption_chart',
                    'savings_widget',
                    'trading_widget',
                    'device_grid',
                    'market_widget',
                    'efficiency_tips'
                ],
                'permissions': [p.value for p in [
                    Permission.VIEW_ENERGY_OFFERS,
                    Permission.PURCHASE_ENERGY,
                    Permission.VIEW_PERSONAL_ANALYTICS
                ]]
            },
            UserRole.COMMUNITY_MANAGER: {
                'sections': [
                    'community_overview',
                    'member_management',
                    'energy_flows',
                    'performance_metrics',
                    'events_challenges',
                    'dispute_resolution',
                    'analytics_reports'
                ],
                'widgets': [
                    'community_stats',
                    'member_activity',
                    'energy_flow_diagram',
                    'performance_charts',
                    'activity_feed',
                    'alerts_widget'
                ],
                'permissions': [p.value for p in [
                    Permission.MANAGE_COMMUNITY,
                    Permission.MODERATE_COMMUNITY,
                    Permission.VIEW_COMMUNITY_ANALYTICS
                ]]
            },
            UserRole.GRID_OPERATOR: {
                'sections': [
                    'grid_overview',
                    'load_monitoring',
                    'equipment_status',
                    'emergency_controls',
                    'maintenance_schedule',
                    'performance_reports',
                    'alerts_incidents'
                ],
                'widgets': [
                    'grid_topology',
                    'load_charts',
                    'equipment_grid',
                    'alert_dashboard',
                    'performance_metrics',
                    'weather_impact'
                ],
                'permissions': [p.value for p in [
                    Permission.VIEW_GRID_ANALYTICS,
                    Permission.CONTROL_GRID_DEVICES,
                    Permission.EMERGENCY_CONTROLS
                ]]
            },
            UserRole.REGULATOR: {
                'sections': [
                    'compliance_overview',
                    'audit_reports',
                    'transaction_monitoring',
                    'market_surveillance',
                    'regulatory_filings',
                    'investigation_tools',
                    'system_health'
                ],
                'widgets': [
                    'compliance_dashboard',
                    'audit_summary',
                    'transaction_analysis',
                    'market_metrics',
                    'alerts_violations',
                    'report_generator'
                ],
                'permissions': [p.value for p in [
                    Permission.AUDIT_TRANSACTIONS,
                    Permission.REGULATORY_OVERSIGHT,
                    Permission.GENERATE_REPORTS
                ]]
            }
        }
        
        return configs.get(role, {})

# Export classes and functions
__all__ = [
    'UserRole', 'Permission', 'Role', 'PermissionModel', 'UserRoleAssignment', 'AccessLog',
    'RBACService', 'UserPermissions', 'DashboardConfig',
    'require_permission', 'require_role', 'get_current_user_id'
]
