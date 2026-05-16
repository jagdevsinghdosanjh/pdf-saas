from dataclasses import dataclass

@dataclass
class User:
    id: str
    email: str

@dataclass
class Plan:
    id: str
    slug: str
    name: str
    price_monthly: int
    max_file_size_mb: int
    max_files_per_merge: int
    ocr_enabled: bool
