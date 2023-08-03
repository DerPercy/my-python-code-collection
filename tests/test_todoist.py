from .context import todoist

def test_comment_metadata():
    #assert None == 
    todoist.comment.get_comment_meta_data("Plain text")
    todoist.comment.get_comment_meta_data("`{ 'a': 'b' }`")
    todoist.comment.get_comment_meta_data("`{ \"a\": \"b\" }`")