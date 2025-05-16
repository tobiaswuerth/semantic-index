from typing import Callable
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import traceback
from functools import wraps


def exception_handled_json_api(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return JSONResponse(content=result)
        except HTTPException as e:
            print(f"Error: {e}")
            print(traceback.format_exc())
            raise e
        except Exception as e:
            print(f"Error: {e}")
            print(traceback.format_exc())
            raise HTTPException(status_code=500, detail="Internal Server Error")

    return wrapper
