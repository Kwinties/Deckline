# core.py (facade)
# Keep this file so existing imports keep working:
#   from .core import DeadlineDb, DeadlineMgr, ...
import base64
import hmac
import hashlib

# Public names (no leading underscore) can come via import *
from .core_mod.config import *     # noqa: F401,F403
from .core_mod.helpers import *    # noqa: F401,F403
from .core_mod.models import *     # noqa: F401,F403

# IMPORTANT:
# Python's "from module import *" does NOT import names starting with "_".
# But other files import these underscore helpers from ".core", so we re-export them explicitly.
from .core_mod.helpers import (  # noqa: F401
    _deck_ids_str,
    _today_epoch_ms_range,
    _parse_skip_dates,
    _is_skip_day,
    _count_study_days,
    _planned_remaining_cards,
    _quota_today_constant,
    _progress_color,
    _sanitize_hex_color,
    _sanitize_gradient_list,
)



_PREMIUM_SECRET = b"deckline_secret_change_this_to_random_bytes"

def verify_premium_code(code: str) -> bool:
    """
    Format:
      DL4.<nonce6>.<sig>

    nonce6:
      6 random uppercase letters/numbers

    sig:
      first 6 bytes of HMAC-SHA256(nonce6, secret)
      base64url no padding
    """
    import base64
    import hmac
    import hashlib

    def _b64url_decode(s: str) -> bytes:
        s = (s or "").strip()
        pad = (-len(s)) % 4
        if pad:
            s += "=" * pad
        return base64.urlsafe_b64decode(s.encode("utf-8"))

    try:
        c = (code or "").strip()
        if not c.startswith("DL4."):
            return False

        parts = c.split(".", 2)
        if len(parts) != 3:
            return False

        nonce = parts[1]
        sig_b64 = parts[2]

        if len(nonce) != 6:
            return False

        sig = _b64url_decode(sig_b64)

        full = hmac.new(_PREMIUM_SECRET, nonce.encode("utf-8"), hashlib.sha256).digest()
        expected = full[:6]  # only 6 bytes

        return hmac.compare_digest(sig, expected)

    except Exception:
        return False




