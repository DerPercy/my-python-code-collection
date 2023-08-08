from .context import todoist

def test_comment_metadata(): 
    assert None == todoist.comment.get_comment_meta_data("Plain text")
    assert None == todoist.comment.get_comment_meta_data("`{ 'a': 'b' }`")
    todoist.comment.get_comment_meta_data("`{ \"a\": \"b\" }`")
    metadata = """`{
        "mm_id": "abcdefg"
    }`"""
    todoist.comment.get_comment_meta_data(metadata)
    