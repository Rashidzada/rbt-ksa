from rest_framework.views import APIView
from rest_framework.response import Response
from .services import ChatService

class ChatAPIView(APIView):
    def post(self, request):
        message = request.data.get('message', '')
        context = request.data.get('context', {})
        reply = ChatService.get_reply(message, context=context)
        return Response({"reply": reply})
