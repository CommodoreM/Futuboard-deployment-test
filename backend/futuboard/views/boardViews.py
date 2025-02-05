from django.http import Http404
import jwt
from rest_framework.decorators import api_view
from django.http import JsonResponse
from ..models import Board
from ..serializers import BoardSerializer
import rest_framework.request
from django.utils import timezone
from ..verification import (
    encode_token,
    hash_password,
    verify_password,
    token_access_failed,
)


# Create your views here.
@api_view(["GET", "POST"])
def all_boards(request: rest_framework.request.Request, format=None):
    if request.method == "POST":
        new_board = Board(
            description="",
            title=request.data["title"],
            creation_date=timezone.now(),
            passwordhash=hash_password(request.data["password"]),
            salt="",
        )
        new_board.save()

        serializer = BoardSerializer(new_board)
        return JsonResponse(serializer.data, safe=False)

    if request.method == "GET":
        query_set = Board.objects.all()
        serializer = BoardSerializer(query_set, many=True)
        return JsonResponse(serializer.data, safe=False)


@api_view(["GET", "POST", "PUT", "DELETE"])
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
            if result := token_access_failed(board_id, request):
                return result

            board = Board.objects.get(pk=board_id)
            serializer = BoardSerializer(board)
            return JsonResponse(serializer.data, safe=False)

        except Board.DoesNotExist:
            raise Http404("Board does not exist")
        except jwt.ExpiredSignatureError:
            return JsonResponse({"message": "Access token expired"}, status=401)
        except jwt.InvalidTokenError:
            return JsonResponse({"message": "Access token invalid"}, status=401)

    if request.method == "PUT":
        try:
            if result := token_access_failed(board_id, request):
                return result

            board = Board.objects.get(pk=board_id)
            board.background_color = request.data.get("background_color", board.background_color)
            board.save()

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
            board.delete()
            return JsonResponse({"message": "Board deleted successfully"}, status=200)
        except:  # noqa: E722
            raise Http404("Board deletion failed")


@api_view(["PUT"])
def update_board_title(request, board_id):
    try:
        if result := token_access_failed(board_id, request):
            return result

        board = Board.objects.get(pk=board_id)
        board.title = request.data.get("title", board.title)
        board.save()

        serializer = BoardSerializer(board)
        return JsonResponse(serializer.data, safe=False)

    except Board.DoesNotExist:
        raise Http404("Board does not exist")
    except jwt.ExpiredSignatureError:
        return JsonResponse({"message": "Access token expired"}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({"message": "Access token invalid"}, status=401)
    except Exception:
        return JsonResponse({"message": "An unexpected error occurred"}, status=500)


@api_view(["PUT"])
def update_board_password(request, board_id):
    try:
        if result := token_access_failed(board_id, request):
            return result

        board = Board.objects.get(pk=board_id)

        if not verify_password(request.data["old_password"], board.passwordhash):
            return JsonResponse({"message": "Wrong old password"}, status=401)

        candidate_password = request.data["new_password"]
        confirm_password = request.data["confirm_password"]

        if candidate_password != confirm_password:
            return JsonResponse({"message": "Passwords do not match"}, status=400)

        board.passwordhash = hash_password(candidate_password)
        board.save()

        serializer = BoardSerializer(board)
        return JsonResponse(serializer.data, safe=False)

    except Board.DoesNotExist:
        raise Http404("Board does not exist")
    except jwt.ExpiredSignatureError:
        return JsonResponse({"message": "Access token expired"}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({"message": "Access token invalid"}, status=401)
    except Exception:
        return JsonResponse({"message": "An unexpected error occurred"}, status=500)


@api_view(["PUT"])
def update_ticket_template(request, board_id):
    try:
        if result := token_access_failed(board_id, request):
            return result

        board = Board.objects.get(pk=board_id)
        board.default_ticket_title = request.data.get("title", board.default_ticket_title)
        board.default_ticket_description = request.data.get("description", board.default_ticket_description)
        board.default_ticket_color = request.data.get("color", board.default_ticket_color)
        board.default_ticket_storypoints = request.data.get("storypoints", board.default_ticket_storypoints)
        board.default_ticket_size = request.data.get("size", board.default_ticket_size)
        board.default_ticket_cornernote = request.data.get("cornernote", board.default_ticket_cornernote)
        board.save()

        serializer = BoardSerializer(board)
        return JsonResponse(serializer.data, safe=False)

    except Board.DoesNotExist:
        raise Http404("Board does not exist")
    except jwt.ExpiredSignatureError:
        return JsonResponse({"message": "Access token expired"}, status=401)
    except jwt.InvalidTokenError:
        return JsonResponse({"message": "Access token invalid"}, status=401)
    except Exception:
        return JsonResponse({"message": "An unexpected error occurred"}, status=500)
