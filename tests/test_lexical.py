from app.lexical import lexical_support

ARTICLE = "Video Playback\n## Videos are buffering or not playing\nCheck your internet connection and lower the video quality."
TA = "வீடியோ\n## வீடியோக்கள் ஓடவில்லை\nஇணைய இணைப்பைச் சரிபார்க்கவும்."

def test_shared_words_pass():
    assert lexical_support("video keeps buffering", ARTICLE)
    assert lexical_support("வீடியோ ஓடவில்லை", TA)

def test_unrelated_words_fail():
    assert not lexical_support("best biryani recipe", ARTICLE)
    assert not lexical_support("சிக்கன் பிரியாணி செய்வது எப்படி", TA)

def test_only_stopwords_fail():
    assert not lexical_support("what is the", ARTICLE)