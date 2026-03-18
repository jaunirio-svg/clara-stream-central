import asyncio
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple, Set

import aiohttp
import yaml


@dataclass
class Channel:
    name: str
    url: str
    tvg_logo: Optional[str]
    group_title: Optional[str]
    raw_extinf: str


class ClaraProcessor:
    def __init__(self, settings_path: str) -> None:
        self.settings_path = settings_path
        self.settings: Dict = {}

    async def load_settings(self) -> None:
        loop = asyncio.get_running_loop()
        content = await loop.run_in_executor(None, self._read_file_sync, self.settings_path)
        self.settings = yaml.safe_load(content) or {}

    @staticmethod
    def _read_file_sync(path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    async def fetch_m3u(self, session: aiohttp.ClientSession, url: str) -> str:
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with session.get(url, timeout=timeout) as resp:
                if resp.status != 200:
                    return ""
                return await resp.text(encoding="utf-8", errors="ignore")
        except Exception:
            return ""

    @staticmethod
    def parse_m3u(content: str) -> List[Channel]:
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        channels: List[Channel] = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.startswith("#EXTINF"):
                extinf = line
                url = lines[i + 1] if i + 1 < len(lines) else ""
                name = ClaraProcessor._extract_name(extinf)
                tvg_logo = ClaraProcessor._extract_attr(extinf, "tvg-logo")
                group_title = ClaraProcessor._extract_attr(extinf, "group-title")
                channels.append(
                    Channel(
                        name=name,
                        url=url,
                        tvg_logo=tvg_logo,
                        group_title=group_title,
                        raw_extinf=extinf,
                    )
                )
                i += 2
            else:
                i += 1
        return channels

    @staticmethod
    def _extract_attr(extinf: str, attr: str) -> Optional[str]:
        marker = f'{attr}="'
        start = extinf.find(marker)
        if start == -1:
            return None
        start += len(marker)
        end = extinf.find('"', start)
        if end == -1:
            return None
        return extinf[start:end]

    @staticmethod
    def _extract_name(extinf: str) -> str:
        if "," in extinf:
            return extinf.split(",", 1)[1].strip()
        return "Unknown"

    async def _check_channel_live(self, session: aiohttp.ClientSession, channel: Channel) -> Tuple[Channel, bool]:
        try:
            timeout = aiohttp.ClientTimeout(total=5)
            async with session.head(channel.url, timeout=timeout) as resp:
                if resp.status == 200:
                    return channel, True
            async with session.get(channel.url, timeout=timeout) as resp:
                return channel, resp.status == 200
        except Exception:
            return channel, False

    async def filter_live_channels(self, channels: List[Channel], check_live: bool) -> List[Channel]:
        if not check_live:
            return channels
        async with aiohttp.ClientSession() as session:
            tasks = [self._check_channel_live(session, ch) for ch in channels]
            results = await asyncio.gather(*tasks)
        return [ch for ch, is_live in results if is_live]

    def filter_by_category(self, channels: List[Channel], allowed_categories: List[str]) -> List[Channel]:
        if not allowed_categories:
            return channels
        allowed_upper = {c.upper() for c in allowed_categories}
        filtered: List[Channel] = []
        for ch in channels:
            group = (ch.group_title or "").upper()
            if group in allowed_upper:
                filtered.append(ch)
        return filtered

    @staticmethod
    def remove_duplicates(channels: List[Channel]) -> List[Channel]:
        seen: Set[str] = set()
        unique: List[Channel] = []
        for ch in channels:
            if ch.url not in seen:
                seen.add(ch.url)
                unique.append(ch)
        return unique

    @staticmethod
    def to_m3u(channels: List[Channel], categories_order: List[str]) -> str:
        lines: List[str] = ["#EXTM3U"]
        by_group: Dict[str, List[Channel]] = {}
        for ch in channels:
            group = ch.group_title or "OUTROS"
            by_group.setdefault(group, []).append(ch)

        ordered_keys = []
        for cat in categories_order:
            if cat in by_group:
                ordered_keys.append(cat)
        for k in by_group:
            if k not in ordered_keys:
                ordered_keys.append(k)

        for group in ordered_keys:
            lines.append(f"# --- {group} ---")
            for ch in by_group[group]:
                lines.append(ch.raw_extinf)
                lines.append(ch.url)
        return "\n".join(lines) + "\n"

    async def run(self) -> Dict[str, int]:
        await self.load_settings()
        sources = self.settings.get("sources", [])
        filters = self.settings.get("filters", {})
        allowed_categories = filters.get("allowed_categories", [])
        check_live_status = bool(filters.get("check_live_status", True))

        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_m3u(session, s.get("url", "")) for s in sources if s.get("url")]
            playlists = await asyncio.gather(*tasks)

        all_channels: List[Channel] = []
        for content in playlists:
            if not content:
                continue
            all_channels.extend(self.parse_m3u(content))

        all_channels = self.filter_by_category(all_channels, allowed_categories)
        all_channels = self.remove_duplicates(all_channels)
        all_channels = await self.filter_live_channels(all_channels, check_live_status)

        m3u_content = self.to_m3u(all_channels, allowed_categories)
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._write_file_sync, "output/channels.m3u", m3u_content)

        return {"online_channels": len(all_channels)}

    @staticmethod
    def _write_file_sync(path: str, content: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


async def process_pipeline(settings_path: str = "config/settings.yaml") -> Dict[str, int]:
    processor = ClaraProcessor(settings_path)
    return await processor.run()