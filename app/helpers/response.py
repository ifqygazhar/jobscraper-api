from typing import Any, Dict
from fastapi.responses import JSONResponse


class ResponseHelper:
    """Helper untuk membuat response API yang konsisten di FastAPI"""

    @staticmethod
    def success_response(
        message: str, data: Any, status_code: int = 200
    ) -> JSONResponse:
        """
        Buat response sukses

        Args:
            message: Pesan sukses
            data: Data yang akan dikembalikan
            status_code: HTTP status code (default: 200)
        """
        return JSONResponse(
            status_code=status_code,
            content={"status": "success", "message": message, "data": data},
        )

    @staticmethod
    def failure_response(message: str, status_code: int = 500) -> JSONResponse:
        """
        Buat response gagal

        Args:
            message: Pesan error
            status_code: HTTP status code (default: 500)
        """
        return JSONResponse(
            status_code=status_code, content={"status": "failed", "message": message}
        )
