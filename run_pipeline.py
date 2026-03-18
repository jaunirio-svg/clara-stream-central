import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.processor import process_pipeline

LOG_FILE = Path("logs/pipeline.log")
STATUS_FILE = Path("output/pipeline_status.json")

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def log(message: str) -> None:
    timestamp = utc_now_iso()
    line = f"[{timestamp}] {message}\n"
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(line)


async def main_async() -> None:
    try:
        log("Iniciando pipeline CLARA_STREAM.")
        stats = await process_pipeline()
        status = {
            "last_run": utc_now_iso(),
            "online_channels": stats.get("online_channels", 0),
            "server_status": "ONLINE",
        }
        STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with STATUS_FILE.open("w", encoding="utf-8") as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
        log(f"Pipeline concluído com sucesso. Canais online: {status['online_channels']}.")
    except Exception as exc:
        log(f"Erro no pipeline: {exc!r}")
        status = {
            "last_run": utc_now_iso(),
            "online_channels": 0,
            "server_status": "ERRO",
        }
        STATUS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with STATUS_FILE.open("w", encoding="utf-8") as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
        raise


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()