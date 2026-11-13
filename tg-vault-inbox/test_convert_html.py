from pathlib import Path

from convert_html import convert

SAMPLE = """
<div class="page_header"><div class="content"><div class="text bold">Performers</div></div></div>
<div class="history">
  <div class="message service" id="message-1"><div class="body details">14 November 2026</div></div>
  <div class="message default clearfix" id="message1">
    <div class="body">
      <div class="pull_right date details" title="14.11.2026 00:08:12 UTC+03:00">00:08</div>
      <div class="from_name">Alice</div>
      <div class="text">Hello <a href="https://example.com">link</a><br>next line</div>
    </div>
  </div>
  <div class="message default clearfix joined" id="message2">
    <div class="body">
      <div class="pull_right date details" title="14.11.2026 00:09:00 UTC+03:00">00:09</div>
      <div class="text">Second</div>
    </div>
  </div>
  <div class="message default clearfix" id="message3">
    <div class="body">
      <div class="pull_right date details" title="14.11.2026 00:10:00 UTC+03:00">00:10</div>
      <div class="from_name">Bob</div>
      <div class="media_wrap"><div class="title bold">brief.pdf</div></div>
    </div>
  </div>
</div>
"""


def test_html_export_becomes_markdown(tmp_path: Path) -> None:
    source = tmp_path / "messages.html"
    source.write_text(SAMPLE, encoding="utf-8")
    output = tmp_path / "performers.md"
    chat_name, count = convert(source, output)
    text = output.read_text(encoding="utf-8")
    assert chat_name == "Performers"
    assert count == 3
    assert "## 14 November 2026" in text
    assert "[14.11.2026 00:08:12 UTC+03:00] @Alice: Hello link\n  next line" in text
    assert "[14.11.2026 00:09:00 UTC+03:00] @Alice: Second" in text
    assert "[file] brief.pdf" in text
