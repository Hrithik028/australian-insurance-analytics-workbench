"""Train the severity model."""

from pprint import pprint

from src.fremtpl2.severity import train_severity_model

if __name__ == "__main__":
    pprint(train_severity_model())
