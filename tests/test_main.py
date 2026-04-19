from linkify_gh_markdown.main import (
    add_compare_links,
    add_github_profile_links,
    add_pull_request_links,
    change_heading_level,
    get_link_ranges,
    linkify,
    remove_html_comments,
)


class TestGetLinkRanges:
    def test_no_links(self):
        assert get_link_ranges("no links here") == []

    def test_single_link(self):
        text = "see [link](https://example.com) here"
        ranges = get_link_ranges(text)
        assert ranges == [(4, 31)]

    def test_multiple_links(self):
        text = "[a](url1) and [b](url2)"
        ranges = get_link_ranges(text)
        assert len(ranges) == 2


class TestAddGithubProfileLinks:
    def test_simple_mention(self):
        result = add_github_profile_links("Thanks @octocat")
        assert result == "Thanks [@octocat](https://github.com/octocat)"

    def test_multiple_mentions(self):
        result = add_github_profile_links("@alice and @bob")
        assert result == (
            "[@alice](https://github.com/alice) and [@bob](https://github.com/bob)"
        )

    def test_mention_with_hyphen(self):
        result = add_github_profile_links("@my-user")
        assert result == "[@my-user](https://github.com/my-user)"

    def test_bot_mention(self):
        result = add_github_profile_links("@dependabot[bot]")
        assert result == "[@dependabot[bot]](https://github.com/dependabot[bot])"

    def test_skip_existing_link(self):
        text = "[@octocat](https://github.com/octocat)"
        result = add_github_profile_links(text)
        assert result == text

    def test_skip_decorator(self):
        text = "@versioning_class()"
        result = add_github_profile_links(text)
        assert result == text

    def test_no_mentions(self):
        text = "No mentions here."
        result = add_github_profile_links(text)
        assert result == text

    def test_code_fenced_is_ignored(self):
        text = "This is not a username it's some `@api_view` code"
        result = add_github_profile_links(text)
        assert result == text


class TestAddCompareLinks:
    def test_simple_compare_url(self):
        url = "https://github.com/owner/repo/compare/3.2.1...3.1.0"
        result = add_compare_links(url)
        assert result == f"[3.2.1...3.1.0]({url})"

    def test_multiple_compare_urls(self):
        content = (
            "https://github.com/owner/repo/compare/1.0.0...1.1.0 "
            "and https://github.com/owner/repo/compare/2.0.0...2.1.0"
        )
        result = add_compare_links(content)
        assert result == (
            "[1.0.0...1.1.0](https://github.com/owner/repo/compare/1.0.0...1.1.0)"
            " and "
            "[2.0.0...2.1.0](https://github.com/owner/repo/compare/2.0.0...2.1.0)"
        )

    def test_skip_existing_link(self):
        text = (
            "[3.16.1...3.17.0](https://github.com/owner/repo/compare/3.16.1...3.17.0)"
        )
        result = add_compare_links(text)
        assert result == text

    def test_no_compare_urls(self):
        text = "No compare URLs here."
        result = add_compare_links(text)
        assert result == text

    def test_repo_with_hyphens(self):
        url = "https://github.com/my-org/my-repo/compare/v1.0...v2.0"
        result = add_compare_links(url)
        assert result == f"[v1.0...v2.0]({url})"


class TestAddPullRequestLinks:
    def test_simple_pr_url(self):
        url = "https://github.com/owner/repo/pull/123"
        result = add_pull_request_links(url)
        assert result == f"[#123]({url})"

    def test_multiple_pr_urls(self):
        content = (
            "https://github.com/owner/repo/pull/1 "
            "and https://github.com/owner/repo/pull/2"
        )
        result = add_pull_request_links(content)
        assert result == (
            "[#1](https://github.com/owner/repo/pull/1)"
            " and "
            "[#2](https://github.com/owner/repo/pull/2)"
        )

    def test_skip_existing_link(self):
        text = "[#123](https://github.com/owner/repo/pull/123)"
        result = add_pull_request_links(text)
        assert result == text

    def test_no_pr_urls(self):
        text = "No PR URLs here."
        result = add_pull_request_links(text)
        assert result == text

    def test_repo_with_hyphens(self):
        url = "https://github.com/my-org/my-repo/pull/42"
        result = add_pull_request_links(url)
        assert result == f"[#42]({url})"


class TestRemoveHtmlComments:
    def test_single_comment(self):
        result = remove_html_comments("before <!-- comment --> after")
        assert result == "before  after"

    def test_multiline_comment(self):
        result = remove_html_comments("before\n<!-- multi\nline\ncomment -->\nafter")
        assert result == "before\n\nafter"

    def test_multiple_comments(self):
        result = remove_html_comments("a <!-- one --> b <!-- two --> c")
        assert result == "a  b  c"

    def test_no_comments(self):
        result = remove_html_comments("no comments here")
        assert result == "no comments here"

    def test_comment_only(self):
        result = remove_html_comments("<!-- just a comment -->")
        assert result == ""


class TestChangeHeadingLevel:
    def test_no_headings(self):
        text = "No headings here."
        assert change_heading_level(text, 3) == text

    def test_single_heading_increase(self):
        result = change_heading_level("## title\n", 3)
        assert result == "### title\n"

    def test_single_heading_decrease(self):
        result = change_heading_level("### title\n", 2)
        assert result == "## title\n"

    def test_multiple_headings_preserve_hierarchy(self):
        content = "## title\n\n### section 1\nLorem\n\n### section 2\nBlah\n"
        expected = "### title\n\n#### section 1\nLorem\n\n#### section 2\nBlah\n"
        assert change_heading_level(content, 3) == expected

    def test_already_at_target_level(self):
        content = "## title\n\n### section\n"
        assert change_heading_level(content, 2) == content

    def test_headings_capped_at_six(self):
        content = "## title\n\n### section\n"
        result = change_heading_level(content, 6)
        assert result == "###### title\n\n###### section\n"

    def test_heading_in_code_block_not_changed(self):
        content = "## real heading\n\n```\n## not a heading\n```\n"
        result = change_heading_level(content, 3)
        assert result == "### real heading\n\n```\n## not a heading\n```\n"

    def test_h1_input(self):
        result = change_heading_level("# title\n\n## section\n", 2)
        assert result == "## title\n\n### section\n"

    def test_single_heading_increase_by_two(self):
        result = change_heading_level("## title\n", 4)
        assert result == "#### title\n"

    def test_multiple_headings_increase_by_three(self):
        content = "## title\n\n### section 1\nLorem\n\n### section 2\nBlah\n"
        expected = "##### title\n\n###### section 1\nLorem\n\n###### section 2\nBlah\n"
        assert change_heading_level(content, 5) == expected

    def test_h1_increase_by_four(self):
        result = change_heading_level("# title\n\n## section\n\n### subsection\n", 5)
        assert result == "##### title\n\n###### section\n\n###### subsection\n"

    def test_single_heading_decrease_by_two(self):
        result = change_heading_level("#### title\n", 2)
        assert result == "## title\n"

    def test_multiple_headings_decrease_by_three(self):
        content = "#### title\n\n##### section 1\nLorem\n\n##### section 2\nBlah\n"
        expected = "# title\n\n## section 1\nLorem\n\n## section 2\nBlah\n"
        assert change_heading_level(content, 1) == expected

    def test_h4_decrease_by_two_preserve_hierarchy(self):
        result = change_heading_level("#### title\n\n##### section\n\n###### subsection\n", 2)
        assert result == "## title\n\n### section\n\n#### subsection\n"


class TestLinkify:
    def test_linkify(self):
        input_content = "Fixed by @octocat in https://github.com/owner/repo/pull/99\n"

        result = linkify(input_content)

        assert "[@octocat](https://github.com/octocat)" in result
        assert "[#99](https://github.com/owner/repo/pull/99)" in result

    def test_linkify_removes_html_comments(self):
        input_content = "Fixed by @octocat <!-- internal note --> in https://github.com/owner/repo/pull/99\n"

        result = linkify(input_content)

        assert "<!-- internal note -->" not in result
        assert "[@octocat](https://github.com/octocat)" in result
        assert "[#99](https://github.com/owner/repo/pull/99)" in result

    def test_linkify_with_heading_level(self):
        content = "## title\n\nFixed by @octocat\n"
        result = linkify(content, heading_level=3)
        assert result.startswith("### title")
        assert "[@octocat](https://github.com/octocat)" in result

    def test_linkify_without_heading_level_unchanged(self):
        content = "## title\n"
        result = linkify(content)
        assert result.startswith("## title")
