def test_create_and_list_conversations(client, user1_auth):
    create_res = client.post(
        "/api/conversations",
        headers=user1_auth["headers"],
        json={"title": "Midterm Review Session"}
    )
    assert create_res.status_code == 201
    conv_id = create_res.json()["id"]

    list_res = client.get("/api/conversations", headers=user1_auth["headers"])
    assert list_res.status_code == 200
    conversations = list_res.json()
    assert any(c["id"] == conv_id and c["title"] == "Midterm Review Session" for c in conversations)


def test_get_conversation_messages(client, user1_auth):
    create_res = client.post(
        "/api/conversations",
        headers=user1_auth["headers"],
        json={"title": "Algorithms Q&A"}
    )
    conv_id = create_res.json()["id"]

    get_res = client.get(f"/api/conversations/{conv_id}", headers=user1_auth["headers"])
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["id"] == conv_id
    assert isinstance(data["messages"], list)


def test_delete_conversation(client, user1_auth):
    create_res = client.post(
        "/api/conversations",
        headers=user1_auth["headers"],
        json={"title": "To Be Deleted"}
    )
    conv_id = create_res.json()["id"]

    del_res = client.delete(f"/api/conversations/{conv_id}", headers=user1_auth["headers"])
    assert del_res.status_code == 200

    # Ensure deleted
    get_res = client.get(f"/api/conversations/{conv_id}", headers=user1_auth["headers"])
    assert get_res.status_code == 404
