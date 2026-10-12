def should_forward(item, config):
    f = config.get("filters", {})
    text = item.get("text", "")
    cs = bool(f.get("case_sensitive", False))
    hay = text if cs else text.casefold()
    include = [x if cs else x.casefold() for x in f.get("include_text", [])]
    exclude = [x if cs else x.casefold() for x in f.get("exclude_text", [])]
    mode = f.get("match_mode", "any")
    if include and mode == "all" and not all(x in hay for x in include):
        return False
    if include and mode == "any" and not any(x in hay for x in include):
        return False
    return not any(x in hay for x in exclude)
