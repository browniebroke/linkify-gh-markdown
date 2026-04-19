import re


def linkify(content: str, heading_level: int | None = None) -> str:
    """Add GitHub links to given content."""
    content = remove_html_comments(content)
    content = add_pull_request_links(content)
    content = add_compare_links(content)
    content = add_github_profile_links(content)
    if heading_level is not None:
        content = change_heading_level(content, heading_level)
    return content


def change_heading_level(content: str, top_level: int) -> str:
    """Adjust all heading levels so the topmost heading starts at top_level."""
    lines = content.split("\n")
    in_code_block = False
    heading_levels = []

    for line in lines:
        if line.startswith("```"):
            in_code_block = not in_code_block
        if not in_code_block and line.startswith("#"):
            match = re.match(r"^(#+)", line)
            heading_levels.append(len(match.group(1)))

    if not heading_levels:
        return content

    current_top = min(heading_levels)
    offset = top_level - current_top

    if offset == 0:
        return content

    result_lines = []
    in_code_block = False

    for line in lines:
        if line.startswith("```"):
            in_code_block = not in_code_block
            result_lines.append(line)
            continue
        if not in_code_block and line.startswith("#"):
            match = re.match(r"^(#+)(.*)", line)
            current_level = len(match.group(1))
            new_level = min(current_level + offset, 6)
            line = "#" * new_level + match.group(2)
        result_lines.append(line)

    return "\n".join(result_lines)


def remove_html_comments(content: str) -> str:
    """Remove HTML comments from the given content."""
    return re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)


def get_link_ranges(text: str) -> list[tuple[int, int]]:
    """Get character ranges of existing markdown links."""
    pattern = r"\[[^]]+\]\([^)]+\)"
    return [(m.start(), m.end()) for m in re.finditer(pattern, text)]


def get_code_ranges(text: str) -> list[tuple[int, int]]:
    """Get character ranges of inline code spans."""
    pattern = r"`[^`]+`"
    return [(m.start(), m.end()) for m in re.finditer(pattern, text)]


def add_github_profile_links(content: str) -> str:
    """Convert @username mentions to GitHub profile links."""
    link_ranges = get_link_ranges(content)
    code_ranges = get_code_ranges(content)
    skip_ranges = link_ranges + code_ranges

    def replace(match: re.Match) -> str:
        start, end = match.span()
        username = match.group(1)

        # Skip if inside existing link, code span,
        # or is a decorator like @versioning_class()
        is_inside_skip = any(s <= start < e for s, e in skip_ranges)
        is_decorator = end < len(content) and content[end] == "("

        if is_inside_skip or is_decorator:
            return match.group(0)

        url_username = username.replace("[bot]", "[bot]")
        return f"[@{username}](https://github.com/{url_username})"

    return re.sub(r"@([\w-]+(?:\[bot\])?)", replace, content)


def add_compare_links(content: str) -> str:
    """Convert compare URLs to markdown links in format [tag1...tag2](url)."""
    link_ranges = get_link_ranges(content)

    def replace(match: re.Match) -> str:
        if any(s <= match.start() < e for s, e in link_ranges):
            return match.group(0)
        from_tag = match.group(3)
        to_tag = match.group(4)
        return f"[{from_tag}...{to_tag}]({match.group(0)})"

    return re.sub(
        r"https://github\.com/([\w\-]+)/([\w\-]+)/compare/([\w\.\-]+)\.\.\.([\w\.\-]+)",
        replace,
        content,
    )


def add_pull_request_links(content: str) -> str:
    """Convert pull request URLs to markdown links in format [#NNNN](url)."""
    link_ranges = get_link_ranges(content)

    def replace(match: re.Match) -> str:
        if any(s <= match.start() < e for s, e in link_ranges):
            return match.group(0)
        return f"[#{match.group(3)}]({match.group(0)})"

    return re.sub(
        r"https://github\.com/([\w\-]+)/([\w\-]+)/pull/(\d+)", replace, content
    )
