def normalize_content_type(original_content_type: str):
    if 'multipart' in original_content_type:
        return 'multipart/form-data'
    elif 'x-www-form-urlencoded' in original_content_type:
        return 'application/x-www-form-urlencoded'
    else:
        return 'application/json'
