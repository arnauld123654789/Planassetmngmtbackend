"""
Role-Based Access Control (RBAC) Utilities

Centralized role checking for multi-role support across the application.
"""

from typing import List
from app.models.enums import UserRole


class RoleChecker:
    """
    Centralized role checking utility for multi-role support.
    
    Handles users with multiple roles (e.g., ["IT Admin", "Logistician", "Verificator"])
    and ensures privilege accumulation from all assigned roles.
    """
    
    @staticmethod
    def has_role(user_roles: List[str], required_role: UserRole) -> bool:
        """
        Check if user has a specific role.
        
        Handles both:
        - Clean role arrays: ["IT Admin", "Logistician"]
        - Legacy comma-delimited: ["IT Admin, Supply Chain Manager"]
        
        Args:
            user_roles: List of role strings from user.roles
            required_role: The UserRole enum value to check
            
        Returns:
            True if user has the required role
            
        Example:
            >>> RoleChecker.has_role(["IT Admin", "Logistician"], UserRole.IT_ADMIN)
            True
            >>> RoleChecker.has_role(["Verificator"], UserRole.IT_ADMIN)
            False
        """
        if not user_roles:
            return False
            
        role_value = required_role.value
        return any(
            role_value == role or role_value in str(role)
            for role in user_roles
        )
    
    @staticmethod
    def has_any_role(user_roles: List[str], required_roles: List[UserRole]) -> bool:
        """
        Check if user has ANY of the required roles.
        
        This is the most common check for permission gates that allow
        multiple roles (e.g., "IT Admin OR Supply Chain Manager").
        
        Args:
            user_roles: List of role strings from user.roles
            required_roles: List of UserRole enums to check
            
        Returns:
            True if user has at least one of the required roles
            
        Example:
            >>> RoleChecker.has_any_role(
            ...     ["IT Admin", "Logistician"],
            ...     [UserRole.IT_ADMIN, UserRole.SUPPLY_CHAIN_MANAGER]
            ... )
            True
            >>> RoleChecker.has_any_role(
            ...     ["Verificator"],
            ...     [UserRole.IT_ADMIN, UserRole.SUPPLY_CHAIN_MANAGER]
            ... )
            False
        """
        if not user_roles:
            return False
            
        return any(
            RoleChecker.has_role(user_roles, required_role)
            for required_role in required_roles
        )
    
    @staticmethod
    def has_all_roles(user_roles: List[str], required_roles: List[UserRole]) -> bool:
        """
        Check if user has ALL of the required roles.
        
        Rare use case - typically you want has_any_role for permission checks.
        
        Args:
            user_roles: List of role strings from user.roles
            required_roles: List of UserRole enums to check
            
        Returns:
            True if user has all required roles
            
        Example:
            >>> RoleChecker.has_all_roles(
            ...     ["IT Admin", "Logistician"],
            ...     [UserRole.IT_ADMIN, UserRole.LOGISTICIAN]
            ... )
            True
        """
        if not user_roles:
            return False
            
        return all(
            RoleChecker.has_role(user_roles, required_role)
            for required_role in required_roles
        )
    
    @staticmethod
    def is_admin(user_roles: List[str]) -> bool:
        """
        Convenience method to check if user is an IT Admin.
        
        Args:
            user_roles: List of role strings from user.roles
            
        Returns:
            True if user has IT Admin role
        """
        return RoleChecker.has_role(user_roles, UserRole.IT_ADMIN)
    
    @staticmethod
    def is_scm(user_roles: List[str]) -> bool:
        """
        Convenience method to check if user is a Supply Chain Manager.
        
        Args:
            user_roles: List of role strings from user.roles
            
        Returns:
            True if user has Supply Chain Manager role
        """
        return RoleChecker.has_role(user_roles, UserRole.SUPPLY_CHAIN_MANAGER)
    
    @staticmethod
    def can_manage(user_roles: List[str]) -> bool:
        """
        Check if user has management privileges (IT Admin OR Supply Chain Manager).
        
        This is a common check for administrative operations.
        
        Args:
            user_roles: List of role strings from user.roles
            
        Returns:
            True if user has management privileges
        """
        return RoleChecker.has_any_role(
            user_roles,
            [UserRole.IT_ADMIN, UserRole.SUPPLY_CHAIN_MANAGER]
        )
