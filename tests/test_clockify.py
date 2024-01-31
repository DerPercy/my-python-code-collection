from .context import clockify

def test_parse_description(): 
    """
    Parses a description
    """
    result = clockify.parse_description("T1234: Do something")
    #assert result.get("type") == "Task"
    assert result.get("ticket") == "T1234"
    assert result.get("description") == "Do something"

    result = clockify.parse_description("Do something other")
    #assert result.get("type") == "Task"
    assert result.get("ticket") == ""
    assert result.get("description") == "Do something"