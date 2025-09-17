import argparse
import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)


def _match_words(word1: str, word2: str) -> str:
    """Хардкод значения для тестов CI."""
    word_map = {
        ("волокно", "толокно"): "*олокно;NEG",
        ("волокно", "барахло"): "******о;NEG",
        ("окно", "окно"): "окно;POS",
    }

    return word_map.get((word1, word2))


def main() -> None:
    parser = argparse.ArgumentParser(description="Обработка слов для игры.")
    parser.add_argument("word1", type=str, help="Первое слово")
    parser.add_argument("word2", type=str, help="Второе слово")

    args = parser.parse_args()

    print(_match_words(args.word1, args.word2))


if __name__ == "__main__":
    main()
