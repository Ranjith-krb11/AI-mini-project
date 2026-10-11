from tools.retrieval import retrieve_context_with_citations


def test_user_document_isolation(client, user1_auth, user2_auth, valid_pdf_bytes):
    # User 1 uploads a private document
    u1_upload = client.post(
        "/api/documents/upload",
        headers=user1_auth["headers"],
        files={"file": ("user1_private_exam_paper.pdf", valid_pdf_bytes, "application/pdf")}
    )
    assert u1_upload.status_code == 201
    u1_doc_id = u1_upload.json()["document_id"]

    # User 1 can see it
    u1_list = client.get("/api/documents", headers=user1_auth["headers"]).json()
    assert any(d["id"] == u1_doc_id for d in u1_list["documents"])

    # User 2 CANNOT see User 1's document
    u2_list = client.get("/api/documents", headers=user2_auth["headers"]).json()
    assert not any(d["id"] == u1_doc_id for d in u2_list["documents"])


def test_user_vector_retrieval_isolation(client, user1_auth, user2_auth, valid_pdf_bytes):
    # User 1 uploads a document containing specific keywords
    client.post(
        "/api/documents/upload",
        headers=user1_auth["headers"],
        files={"file": ("user1_notes.pdf", valid_pdf_bytes, "application/pdf")}
    )

    u1_id = user1_auth["user"]["id"]
    u2_id = user2_auth["user"]["id"]

    # Query using User 1's ID -> finds matching content
    u1_context, u1_cites = retrieve_context_with_citations("Virtual Memory", user_id=u1_id)
    assert "Virtual Memory" in u1_context
    assert len(u1_cites) > 0

    # Query using User 2's ID -> CANNOT access User 1's vector chunks
    u2_context, u2_cites = retrieve_context_with_citations("Virtual Memory", user_id=u2_id)
    assert u2_context == ""
    assert len(u2_cites) == 0
