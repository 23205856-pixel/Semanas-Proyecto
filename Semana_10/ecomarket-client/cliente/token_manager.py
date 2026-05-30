import aiohttp
import asyncio
import base64
import json
import time

from typing import Optional


class TokenManager:

    def __init__(self):

        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None

        self._refresh_lock = asyncio.Lock()

        self._refresh_endpoint = (
            "http://localhost:8000/api/auth/refresh"
        )

    def decode_payload(self, token: str):

        try:

            _, payload, _ = token.split('.')

            payload += '=' * (-len(payload) % 4)

            decoded = base64.b64decode(payload)

            return json.loads(decoded)

        except Exception:

            raise ValueError(
                "Token malformado"
            )

    def is_expiring_soon(
        self,
        margin_seconds: int = 300
    ) -> bool:

        if not self._access_token:
            return True

        payload = self.decode_payload(
            self._access_token
        )

        exp = payload.get("exp")

        if not exp:
            return True

        return (
            exp - int(time.time())
        ) < margin_seconds

    def store_tokens(
        self,
        access_token: str,
        refresh_token: str
    ):

        self._access_token = access_token
        self._refresh_token = refresh_token

    def get_auth_header(self):

        if not self._access_token:
            return {}

        return {
            "Authorization":
                f"Bearer {self._access_token}"
        }

    async def refresh_access_token(self):

        async with self._refresh_lock:

            if (
                self._access_token
                and not self.is_expiring_soon()
            ):
                return True

            if not self._refresh_token:
                return False

            async with aiohttp.ClientSession() as session:

                try:

                    async with session.post(
                        self._refresh_endpoint,
                        json={
                            "refresh_token":
                                self._refresh_token
                        }
                    ) as resp:

                        if resp.status != 200:
                            return False

                        data = await resp.json()

                        self._access_token = (
                            data["access_token"]
                        )

                        if "refresh_token" in data:

                            self._refresh_token = (
                                data["refresh_token"]
                            )

                        return True

                except Exception:

                    return False

    def logout(self):

        self._access_token = None
        self._refresh_token = None