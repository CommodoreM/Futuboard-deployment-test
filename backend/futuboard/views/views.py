from django.http import Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from ..models import Board, Column, Ticket, Usergroup, User, UsergroupUser, Swimlanecolumn
from ..serializers import BoardSerializer, ColumnSerializer, TicketSerializer, UserSerializer
import rest_framework.request
from django.utils import timezone
from ..verification import new_password, verify_password
import uuid

# Create your views here.
@api_view(['GET', 'POST'])
def get_all_boards(request: rest_framework.request.Request, format=None):
    if request.method == 'POST':
        print(request.data['id'])
        try:
            new_board = Board(boardid = request.data['id'],
                              description = '',
                            title = request.data['title'],
                            creator = '',
                            creation_date = timezone.now(),
                            passwordhash = new_password(request.data['password']),
                            salt = '')
            new_board.save()

            new_usergroup = Usergroup(boardid = new_board, type = 'board')
            new_usergroup.save()

            serializer = BoardSerializer(new_board)
            return JsonResponse(serializer.data, safe=False)
        except:
            raise Http404("Cannot create Board")
    if request.method == 'GET':
        query_set = Board.objects.all()
        serializer = BoardSerializer(query_set, many=True)
        return JsonResponse(serializer.data, safe=False)

@api_view(['GET', 'POST'])
def get_board_by_id(request, board_id):
    if request.method == 'POST':
        # Get password from request
        password = request.data['password']
        # Get board from database
        try:
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            raise Http404("Board does not exist")
        # verify password
        if verify_password(password, board_id, board.passwordhash):
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})        
    if request.method == 'GET':
        try:
            board = Board.objects.get(pk=board_id)
            serializer = BoardSerializer(board)
            return JsonResponse(serializer.data, safe=False)

            # TODO: only return the board if the user is authorized
            # (password is empty of the user has entered the password previously)

            # if verify_password("", board_id, board.passwordhash):
            #     serializer = BoardSerializer(board)
            #     return JsonResponse(serializer.data, safe=False)
            # else:
            #     # return a 401 if the user does not have access to the board   
            #     return HttpResponse(status=401)
        except Board.DoesNotExist:
            raise Http404("Board does not exist")

@api_view(['GET', 'POST'])
def get_columns_from_board(request, board_id):
    if request.method == 'GET':
        try:
            query_set = Column.objects.filter(boardid=board_id).order_by('ordernum')
        except Board.DoesNotExist:
            raise Http404("Column does not exist") 
        serializer = ColumnSerializer(query_set, many=True)
        return JsonResponse(serializer.data, safe=False)
    if request.method == 'POST':
        try:
            length = len(Column.objects.filter(boardid=board_id))
            new_column = Column(
                columnid = request.data['columnid'],
                boardid = Board.objects.get(pk=board_id),
                wip_limit = 0,
                color = '',
                description = '',
                title = request.data['title'],
                ordernum = length,
                creation_date = timezone.now(),
                swimlane = request.data['swimlane'],
                )
            new_column.save()
            if request.data['swimlane']:
                defaultSwimlaneNames = ["To Do", "Doing", "Verify", "Done"]
                for name in defaultSwimlaneNames:
                    swimlanecolumn = Swimlanecolumn(
                        columnid = Column.objects.get(pk=request.data['columnid']),
                        color = "white",
                        title = name,
                        ordernum = defaultSwimlaneNames.index(name)
                    )
                    swimlanecolumn.save()
            serializer = ColumnSerializer(new_column)
            return JsonResponse(serializer.data, safe=False)
        except:
            print("Column creation failed")
            raise Http404("Column creation failed")

@api_view(['GET', 'POST', 'PUT'])
def get_tickets_from_column(request, board_id, column_id):
    if request.method == 'PUT':
        try:
            tickets_data = request.data

            # if ticket has a columnid that is not the same as the columnid from the ticket in the database, change it
            for ticket in tickets_data:
                ticket_from_database = Ticket.objects.get(ticketid=ticket['ticketid'])
                if ticket_from_database.columnid != Column.objects.get(pk=column_id):
                    ticket_from_database.columnid = Column.objects.get(pk=column_id)
                    ticket_from_database.save()
                    
            #update order of tickets
            for index, ticket_data in enumerate(tickets_data):
                task = Ticket.objects.get(ticketid=ticket_data['ticketid'])
                task.order = index
                task.save()

            return JsonResponse({"message": "Tasks order updated successfully"}, status=200)
        except Ticket.DoesNotExist:
            raise Http404("Task does not exist")
        except:
            raise Http404("Error updating tasks order.")
    if request.method == 'POST':
        try:
            length = len(Ticket.objects.filter(columnid=column_id))
            new_ticket = Ticket(
                ticketid = request.data['ticketid'],
                columnid = Column.objects.get(pk=column_id),
                title = request.data['title'],
                description = request.data['description'],
                color = request.data['color'] if "color" in request.data else "white",
                storypoints = 8,
                size = int(request.data['size']) if request.data['size'] else 0,
                order = length,
                creation_date = timezone.now(),
                cornernote = request.data['cornernote'] if "cornernote" in request.data else ""
                )
            
            new_ticket.save()

            new_usergroup = Usergroup(ticketid = new_ticket, type = 'ticket')
            print("NEW USER GROUP")
            print(new_usergroup.usergroupid)
            new_usergroup.save()

            serializer = TicketSerializer(new_ticket)
            return JsonResponse(serializer.data, safe=False)
        except:
            raise Http404("Cannot create Ticket")
    if request.method == 'GET':
        try:
            query_set = Ticket.objects.filter(columnid=column_id).order_by('order')
            serializer = TicketSerializer(query_set, many=True)
            return JsonResponse(serializer.data, safe=False)
        except:
            raise Http404("Error getting tickets.") 
@api_view(['PUT', 'DELETE'])
def update_ticket(request, column_id, ticket_id):
    try:
        ticket = Ticket.objects.get(pk=ticket_id, columnid=column_id)
    except Ticket.DoesNotExist:
        raise Http404("Ticket not found")
    if(request.method == 'DELETE'):
        try:
            usergroup = Usergroup.objects.get(ticketid=ticket_id)
            usergroupuser = UsergroupUser.objects.filter(usergroupid=usergroup)
            users = [group.userid for group in usergroupuser]
            for user in users:
                user.delete()
            ticket.delete()
            return JsonResponse({"message": "Ticket deleted successfully"}, status=200)
        except:
            raise Http404("Cannot delete Ticket")
    
    if request.method == 'PUT':
        try:
            ticket.title = request.data.get('title', ticket.title)
            ticket.description = request.data.get('description', ticket.description)
            ticket.color = request.data.get('color', ticket.color)
            ticket.storypoints = request.data.get('storypoints', ticket.storypoints)
            ticket.size = request.data.get('size', ticket.size)
            ticket.cornernote = request.data.get('cornernote', ticket.cornernote)
            ticket.save()

            serializer = TicketSerializer(ticket)
            return JsonResponse(serializer.data, safe=False)
        except:
            raise Http404("Cannot update Ticket")
        
@api_view(['PUT'])
def update_column(request, board_id, column_id):
    try:
        column = Column.objects.get(pk=column_id, boardid=board_id)
    except Column.DoesNotExist:
        raise Http404("Column not found")

    if request.method == 'PUT':
        try:
            column.title = request.data.get('title', column.title)
            column.save()

            serializer = ColumnSerializer(column)
            return JsonResponse(serializer.data, safe=False)
        except:
            raise Http404("Cannot update Column")

@api_view(['GET', 'POST'])
def get_users_from_board(request, board_id):
    if request.method == 'GET':
        try:
            query_set = Usergroup.objects.get(boardid=board_id)
            query_set2 = UsergroupUser.objects.filter(usergroupid=query_set.usergroupid)
            users = [user.userid for user in query_set2]
            serializer = UserSerializer(users, many=True)
        except Board.DoesNotExist:
            raise Http404("Error getting users") 
        return JsonResponse(serializer.data, safe=False)
    if request.method == 'POST':
        try:
            usergroup = Usergroup.objects.get(boardid=board_id)
            new_user = User(name = request.data['name'],)
            new_user.save()

            new_UsergroupUser = UsergroupUser(usergroupid = usergroup, userid = new_user)
            new_UsergroupUser.save()

            serializer = UserSerializer(new_user)
            return JsonResponse(serializer.data, safe=False)
        except:
            raise Http404("User creation failed")

@api_view(['GET','POST', 'PUT'])
def get_users_from_ticket(request, ticket_id):
    if request.method == 'GET':
        try:
            query_set = Usergroup.objects.get(ticketid=ticket_id)
            query_set2 = UsergroupUser.objects.filter(usergroupid=query_set.usergroupid)
            users = [user.userid for user in query_set2]
            serializer = UserSerializer(users, many=True)
        except Board.DoesNotExist:
            raise Http404("Error getting users") 
        return JsonResponse(serializer.data, safe=False)
    if request.method == 'PUT':
        try: 
            usergroup = Usergroup.objects.get(ticketid=ticket_id)
            query_set2 = UsergroupUser.objects.filter(usergroupid=usergroup)
            users = [user.userid for user in query_set2] #list of users in the new ticket
            if request.data == []:
                query_set2.delete()
            else:
                old_usergroup = UsergroupUser(usergroupid = usergroup, userid = User.objects.get(pk=request.data[0]['userid']))
                old_usergroup.delete()
                for user in request.data:
                    new_usergroup = UsergroupUser(usergroupid = usergroup, userid = User.objects.get(pk=user['userid']))
                    new_usergroup.save()

        except:
            raise Http404("User update failed")
        #TODO: implement
        print("TO BE IMPLEMENTED")
        return JsonResponse({"message": "Users updated successfully"}, status=200)
    if request.method == 'POST': 
        #when a user is dragged to a ticket for the first time, just create a new one with a new userid but same other fields, makes it easier to delete etc
        try:
            usergroup = Usergroup.objects.get(ticketid=ticket_id)
            new_user =  User(name = request.data['name'])
            new_user.save()

            new_UsergroupUser = UsergroupUser(usergroupid = usergroup, userid = new_user)
            new_UsergroupUser.save()

            serializer = UserSerializer(new_user)
            return JsonResponse(serializer.data, safe=False)
        except:
            raise Http404("User creation failed")
        
@api_view(['DELETE'])
def update_user(request, user_id):
    if request.method == 'DELETE':
        try:
            user = User.objects.get(pk=user_id)
            response = u'Successfully deleted user: {}'.format(user_id)
            user.delete()
            return HttpResponse(response)
        except:
            raise Http404("User deletion failed")
        

@api_view(['GET','POST', 'PUT', 'DELETE'])
def get_users_from_ticket(request, ticket_id):
    if request.method == 'GET':
        try:
            query_set = Usergroup.objects.get(ticketid=ticket_id)
            query_set2 = UsergroupUser.objects.filter(usergroupid=query_set.usergroupid)
            users = [user.userid for user in query_set2]
            serializer = UserSerializer(users, many=True)
        except Board.DoesNotExist:
            raise Http404("Error getting users") 
        return JsonResponse(serializer.data, safe=False)
    if request.method == 'PUT':
        try: 
            usergroup = Usergroup.objects.get(ticketid=ticket_id)
            query_set2 = UsergroupUser.objects.filter(usergroupid=usergroup)
            users = [user.userid for user in query_set2] #list of users in the new ticket

            if request.data == []:
                for user in query_set2:
                    user.delete()
                query_set2.delete()
                
            else:
                old_usergroup = UsergroupUser(usergroupid = usergroup, userid = User.objects.get(pk=request.data[0]['userid']))
                old_usergroup.delete()
                for user in query_set2:
                    user.delete()
                
                for user in request.data:
                    new_usergroup = UsergroupUser(usergroupid = usergroup, userid = User.objects.get(pk=user['userid']))
                    new_usergroup.save()

        except:
            raise Http404("User update failed")
        #TODO: implement
        print("TO BE IMPLEMENTED")
        return JsonResponse({"message": "Users updated successfully"}, status=200)
    if request.method == 'POST': 
        #when a user is dragged to a ticket for the first time, just create a new one with a new userid but same other fields, makes it easier to delete etc
        try:
            usergroup = Usergroup.objects.get(ticketid=ticket_id)
            new_user =  User(name = request.data['name'])
            new_user.save()

            new_UsergroupUser = UsergroupUser(usergroupid = usergroup, userid = new_user)
            new_UsergroupUser.save()

            serializer = UserSerializer(new_user)
            return JsonResponse(serializer.data, safe=False)
            
        except:
            raise Http404("User creation failed")
