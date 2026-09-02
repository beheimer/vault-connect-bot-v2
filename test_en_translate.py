"""Tests to verify all Ukrainian/Russian developer-facing text has been translated to English."""
import re
import pytest

CYRILLIC = re.compile('[а-яА-ЯёЁіІїЇєЄґҐ]')

# Files that should have NO Cyrillic in comments or developer-facing strings
CLEAN_FILES = [
    'config/settings.py',
    'handlers/__init__.py',
    'utils/access.py',
    'utils/database.py',
    'utils/db.py',
    'utils/lang.py',
    'utils/admin_check.py',
    'utils/promo.py',
    'utils/referral.py',
    
]


def _get_comments(filepath):
    """Extract pure comment lines and inline comments from a Python file."""
    comments = []
    with open(filepath) as f:
        for i, line in enumerate(f, 1):
            stripped = line.strip()
            # Pure comment line
            if stripped.startswith('#'):
                comments.append((i, stripped))
            # Inline comment after code
            elif '#' in line:
                code_part, _, comment_part = line.partition('#')
                if comment_part and not code_part.strip().startswith(('#', '"', "'")):
                    comments.append((i, '#' + comment_part.rstrip()))
    return comments


class TestConfigSettings:
    def test_no_cyrillic_in_comments(self):
        comments = _get_comments('config/settings.py')
        for lineno, comment in comments:
            assert not CYRILLIC.search(comment), \
                f"config/settings.py:{lineno} still has Cyrillic: {comment}"

    def test_admin_comment_translated(self):
        with open('config/settings.py') as f:
            content = f.read()
        assert '# Your Telegram username (without @)' in content

    def test_payment_comment_translated(self):
        with open('config/settings.py') as f:
            content = f.read()
        assert '# Token from @BotFather' in content

    def test_channel_link_comment_translated(self):
        with open('config/settings.py') as f:
            content = f.read()
        assert 'Same as CHANNEL_ID' in content

    def test_channel_id_comment_translated(self):
        with open('config/settings.py') as f:
            content = f.read()
        assert 'Your channel ID' in content

    def test_referral_comment_translated(self):
        with open('config/settings.py') as f:
            content = f.read()
        assert 'completely disables the referral system' in content

    def test_promo_comment_translated(self):
        with open('config/settings.py') as f:
            content = f.read()
        assert 'enables/disables the promo code system' in content


class TestHandlersStart:
    def test_trial_check_comment(self):
        with open('handlers/start.py') as f:
            content = f.read()
        assert '# Check if trial has already been used' in content
        assert 'Перевірка чи тріал' not in content

    def test_trial_duration_comment(self):
        with open('handlers/start.py') as f:
            content = f.read()
        assert '# Read trial duration from settings' in content
        assert 'Читаємо тривалість' not in content


class TestHandlersAdminPanel:
    def test_confirm_buttons_translated(self):
        with open('handlers/admin_panel.py') as f:
            content = f.read()
        assert '"✅ Yes"' in content
        assert '"❌ No"' in content
        assert '"✅ Так"' not in content
        assert '"❌ Ні"' not in content


class TestCleanFiles:
    """Verify files that should have zero Cyrillic in comments."""
    @pytest.mark.parametrize("filepath", CLEAN_FILES)
    def test_no_cyrillic_in_comments(self, filepath):
        comments = _get_comments(filepath)
        for lineno, comment in comments:
            assert not CYRILLIC.search(comment), \
                f"{filepath}:{lineno} has Cyrillic in comment: {comment}"


class TestBotCommandsPreserved:
    """BotCommand strings for uk/ru should NOT have been changed."""
    def test_uk_botcommands_preserved(self):
        with open('bot.py') as f:
            content = f.read()
        assert "🚀 Запустити бота" in content
        assert "🌐 Змінити мову" in content

    def test_ru_botcommands_preserved(self):
        with open('bot.py') as f:
            content = f.read()
        assert "🚀 Запустить бота" in content
        assert "🌐 Изменить язык" in content
