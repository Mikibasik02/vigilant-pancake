import asyncio
import tomllib
import sys
import logging
import os
from threading import Thread
from flask import Flask

# Disabilita la voce per evitare errori con audioop
os.environ["DISCORD_INSTANCE_NO_VOICE"] = "true"

from tampermint.bot import start_bot


logger = logging.getLogger(__name__)

# Crea una semplice app Flask per il keep-alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

async def main():
    logging.basicConfig(filename="bot.log", encoding="utf-8", level=logging.DEBUG)
    logger.info("Starting main.")
    
    # Avvia il server web fittizio (Render vedrà la porta aperta)
    keep_alive()
    logger.info("Keep-alive server started.")

    token = os.getenv("DISCORD_TOKEN")
    if token:
        logger.info("Token trovato nella variabile d'ambiente DISCORD_TOKEN")
        await start_bot(token)
    else:
        logger.info("Variabile d'ambiente non trovata, cerco nel file config.toml")
        try:
            config_file = sys.argv[1] if len(sys.argv) > 1 else "config.toml"
            with open(config_file, "rb") as f:
                config = tomllib.load(f)
            logger.info("Configuration file loaded.")
            await start_bot(config["secret_token"])
        except FileNotFoundError:
            logger.error(f"File {config_file} non trovato e variabile d'ambiente DISCORD_TOKEN non impostata")
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
