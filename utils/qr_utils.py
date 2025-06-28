from PIL import Image
from pyzbar.pyzbar import decode
from urllib.parse import urlparse, parse_qs, unquote
from typing import List, Tuple, Dict, Optional


def decode_qr_from_image(image: Image.Image) -> List[Tuple[str, Tuple[int, int, int, int]]]:
    """从PIL图像中解码所有二维码。

    Args:
        image: PIL图像对象。
    Returns:
        包含元组(data, rect) 的列表，其中 data 为二维码中的原始字符串，rect 为 (x, y, w, h)。
    """
    results = decode(image)
    decoded = []
    for r in results:
        data = r.data.decode("utf-8", errors="ignore")
        rect = (r.rect.left, r.rect.top, r.rect.width, r.rect.height)
        decoded.append((data, rect))
    return decoded


def parse_otp_uri(uri: str) -> Optional[Dict[str, str]]:
    """解析 otpauth URI，提取名称、发行方和密钥等信息。

    Args:
        uri: otpauth:// 开头的URI。
    Returns:
        如果是有效OTP URI，则返回包含 name、issuer、secret、type 键的字典；否则返回 None。
    """
    try:
        parsed = urlparse(uri)
        if parsed.scheme != "otpauth":
            return None

        otp_type = parsed.netloc  # totp 或 hotp
        label = unquote(parsed.path.lstrip("/"))
        # label 格式可能为 'Issuer:Account' 或仅 'Account'
        if ":" in label:
            issuer_label, name = label.split(":", 1)
        else:
            issuer_label, name = "", label

        params = parse_qs(parsed.query)
        secret = params.get("secret", [""])[0]
        issuer_param = params.get("issuer", [""])[0]
        issuer = issuer_param or issuer_label

        if not secret:
            return None

        return {
            "name": name,
            "issuer": issuer,
            "secret": secret,
            "type": otp_type,
        }
    except Exception:
        return None 