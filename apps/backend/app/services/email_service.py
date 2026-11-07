"""Email service with mock mode for dev/test."""

from dataclasses import dataclass, field

from app.config import get_settings


@dataclass
class EmailMessage:
    to: str
    subject: str
    html: str


@dataclass
class InMemoryEmailBackend:
    """For tests + local dev."""
    sent: list[EmailMessage] = field(default_factory=list)

    def send(self, msg: EmailMessage) -> bool:
        self.sent.append(msg)
        return True


_backend = InMemoryEmailBackend()


def get_backend() -> InMemoryEmailBackend:
    return _backend


def reset_backend() -> None:
    _backend.sent.clear()


def send_email(to: str, subject: str, html: str) -> bool:
    settings = get_settings()
    msg = EmailMessage(to=to, subject=subject, html=html)
    if settings.email_provider == "mock":
        return _backend.send(msg)
    # Future: Resend / SES integration here
    return _backend.send(msg)


def build_verify_email(name: str, link: str) -> tuple[str, str]:
    subject = "Xác minh email DailyExam"
    html = (
        f"<p>Chào {name},</p>"
        f"<p>Vui lòng xác minh email bằng cách click vào link bên dưới:</p>"
        f'<p><a href="{link}">{link}</a></p>'
        f"<p>Link hiệu lực trong 24 giờ.</p>"
    )
    return subject, html


def build_reset_email(name: str, link: str) -> tuple[str, str]:
    subject = "Đặt lại mật khẩu DailyExam"
    html = (
        f"<p>Chào {name},</p>"
        f"<p>Dùng link bên dưới để đặt lại mật khẩu:</p>"
        f'<p><a href="{link}">{link}</a></p>'
        f"<p>Link hiệu lực trong 15 phút.</p>"
    )
    return subject, html


def build_result_email(parent_name: str, child_name: str, school: str, score: float, max_score: float, link: str) -> tuple[str, str]:
    subject = f"Kết quả bài thi của {child_name}"
    pct = round(score / max_score * 100) if max_score else 0
    html = (
        f"<p>Chào {parent_name},</p>"
        f"<p><strong>{child_name}</strong> vừa hoàn thành đề thi {school}.</p>"
        f"<p>Điểm: <strong>{score:.1f} / {max_score:.1f}</strong> ({pct}%)</p>"
        f'<p><a href="{link}">Xem chi tiết</a></p>'
    )
    return subject, html
