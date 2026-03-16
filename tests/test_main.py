from linkify_gh_markdown.main import (
    add_compare_links,
    add_github_profile_links,
    add_pull_request_links,
    get_link_ranges,
    linkify,
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


class TestLinkify:
    def test_linkify(self):
        input_content = "Fixed by @octocat in https://github.com/owner/repo/pull/99\n"

        result = linkify(input_content)

        assert "[@octocat](https://github.com/octocat)" in result
        assert "[#99](https://github.com/owner/repo/pull/99)" in result
