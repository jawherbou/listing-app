def test_upsert_listing(client):
    payload = {
        "listings": [
            {
                "listing_id": "test123",
                "scan_date": "2024-10-22 12:00:00",
                "is_active": True,
                "image_hashes": ["abc123"],
                "properties": [
                    {"name": "brand", "type": "str", "value": "TestBrand"}
                ],
                "entities": [
                    {"name": "test_entity", "data": {"key": "value"}}
                ]
            }
        ]
    }
    response = client.put("/api/upsert", json=payload)

    assert response.status_code == 200
    assert response.json()["message"] == "Listings inserted/updated successfully."

def test_get_listing(client):
    payload = {
        "listings": [
            {
                "listing_id": "test123",
                "scan_date": "2025-01-01T00:00:00",
                "is_active": True,
                "image_hashes": ["hash1"],
                "entities": [],
                "properties": []
            }
        ]
    }
    client.put("/api/upsert", json=payload)

    response = client.get("/api/listings", params={"listing_id": "test123"})

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["listings"][0]["listing_id"] == "test123"
