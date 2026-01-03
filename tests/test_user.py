from goodreads_cli.auth.user import parse_current_user


def test_parse_current_user() -> None:
    html = (
        "<script>ReactStores.CurrentUserStore.initializeWith("
        '{"currentUser":{"id":123,"name":"Example User","profileUrl":"https://www.goodreads.com/user/show/123"}});'
        "</script>"
    )
    user = parse_current_user(html)
    assert user is not None
    assert user.user_id == "123"
    assert user.name == "Example User"
    assert user.profile_url == "https://www.goodreads.com/user/show/123"


def test_parse_current_user_missing() -> None:
    html = "<html><body>No user here</body></html>"
    user = parse_current_user(html)
    assert user is None
