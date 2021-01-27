def test_unable_to_find_color():
    import ubelt as ub
    import pytest
    if ub.util_colors.NO_COLOR:
        pytest.skip()

    with pytest.warns(UserWarning):
        text = ub.color_text('text', 'wizbang')
        assert text == 'text', 'bad colors should pass the text back'


def test_global_color_disable():
    """
    CommandLine:
        xdoctest -m /home/joncrall/code/ubelt/tests/test_color.py test_global_color_disable
    """
    import ubelt as ub
    import pytest

    if ub.util_colors.NO_COLOR:
        pytest.skip()

    text = 'text = "hi"'

    has_color = ub.color_text(text, 'red') != ub.color_text(text, None)

    text1a = ub.color_text(text, 'red')
    text1b = ub.highlight_code(text)
    if has_color:
        assert text != text1a
        assert text != text1b

    # Force colors to be disabled
    prev = ub.util_colors.NO_COLOR

    try:
        ub.util_colors.NO_COLOR = True

        text2a = ub.color_text(text, 'red')
        text2b = ub.highlight_code(text)
        assert text == text2a
        assert text == text2b
    finally:
        # Re-enable coloration
        ub.util_colors.NO_COLOR = prev

    text3a = ub.color_text(text, 'red')
    text3b = ub.highlight_code(text)
    if has_color:
        assert text != text3a
        assert text != text3b
