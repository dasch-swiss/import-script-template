from loguru import logger

from src.utils.logger_config import logger_config


def main() -> None:
    logger.info("Hello, world!")


if __name__ == "__main__":
    logger_config()
    main()
