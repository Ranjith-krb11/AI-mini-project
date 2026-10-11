from database.vector_db import get_or_create_collection


def test_upload_valid_pdf(client, user1_auth, valid_pdf_bytes):
    res = client.post(
        "/api/documents/upload",
        headers=user1_auth["headers"],
        files={"file": ("operating_systems.pdf", valid_pdf_bytes, "application/pdf")}
    )
    assert res.status_code == 201
    data = res.json()
    assert "document_id" in data
    assert data["original_filename"] == "operating_systems.pdf"
    assert data["chunks"] > 0


def test_upload_non_pdf_extension_rejected(client, user1_auth):
    res = client.post(
        "/api/documents/upload",
        headers=user1_auth["headers"],
        files={"file": ("notes.txt", b"plain text notes", "text/plain")}
    )
    assert res.status_code == 400
    assert "pdf" in res.json()["detail"].lower()


def test_upload_empty_pdf_rejected(client, user1_auth):
    res = client.post(
        "/api/documents/upload",
        headers=user1_auth["headers"],
        files={"file": ("empty.pdf", b"", "application/pdf")}
    )
    assert res.status_code == 400
    assert "empty" in res.json()["detail"].lower()


def test_list_documents(client, user1_auth, valid_pdf_bytes):
    # Upload a document first
    client.post(
        "/api/documents/upload",
        headers=user1_auth["headers"],
        files={"file": ("lecture_syllabus.pdf", valid_pdf_bytes, "application/pdf")}
    )

    res = client.get("/api/documents", headers=user1_auth["headers"])
    assert res.status_code == 200
    data = res.json()
    assert data["total"] >= 1
    assert any(d["original_filename"] == "lecture_syllabus.pdf" for d in data["documents"])


def test_delete_document_and_vector_cleanup(client, user1_auth, valid_pdf_bytes):
    # Upload
    upload_res = client.post(
        "/api/documents/upload",
        headers=user1_auth["headers"],
        files={"file": ("temporary_notes.pdf", valid_pdf_bytes, "application/pdf")}
    )
    doc_id = upload_res.json()["document_id"]

    # Verify vector chunks exist in ChromaDB
    collection = get_or_create_collection()
    chunks_before = collection.get(where={"document_id": doc_id})
    assert len(chunks_before["ids"]) > 0

    # Delete document
    del_res = client.delete(f"/api/documents/{doc_id}", headers=user1_auth["headers"])
    assert del_res.status_code == 200

    # Verify deleted from DB
    list_res = client.get("/api/documents", headers=user1_auth["headers"])
    assert not any(d["id"] == doc_id for d in list_res.json()["documents"])

    # Verify vector chunks were purged from ChromaDB
    chunks_after = collection.get(where={"document_id": doc_id})
    assert len(chunks_after["ids"]) == 0
