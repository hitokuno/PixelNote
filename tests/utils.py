def assert_with_debug(assertion, res, msg=None):
    try:
        assert assertion
    except AssertionError:
        print("==== DEBUG: status_code:", res.status_code)
        print("==== DEBUG: response body:", res.text)
        if msg:
            print("==== DEBUG:", msg)
        raise
