import os
import re
import json
from utils import database as db


class CorpusExtractor:
    def __init__(self, raw_directory):
        self.db_manager = db.DatabaseManager()
        self.raw_dir = raw_directory

    def get_corpuses(self):
        corpuses = self.db_manager.get_corpuses()
        return [corp[3] for corp in corpuses]

    def find_next_available_filename(self):
        pattern = re.compile(r'corpus(\d+)\.json')
        files = os.listdir(self.raw_dir)
        used_nums = {int(match.group(1)) for match in (pattern.match(f) for f in files) if match}
        max_num = max(used_nums) if used_nums else 0
        return f'corpus{next((num for num in range(1, max_num + 2) if num not in used_nums), 1)}.json'

    def save_corpuses(self, filename, corpuses):
        with open(os.path.join(self.raw_dir, filename), 'w') as file:
            json.dump(corpuses, file, indent=2)
            print(f'Exported {len(corpuses)} corpuses to {filename}')

    def run_extraction(self):
        corpuses = self.get_corpuses()
        filename = self.find_next_available_filename()
        self.save_corpuses(filename, corpuses)


# Example usage:
if __name__ == "__main__":
    extractor = CorpusExtractor('../../data/raw/')
    extractor.run_extraction()
