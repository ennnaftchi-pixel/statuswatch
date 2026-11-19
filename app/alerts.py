import httpx

from app.config import settings


async def send_telegram_alert(service_name: str, status: str, url: str) -> None:
    """Sends a message to Telegram if credentials are configured."""
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        print(f"[WARNING] Telegram credentials not set. Skipping alert for {service_name}.")
        return

    status_text = "DOWN" if status == "down" else "RECOVERED"
    
    text = (
        f"*StatusWatch Alert*\n\n"
        f"Service: *{service_name}*\n"
        f"URL: {url}\n"
        f"Status: *{status_text}*"
    )

    api_url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": text,
        "parse_mode": "Markdown",
    }

    async with httpx.AsyncClient() as client:
        try:
            await client.post(api_url, json=payload, timeout=5.0)
        except httpx.RequestError as exc:
            print(f"[ERROR] Failed to send Telegram alert: {exc}")
