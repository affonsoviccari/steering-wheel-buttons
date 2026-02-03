import logging

# Mapeamento de cores ANSI
COLORS = {
    "DEBUG": "\033[37m",   # branco
    "INFO": "\033[36m",    # ciano
    "WARNING": "\033[33m", # amarelo
    "ERROR": "\033[31m",   # vermelho
    "CRITICAL": "\033[41m" # fundo vermelho
}
RESET = "\033[0m"

class ColorFormatter(logging.Formatter):
    def format(self, record):
        log_color = COLORS.get(record.levelname, RESET)
        formatter = logging.Formatter(
            f"%(asctime)s {log_color}[%(levelname)s]{RESET} "
            f"\033[35m%(name)s{RESET}: "
            f"\033[37m%(message)s{RESET}"
        )
        return formatter.format(record)

def setup_logging():
    handler = logging.StreamHandler()
    handler.setFormatter(ColorFormatter())
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = [handler] 