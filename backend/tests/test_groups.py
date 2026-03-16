from fastapi.testclient import TestClient
from sqlmodel import Session
import starlette.status

from domain.users.entity import User
from domain.groups.entity import Group


def test_create_group(session: Session, test_user: User, authenticated_client: TestClient):
    response = authenticated_client.post(
        "/groups/", json={"name": "Test Group", "columns": ["col1", "col2"]})
    data = response.json()

    assert response.status_code in [
        starlette.status.HTTP_200_OK, starlette.status.HTTP_201_CREATED]
    assert data["name"] == "Test Group"
    assert data["owner_id"] == test_user.id


def test_read_groups(session: Session, test_user: User, authenticated_client: TestClient):
    group = Group(name="My Test Group", owner_id=test_user.id, columns=[])
    session.add(group)
    session.commit()

    response = authenticated_client.get("/groups/")
    data = response.json()

    assert response.status_code == starlette.status.HTTP_200_OK
    assert len(data) >= 1
    assert any(g["name"] == "My Test Group" for g in data)


def test_read_group(session: Session, test_user: User, authenticated_client: TestClient):
    group = Group(name="Another Test Group", owner_id=test_user.id, columns=[])
    session.add(group)
    session.commit()

    response = authenticated_client.get(f"/groups/{group.id}")
    data = response.json()

    assert response.status_code == starlette.status.HTTP_200_OK
    assert data["name"] == "Another Test Group"


def test_update_group(session: Session, test_user: User, authenticated_client: TestClient):
    group = Group(name="Group to Update", owner_id=test_user.id, columns=[])
    session.add(group)
    session.commit()

    response = authenticated_client.patch(
        f"/groups/{group.id}", json={"name": "Updated Name"})
    data = response.json()

    assert response.status_code == starlette.status.HTTP_200_OK
    assert data["name"] == "Updated Name"


def test_delete_group(session: Session, test_user: User, authenticated_client: TestClient):
    group = Group(name="Group to Delete", owner_id=test_user.id, columns=[])
    session.add(group)
    session.commit()
    group_id = group.id

    response = authenticated_client.delete(f"/groups/{group_id}")
    assert response.status_code == starlette.status.HTTP_200_OK

    # Expire the session to clear the identity map and force a fresh query from the database
    session.expunge_all()
    deleted_group = session.get(Group, group_id)
    assert deleted_group is None
