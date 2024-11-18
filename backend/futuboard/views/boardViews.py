from django.http import Http404
import jwt
from rest_framework.decorators import api_view
from django.http import JsonResponse
from ..models import Board, Column, Ticket, Usergroup, UsergroupUser, Swimlanecolumn, Action
from ..serializers import BoardSerializer
import rest_framework.request
from django.utils import timezone
from ..verification import decode_token, encode_token, get_token_from_request, new_password, verify_password


# Create your views here.
@api_view(["GET", "POST"])
def all_boards(request: rest_framework.request.Request, format=None):
    if request.method == "POST":
        try:
            new_board = Board(
                boardid=request.data["id"],
                description="",
                title=request.data["title"],
                creator="",
                creation_date=timezone.now(),
                passwordhash=new_password(request.data["password"]),
                salt="",
            )
            new_board.save()

            new_usergroup = Usergroup(boardid=new_board, type="board")
            new_usergroup.save()

            serializer = BoardSerializer(new_board)
            return JsonResponse(serializer.data, safe=False)
        except:  # noqa: E722
            raise Http404("Cannot create Board")
    if request.method == "GET":
        query_set = Board.objects.all()
        serializer = BoardSerializer(query_set, many=True)
        return JsonResponse(serializer.data, safe=False)


@api_view(["GET", "POST", "DELETE"])
def board_by_id(request, board_id):
    if request.method == "POST":
        # Get password from request
        password = request.data["password"]

        # Get board from database
        try:
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            raise Http404("Board does not exist")
        # verify password
        if verify_password(password, board.passwordhash):
            token = encode_token(board.boardid)
            return JsonResponse({"success": True, "token": token})
        else:
            return JsonResponse({"success": False})
    if request.method == "GET":
        try:
            token = get_token_from_request(request)
            if token is None:
                return JsonResponse({"message": "Access token missing"}, status=401)

            decoded_token = decode_token(token)

            if decoded_token["board_id"] != str(board_id):
                return JsonResponse({"message": "Access token to wrong board"}, status=405)

            board = Board.objects.get(pk=board_id)
            serializer = BoardSerializer(board)
            return JsonResponse(serializer.data, safe=False)

        except Board.DoesNotExist:
            raise Http404("Board does not exist")
        except jwt.ExpiredSignatureError:
            return JsonResponse({"message": "Access token expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"message": "Access token invalid"}, status=401)

    if request.method == "DELETE":
        try:
            board = Board.objects.get(pk=board_id)
            # delete users in the board.
            usergroup = Usergroup.objects.get(boardid=board.boardid)
            usergroupuser = UsergroupUser.objects.filter(usergroupid=usergroup.usergroupid)
            users = [group.userid for group in usergroupuser]
            for user in users:
                user.delete()

            # delete magnets in tickets and actions.
            columns = Column.objects.filter(boardid=board)
            for column in columns:
                swimlanecolumns = Swimlanecolumn.objects.filter(columnid=column)
                for swimlanecolumn in swimlanecolumns:
                    actions = Action.objects.filter(swimlanecolumnid=swimlanecolumn.swimlanecolumnid)
                    for action in actions:
                        usergroup = Usergroup.objects.get(actionid=action.actionid)
                        usergroupuser = UsergroupUser.objects.filter(usergroupid=usergroup)
                        users = [group.userid for group in usergroupuser]
                        for user in users:
                            user.delete()

                tickets = Ticket.objects.filter(columnid=column)
                for ticket in tickets:
                    usergroup = Usergroup.objects.get(ticketid=ticket.ticketid)
                    usergroupuser = UsergroupUser.objects.filter(usergroupid=usergroup)
                    users = [group.userid for group in usergroupuser]
                    for user in users:
                        user.delete()

            board.delete()
            return JsonResponse({"message": "Board deleted successfully"}, status=200)
        except:  # noqa: E722
            raise Http404("Board deletion failed")
