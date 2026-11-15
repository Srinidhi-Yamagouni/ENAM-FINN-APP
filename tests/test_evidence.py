from app.evidence import grounded_claim, verify_number


def test_number_verification_drops_mismatch():
    assert verify_number(410, "EBITDA was INR 410 crore.",).verified
    assert not verify_number(411, "EBITDA was INR 410 crore.").verified
    assert grounded_claim(411, "EBITDA was INR 410 crore.", {"page": "4"}) is None


def test_number_verification_keeps_citation():
    claim = grounded_claim(2310, "Revenue ₹2,310 crore.", {"document": "Q2", "page": "4"})
    assert claim["verified"] is True
    assert claim["citation"]["page"] == "4"
