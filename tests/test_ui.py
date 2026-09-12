from app.ui import FONT_PATH, page_css, render_markdown


def test_renders_each_markdown_block_with_automatic_direction():
    rendered = render_markdown(
        "## نتیجه\n\nمقدار BMI برابر 23 است.\n\n## Summary\n\nBMI equals 23."
    )

    assert '<h2 dir="auto">نتیجه</h2>' in rendered
    assert '<p dir="auto">مقدار BMI برابر 23 است.</p>' in rendered
    assert '<h2 dir="auto">Summary</h2>' in rendered
    assert '<p dir="auto">BMI equals 23.</p>' in rendered


def test_markdown_is_sanitized_and_font_is_bundled():
    rendered = render_markdown('[unsafe](javascript:alert(1)) <script>alert(2)</script>')
    css = page_css()

    assert "javascript:" not in rendered
    assert "<script>" not in rendered
    assert FONT_PATH.is_file()
    assert 'font-family: "Vazirmatn"' in css
    assert ':dir(rtl)' in css


def test_page_css_keeps_streamlit_shell_light_and_responsive():
    css = page_css()

    assert '[data-testid="stHeader"]' in css
    assert '[data-testid="stAppViewContainer"]' in css
    assert "@media (max-width: 768px)" in css
