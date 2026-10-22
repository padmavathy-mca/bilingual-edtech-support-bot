"""PII redaction for logs and tickets."""
import logging, re

_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE = re.compile(r"(?<!\d)(?:\+?91[\s-]?)?[6-9]\d{9}(?!\d)")
_LONGNUM = re.compile(r"\b\d{9,}\b")


def redact(text: str) -> str:
    text = _EMAIL.sub("[email]", text)
    text = _PHONE.sub("[phone]", text)
    return _LONGNUM.sub("[number]", text)


class RedactFilter(logging.Filter):
    def filter(self, record):
        record.msg = redact(str(record.msg))
        return True


def get_logger(name="support-bot"):
    log = logging.getLogger(name)
    if not log.handlers:
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        h.addFilter(RedactFilter())
        log.addHandler(h); log.setLevel(logging.INFO)
    return log
