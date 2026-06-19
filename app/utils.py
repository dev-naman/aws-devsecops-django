def is_owner_or_superuser(request, asset_tracker):
    return request.user == asset_tracker.user or request.user.is_superuser
