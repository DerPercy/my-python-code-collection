from django.shortcuts import render
from lib.ui.ui_message import Message
# Create your views here.


def index(request):
    msgList = [Message("Hello message")]
    context = {
        "content": "Hello Content",
        "messages": msgList
    }
    return render(request,"index.html",context)