import pytest
import futuboard.models as md
from rest_framework.test import APIClient
import uuid
from django.urls import reverse
import json
from .test_utils import addBoard, addColumn, addTicket, resetDB
from ..futuboard.verification import verify_password


@pytest.fixture()
def enable_auth_token_checking(settings):
    settings.DISABLE_AUTH_TOKEN_CHECKING = False


############################################################################################################
############################################# VIEW TESTS ###################################################
############################################################################################################


@pytest.mark.django_db
def test_all_boards():
    """
    Test the all_boards function in backend/futuboard/views/boardViews.py
    Has two methods: GET and POST
        GET: Returns all boards
        POST: Creates a new board
    """
    api_client = APIClient()
    # Post 5 boards
    for i in range(5):
        response = api_client.post(
            reverse("all_boards"), {"id": uuid.uuid4(), "title": "board" + str(i), "password": "password" + str(i)}
        )
        assert response.status_code == 200

    assert md.Board.objects.count() == 5
    md.Board.objects.all().delete()
    assert md.Board.objects.count() == 0


@pytest.mark.django_db
def test_board_by_id():
    """
    Test the board_by_id function in backend/futuboard/views/boardViews.py
    Has three methods: GET, POST and DELETE
        GET: Returns a board by id
        POST: Returns a success message if the password is correct
        DELETE: Returns a success message if the board was deleted
    """
    api_client = APIClient()
    # Add 5 boards to the database
    boardids = []
    for i in range(5):
        response = api_client.post(reverse("all_boards"), {"title": "board" + str(i), "password": "password" + str(i)})
        assert response.status_code == 200
        boardids.append(response.json()["boardid"])
    tokens = []
    # Post board by id (Password verification)
    for i in range(5):
        response = api_client.post(reverse("board_by_id", args=[boardids[i]]), {"password": "password" + str(i)})
        data = response.json()
        print(data)
        assert data["success"] is True
        assert data["token"] is not None
        tokens.append(data["token"])
        assert response.status_code == 200
    # Test getting board by id with wrong password
    response = api_client.post(reverse("board_by_id", args=[boardids[0]]), {"password": "wrongpassword"})
    data = response.json()
    print(data)
    assert data["success"] is False
    assert response.status_code == 200
    # Get board by id for all boards
    for i in range(5):
        response = api_client.get(
            reverse("board_by_id", args=[boardids[i]]), headers={"Authorization": f"Bearer {tokens[i]}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["boardid"] == str(boardids[i])
        assert data["title"] == "board" + str(i)
        assert response.status_code == 200
    # Delete a board by id for all boards
    for i in range(5):
        response = api_client.delete(
            reverse("board_by_id", args=[boardids[i]]), headers={"Authorization": f"Bearer {tokens[i]}"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Board deleted successfully"
    # Verify boards are deleted
    for i in range(5):
        response = api_client.get(
            reverse("board_by_id", args=[boardids[i]]), headers={"Authorization": f"Bearer {tokens[i]}"}
        )
        assert response.status_code == 404
    # Ensure no boards are left in the database
    assert md.Board.objects.count() == 0
    # Delete all boards
    resetDB()


@pytest.mark.django_db
def test_get_endpoints_dont_require_auth(enable_auth_token_checking):
    api_client = APIClient()

    creation_response = api_client.post(reverse("all_boards"), {"title": "board", "password": "password"})
    assert creation_response.status_code == 200
    boardid = creation_response.json()["boardid"]

    get_response_unauthenticated = api_client.get(reverse("board_by_id", args=[boardid]))
    assert get_response_unauthenticated.status_code == 200

    get_response_authenticated = api_client.get(reverse("columns_on_board", args=[boardid]))
    assert get_response_authenticated.status_code == 200

    get_response_authenticated = api_client.get(reverse("cumulative_flow", args=[boardid]))
    assert get_response_authenticated.status_code == 200

    get_response_authenticated = api_client.get(reverse("scopes_on_board", args=[boardid]))
    assert get_response_authenticated.status_code == 200


@pytest.mark.django_db
def test_editingh_endpoints_require_auth(enable_auth_token_checking):
    api_client = APIClient()

    creation_response = api_client.post(reverse("all_boards"), {"title": "board", "password": "password"})
    assert creation_response.status_code == 200
    boardid = creation_response.json()["boardid"]

    get_response_authenticated = api_client.post(
        reverse("columns_on_board", args=[boardid]), {"columnid": "1234", "swimlane": False, "title": "title"}
    )
    assert get_response_authenticated.status_code == 401


@pytest.mark.django_db
def test_columns_on_board():
    """
    Test the columns_on_board function in backend/futuboard/views/views.py
    Has two methods: GET and POST
        GET: Returns all columns from a board
        POST: Creates a new column in a board
    """
    api_client = APIClient()
    # Create a board and add 5 columns to it, of which 1 is a swimlane column
    columnids = [uuid.uuid4() for i in range(5)]
    response = api_client.post(reverse("all_boards"), {"title": "board", "password": "password"})
    assert response.status_code == 200
    boardid = response.json()["boardid"]
    # Non-swimlane columns
    for i in range(4):
        # Using json.dumps assures swimlane is a boolean not a string
        data = {"columnid": str(columnids[i]), "title": "column" + str(i), "position": i, "swimlane": False}
        response = api_client.post(
            reverse("columns_on_board", args=[boardid]), data=json.dumps(data), content_type="application/json"
        )
        assert response.status_code == 200

    # Swimlane column
    data = {"columnid": str(columnids[4]), "title": "column4", "position": 4, "swimlane": True}
    response = api_client.post(
        reverse("columns_on_board", args=[boardid]), data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200
    # Get columns from board
    response = api_client.get(reverse("columns_on_board", args=[boardid]))
    data = response.json()
    assert len(data) == 5
    # Make sure there are 4 non-swimlane columns and 1 swimlane column
    assert len([column for column in data if column["swimlane"] is False]) == 4
    assert len([column for column in data if column["swimlane"] is True]) == 1
    assert md.Swimlanecolumn.objects.count() == 4
    assert md.Column.objects.count() == 5
    assert response.status_code == 200
    # Delete all columns
    md.Column.objects.all().delete()
    # Get columns from board
    response = api_client.get(reverse("columns_on_board", args=[boardid]))
    data = response.json()
    assert len(data) == 0
    assert response.status_code == 200

    resetDB()


@pytest.mark.django_db
def test_tickets_on_column():
    """
    Test the tickets_on_column function in backend/futuboard/views/views.py
    Has three methods: GET, POST and PUT
        GET: Returns all tickets from a column
        POST: Creates a new ticket in a column
        PUT: Moves a ticket to a new column and updates the order of the tickets
    """
    api_client = APIClient()
    # Create a board and a column and add 5 tickets to it
    columnid = uuid.uuid4()
    response = api_client.post(reverse("all_boards"), {"title": "board", "password": "password"})
    boardid = response.json()["boardid"]
    assert response.status_code == 200
    data = {"columnid": str(columnid), "title": "column", "position": 0, "swimlane": False}
    response = api_client.post(
        reverse("columns_on_board", args=[boardid]), data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200
    # Add 5 tickets to column
    ticketids = [uuid.uuid4() for i in range(5)]
    for i in range(5):
        data = {
            "ticketid": str(ticketids[i]),
            "title": "ticket" + str(i),
            "description": "description" + str(i),
            "position": i,
            "size": 5,
        }
        response = api_client.post(
            reverse("tickets_on_column", args=[columnid]),
            data=json.dumps(data),
            content_type="application/json",
        )
        assert response.status_code == 200
    # Get tickets from column
    response = api_client.get(reverse("tickets_on_column", args=[columnid]))
    data = response.json()
    assert len(data) == 5
    assert response.status_code == 200
    # Test PUT request to update ticket to a new column
    # Create a new column
    newcolumnid = uuid.uuid4()
    data = {
        "columnid": str(newcolumnid),
        "title": "newcolumn",
        "position": 1,
        "swimlane": False,
    }
    response = api_client.post(
        reverse("columns_on_board", args=[boardid]), data=json.dumps(data), content_type="application/json"
    )
    # List of ticketids to move to new column, move 1st and 4th ticket
    data = [
        {
            "ticketid": str(ticketids[0]),
        },
        {
            "ticketid": str(ticketids[3]),
        },
    ]

    response = api_client.put(
        reverse("tickets_on_column", args=[newcolumnid]),
        data=json.dumps(data),
        content_type="application/json",
    )
    assert response.status_code == 200
    # Get tickets from new column
    response = api_client.get(reverse("tickets_on_column", args=[newcolumnid]))
    data = response.json()
    assert len(data) == 2
    assert response.status_code == 200
    # Get tickets from old column
    response = api_client.get(reverse("tickets_on_column", args=[columnid]))
    data = response.json()
    assert len(data) == 3
    assert response.status_code == 200

    resetDB()


@pytest.mark.django_db
def test_update_ticket():
    """
    Test the update_ticket function in backend/futuboard/views/views.py
    Has two methods: PUT and DELETE
        PUT: Updates a ticket
        DELETE: Deletes a ticket
    """
    api_client = APIClient()
    # Create a board and a column and add a ticket to it
    columnid = uuid.uuid4()
    response = api_client.post(reverse("all_boards"), {"title": "board", "password": "password"})
    boardid = response.json()["boardid"]
    assert response.status_code == 200
    data = {"columnid": str(columnid), "title": "column", "position": 0, "swimlane": False}
    response = api_client.post(
        reverse("columns_on_board", args=[boardid]), data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200

    # Add a ticket to column
    ticketid = uuid.uuid4()
    data = {
        "ticketid": str(ticketid),
        "title": "ticket",
        "description": "description",
        "position": 0,
        "size": 5,
    }
    response = api_client.post(
        reverse("tickets_on_column", args=[columnid]),
        data=json.dumps(data),
        content_type="application/json",
    )
    assert response.status_code == 200

    # Test PUT request to update ticket
    data = {
        "ticketid": str(ticketid),
        "title": "updatedticket",
        "description": "This is an updated description",
        "position": 0,
        "size": 5,
    }
    response = api_client.put(
        reverse("update_ticket", args=[ticketid]), data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200

    # Get ticket by id
    response = api_client.get(reverse("tickets_on_column", args=[columnid]))
    data = response.json()
    print(data)
    assert data[0]["title"] == "updatedticket"
    assert data[0]["description"] == "This is an updated description"
    assert response.status_code == 200

    resetDB()


@pytest.mark.django_db
def test_update_column():
    """
    Test the update_column function in backend/futuboard/views/views.py
    Has two methods: PUT and DELETE
        PUT: Updates a column
        DELETE: Deletes column
    """
    api_client = APIClient()

    # Create a board and a column
    columnid = uuid.uuid4()
    response = api_client.post(reverse("all_boards"), {"title": "board", "password": "password"})
    assert response.status_code == 200
    boardid = response.json()["boardid"]

    data = {"columnid": str(columnid), "title": "column", "position": 0, "swimlane": False}
    response = api_client.post(
        reverse("columns_on_board", args=[boardid]), data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200

    # Test PUT request to update column
    data = {"columnid": str(columnid), "title": "updatedcolumn", "position": 0, "swimlane": False}
    response = api_client.put(
        reverse("update_column", args=[columnid]), data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200

    # Get column by id
    response = api_client.get(reverse("columns_on_board", args=[boardid]))
    data = response.json()
    assert data[0]["title"] == "updatedcolumn"
    assert response.status_code == 200

    resetDB()


@pytest.mark.django_db
def test_users_on_board():
    """
    Test the users_on_board function in backend/futuboard/views/views.py
    Has two methods: GET and POST
        GET: Returns all users from a board
        POST: Adds a user to a board
    """
    api_client = APIClient()
    # Create a board and add 5 users to it
    response = api_client.post(reverse("all_boards"), {"title": "board", "password": "password"})
    assert response.status_code == 200
    boardid = response.json()["boardid"]
    userids = [uuid.uuid4() for i in range(5)]
    for i in range(5):
        response = api_client.post(
            reverse("users_on_board", args=[boardid]),
            {"userid": str(userids[i]), "name": "user" + str(i)},
        )
        assert response.status_code == 200

    response = api_client.get(reverse("users_on_board", args=[boardid]))
    data = response.json()
    assert len(data) == 5
    assert response.status_code == 200

    md.User.objects.all().delete()

    response = api_client.get(reverse("users_on_board", args=[boardid]))
    data = response.json()
    assert len(data) == 0
    assert response.status_code == 200

    resetDB()


@pytest.mark.django_db
def test_users_on_ticket():
    """
    Test the users_on_ticket function in backend/futuboard/views/views.py
    Has three methods: GET, POST and PUT
        GET: Returns all users from a ticket
        POST: Adds a user to a ticket
        DELETE: Removes a user from a ticket
    """

    api_client = APIClient()
    # Create a board, a column, a ticket and add 5 users to it
    columnid = uuid.uuid4()
    ticketid = uuid.uuid4()
    response = api_client.post(reverse("all_boards"), {"title": "board", "password": "password"})
    assert response.status_code == 200
    boardid = response.json()["boardid"]

    data = {"columnid": str(columnid), "title": "column", "position": 0, "swimlane": False}
    response = api_client.post(
        reverse("columns_on_board", args=[boardid]), data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200
    data = {
        "ticketid": str(ticketid),
        "title": "ticket",
        "description": "description",
        "position": 0,
        "size": 5,
    }
    response = api_client.post(
        reverse("tickets_on_column", args=[columnid]),
        data=json.dumps(data),
        content_type="application/json",
    )
    assert response.status_code == 200
    userids = []
    for i in range(5):
        response = api_client.post(
            reverse("users_on_board", args=[boardid]),
            {"name": "user" + str(i)},
        )
        assert response.status_code == 200
        userids.append(response.json()["userid"])

    for i in range(5):
        response = api_client.post(
            reverse("users_on_ticket", args=[ticketid]),
            {"userid": userids[i]},
        )
        assert response.status_code == 200

    # Get users from ticket
    response = api_client.get(reverse("users_on_ticket", args=[ticketid]))
    data = response.json()
    assert len(data) == 5
    assert response.status_code == 200

    for i in range(5):
        response = api_client.delete(
            reverse("users_on_ticket", args=[ticketid]),
            {"userid": userids[i]},
        )
        assert response.status_code == 200

    # Get users from ticket
    response = api_client.get(reverse("users_on_ticket", args=[ticketid]))
    data = response.json()
    assert len(data) == 0
    assert response.status_code == 200

    resetDB()


@pytest.mark.django_db
def test_update_user():
    """
    Test the update_user function in backend/futuboard/views/views.py
    Has one method: DELETE
        DELETE: Deletes a user
    """
    api_client = APIClient()
    # Create a board and a user
    response = api_client.post(reverse("all_boards"), {"title": "board", "password": "password"})
    assert response.status_code == 200
    boardid = response.json()["boardid"]
    response = api_client.post(reverse("users_on_board", args=[boardid]), {"name": "user"})
    data = response.json()
    # get user id from response
    print(data)
    userid = data["userid"]
    assert response.status_code == 200
    # Test DELETE request to update user
    response = api_client.delete(reverse("update_user", args=[userid]))
    assert response.status_code == 200
    # Check that amount of users is 0
    assert md.User.objects.count() == 0

    resetDB()


@pytest.mark.django_db
def test_deleting_column():
    """
    Test deleting a column by id
    Test that the right column is deleted.
    """
    api_client = APIClient()

    boardid = addBoard().boardid
    columnid = addColumn(boardid, uuid.uuid4()).columnid
    columnid2 = addColumn(boardid, uuid.uuid4()).columnid

    response = api_client.delete(reverse("update_column", args=[columnid]))

    assert response.status_code == 200
    assert md.Column.objects.all()[0].columnid == columnid2

    resetDB()


@pytest.mark.django_db
def test_deleting_ticket():
    """
    Test deleting a ticket by id
    Test that the right ticket is deleted.
    """

    api_client = APIClient()

    boardid = addBoard().boardid
    columnid = addColumn(boardid, uuid.uuid4()).columnid
    ticketid = addTicket(columnid, uuid.uuid4()).ticketid
    ticketid2 = addTicket(columnid, uuid.uuid4()).ticketid

    response = api_client.delete(reverse("update_ticket", args=[ticketid]))

    assert response.status_code == 200
    assert md.Ticket.objects.all()[0].ticketid == ticketid2

    resetDB()


@pytest.mark.django_db
def test_updating_columns_order():
    """
    Test updating columns order
    Test that columns new order is correct
    """

    api_client = APIClient()

    boardid = addBoard().boardid
    columnid1 = addColumn(boardid, uuid.uuid4()).columnid
    columnid2 = addColumn(boardid, uuid.uuid4()).columnid
    columnid3 = addColumn(boardid, uuid.uuid4()).columnid
    columnid4 = addColumn(boardid, uuid.uuid4(), "Swimlane", True).columnid

    data = [
        {"columnid": str(columnid3)},
        {"columnid": str(columnid4)},
        {"columnid": str(columnid2)},
        {"columnid": str(columnid1)},
    ]

    response = api_client.put(
        reverse("columns_on_board", args=[boardid]), data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200
    assert md.Column.objects.get(pk=columnid1).ordernum == 3
    assert md.Column.objects.get(pk=columnid2).ordernum == 2
    assert md.Column.objects.get(pk=columnid3).ordernum == 0
    assert md.Column.objects.get(pk=columnid4).ordernum == 1

    response = api_client.get(reverse("columns_on_board", args=[boardid]))
    data = response.json()
    assert data[0]["columnid"] == str(columnid3)
    assert data[1]["columnid"] == str(columnid4)
    assert data[2]["columnid"] == str(columnid2)
    assert data[3]["columnid"] == str(columnid1)

    resetDB()


@pytest.mark.django_db
def test_password_change_correct():
    """
    Test that password changes correctly
    """
    api_client = APIClient()

    boardid = addBoard(password="password").boardid

    # Get token for auth
    response = api_client.post(reverse("board_by_id", args=[boardid]), {"password": "password"})
    assert response.status_code == 200
    data = response.json()
    token = data["token"]

    response = api_client.put(
        reverse("update_board_password", args=[boardid]),
        data={
            "old_password": "password",
            "new_password": "newpassword",
            "confirm_password": "newpassword",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert verify_password("newpassword", md.Board.objects.all()[0].passwordhash)

    resetDB()


@pytest.mark.django_db
def test_password_change_with_incorrect_old_password():
    """
    Test that password doesn't change if given incorrect old password
    """
    api_client = APIClient()

    boardid = addBoard(password="password").boardid

    # Get token for auth
    response = api_client.post(reverse("board_by_id", args=[boardid]), {"password": "password"})
    assert response.status_code == 200
    data = response.json()
    token = data["token"]

    response = api_client.put(
        reverse("update_board_password", args=[boardid]),
        data={
            "old_password": "wrong",
            "new_password": "newpassword",
            "confirm_password": "newpassword",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert verify_password("password", md.Board.objects.first().passwordhash)

    resetDB()


@pytest.mark.django_db
def test_password_change_with_clashing_confirm_password():
    """
    Test that password doesn't change if new password and confirm password not matching
    """
    api_client = APIClient()

    boardid = addBoard(password="password").boardid

    # Get token for auth
    response = api_client.post(reverse("board_by_id", args=[boardid]), {"password": "password"})
    assert response.status_code == 200
    data = response.json()
    token = data["token"]

    response = api_client.put(
        reverse("update_board_password", args=[boardid]),
        data={
            "old_password": "password",
            "new_password": "newpassword1",
            "confirm_password": "newpassword2",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
    assert verify_password("password", md.Board.objects.first().passwordhash)

    resetDB()


@pytest.mark.django_db
def test_update_ticket_template():
    """
    Test the update_ticket_template function in backend/futuboard/views/boardViewsViews.py
    Has one method: PUT

        PUT: Updates ticket template values
    """
    api_client = APIClient()
    boardid = addBoard(uuid.uuid4(), password="password").boardid

    # Get token for auth
    response = api_client.post(reverse("board_by_id", args=[boardid]), {"password": "password"})
    assert response.status_code == 200
    data = response.json()
    token = data["token"]

    response = api_client.put(
        reverse("update_ticket_template", args=[boardid]),
        data=json.dumps(
            {
                "title": "New title",
                "description": "New description",
                "color": "#ffeb3b",
                "size": 16,
                "cornernote": "New cornernote",
            }
        ),
        content_type="application/json",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert md.Board.objects.get(pk=boardid).default_ticket_color == "#ffeb3b"
    assert md.Board.objects.get(pk=boardid).default_ticket_cornernote == "New cornernote"
    assert md.Board.objects.get(pk=boardid).default_ticket_description == "New description"
    assert md.Board.objects.get(pk=boardid).default_ticket_size == 16
    assert md.Board.objects.get(pk=boardid).default_ticket_title == "New title"

    resetDB()


@pytest.mark.django_db
def test_update_board_notes():
    """
    Test updating the board's notes
    """
    api_client = APIClient()
    boardid = addBoard(password="password").boardid

    # Get token for auth
    response = api_client.post(reverse("board_by_id", args=[boardid]), {"password": "password"})
    assert response.status_code == 200
    data = response.json()
    token = data["token"]

    response = api_client.put(
        reverse("update_board_notes", args=[boardid]),
        data={"notes": "test notes"},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["notes"] == "test notes"
    assert md.Board.objects.get(pk=boardid).notes == "test notes"

    resetDB()
