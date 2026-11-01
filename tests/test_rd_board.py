"""Read-only /rd ledger. The page must not accept orders or strategy edits."""
import json
from pathlib import Path

import pytest

from quantlab import rd_board
from quantlab.webapp import app as webapp


def test_ledger_rejects_a_closed_message_without_evidence(tmp_path):
    path = tmp_path / "messages.jsonl"
    path.write_text(json.dumps({
        "id": "x",
        "role": "test",
        "status": "answered",
        "evidence": "  ",
        "body": "closed without a path",
    }) + "\n", encoding="utf-8")
    with pytest.raises(ValueError, match="rd_message"):
        rd_board.load_messages(path)


def test_checked_in_ledger_loads_and_keeps_product_items_open():
    rows = rd_board.load_messages()
    by_id = {row["id"]: row for row in rows}
    assert by_id["product-001"]["status"] == "open"
    assert by_id["product-002"]["status"] == "open"
    assert by_id["architect-002"]["status"] == "open"
    assert by_id["director-001"]["evidence"].startswith("docs/rd/experiments/")
    assert (Path(rd_board.LEDGER).parent / "experiments" / "universe.md").is_file()
    assert (Path(rd_board.LEDGER).parent / "experiments" / "factors.md").is_file()
    assert (Path(rd_board.LEDGER).parent / "experiments" / "portfolio.md").is_file()


def test_rd_page_is_read_only_and_pins_open_threads():
    webapp.app.config.update(TESTING=True)
    response = webapp.app.test_client().get("/rd")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "未关闭" in html
    assert "可交易候选" in html
    assert "实验设计" in html
    assert "股票池消融设计" in html
    assert 'id=rd-role-product' in html
    assert 'id=rd-role-architect' in html
    assert "<form" not in html.lower()
    assert "method=\"post\"" not in html.lower()
    assert html.index("id=rd-open") < html.index("id=rd-role-product")
