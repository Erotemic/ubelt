def test_unable_to_find_color():
    import ubelt as ub
    import pytest
    with pytest.warns(UserWarning):
        text = ub.color_text('text', 'wizbang')
        assert text == 'text', 'bad colors should pass the text back'
