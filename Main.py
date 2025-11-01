# main.py
import argparse
import asyncio
import logging
from telethon_client import make_client, load_config
from db import init_db
from scanner import scan_initial_or_incremental

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

async def main():
    p = argparse.ArgumentParser()
    p.add_argument("--full", action="store_true", help="Run full initial scan")
    args = p.parse_args()
    await init_db(load_config().get("db_path", "tmauto.db"))
    await scan_initial_or_incremental(full_scan=args.full)

if __name__ == "__main__":
    asyncio.run(main())
