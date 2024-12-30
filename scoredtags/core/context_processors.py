def top_navbar_search_processor(request):
    top_search_uid = 0
    top_search_vars = {
        "uid": top_search_uid,
        "placeholder_text": "search...",
        "search_item_type": "project",
    }
    return {"top_search_vars": top_search_vars}