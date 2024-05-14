import os
import json
from discoverable.utils import database as db


class CorpusExtractor:
    def __init__(self, raw_directory):
        self.db_manager = db.DatabaseManager()
        self.raw_dir = raw_directory
        self.output_file = os.path.join(self.raw_dir, 'db_dump.json')

    def get_corpuses(self):
        corpuses = self.db_manager.get_corpuses()
        return [corp[3] for corp in corpuses]

    def save_corpuses(self, corpuses):
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, 'w') as file:
            json.dump(corpuses, file, indent=2)
            print(f'Exported {len(corpuses)} corpuses to {self.output_file}')

    def run_extraction(self):
        corpuses = self.get_corpuses()
        self.save_corpuses(corpuses)


if __name__ == "__main__":
    extractor = CorpusExtractor('../../data/db_dumps/')
    extractor.run_extraction()