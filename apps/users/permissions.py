from rest_framework import permissions


class IsWaitress(permissions.BasePermission):
    message = 'You must be a waitress to access this endpoint.'

    def has_permission(self, request, view):
        return request.user.type == 'waitress'


class IsAdmin(permissions.BasePermission):
    message = 'You must be an admin to access this endpoint.'

    def has_permission(self, request, view):
        return request.user.type == 'admin'


class IsRestaurantOwner(permissions.BasePermission):
    message = 'You must be a restaurant owner to access this endpoint.'

    def has_permission(self, request, view):
        return request.user.type == 'restaurant'


class IsWaitressOrAdmin(permissions.BasePermission):
    message = 'You must be a waitress or admin to access this endpoint.'

    def has_permission(self, request, view):
        return request.user.type in ['waitress', 'admin']

