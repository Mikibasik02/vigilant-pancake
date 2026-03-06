import asyncio
import tomllib
import sys
import logging
import os

from tampermint.bot import start_bot


logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(filename="bot.log", encoding="utf-8", level=logging.DEBUG)
    logger.info("Starting main.")
    
    # CERCA IL TOKEN NELLA VARIABILE D'AMBIENTE (PER PRIMO)
    token = os.getenv("DISCORD_TOKEN")
    
    if token:
        # Se trovato nella variabile d'ambiente, usalo direttamente
        logger.info("Token trovato nella variabile d'ambiente DISCORD_TOKEN")
        await start_bot(token)
    else:
        # Altrimenti cerca nel file di configurazione (per compatibilità locale)
        logger.info("Variabile d'ambiente DISCORD_TOKEN non trovata, cerco nel file config.toml")
        try:
            config_file = sys.argv[1] if len(sys.argv) > 1 else "config.toml"
            with open(config_file, "rb") as f:
                config = tomllib.load(f)
            logger.info("Configuration file loaded.")
            await start_bot(config["secret_token"])
        except FileNotFoundError:
            logger.error(f"File {config_file} non trovato e variabile d'ambiente DISCORD_TOKEN non impostata")
            logger.error("Imposta DISCORD_TOKEN come variabile d'ambiente o crea config.toml")
        except KeyError:
            logger.error(f"File {config_file} trovato ma chiave 'secret_token' mancante")
        except Exception as e:
            logger.error(f"Errore: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.critical("Interrupted. Shutting down.")
        quit()
