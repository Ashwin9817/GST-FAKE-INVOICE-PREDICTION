"""
GSTIN (Goods and Services Tax Identification Number) Generator.
Generates structurally valid synthetic GSTIN strings following the Indian GSTIN schema.
Format: [2 Digit State Code] [5 Alpha PAN] [4 Numeric PAN] [1 Alpha PAN Check] [1 Entity Digit] [Z] [1 Checksum]
Example: 27ABCDE1234F1Z5
"""

import random
import string
from data_generator.config import STATE_CODES

class GSTINGenerator:
    """Generates synthetic GSTIN numbers adhering to standard structural patterns."""

    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
        self.state_code_keys = list(STATE_CODES.keys())

    def generate_gstin(self, state_code: str = None) -> tuple[str, str]:
        """
        Generates a valid-looking synthetic GSTIN and returns (gstin, state_name).
        """
        if not state_code or state_code not in STATE_CODES:
            state_code = random.choice(self.state_code_keys)

        state_name = STATE_CODES[state_code]

        # 5 letters (3 random + 1 entity type like 'C' for Company, 'P' for Person + 1 first letter of surname)
        pan_letters = "".join(random.choices(string.ascii_uppercase, k=3)) + random.choice(["C", "P", "F", "H", "A"]) + random.choice(string.ascii_uppercase)
        # 4 digits
        pan_digits = "".join(random.choices(string.digits, k=4))
        # 1 check letter
        pan_check = random.choice(string.ascii_uppercase)
        # 1 entity code
        entity_code = str(random.randint(1, 9))
        # Constant character 'Z'
        z_char = "Z"
        # Checksum character (alphanumeric)
        checksum = random.choice(string.ascii_uppercase + string.digits)

        gstin = f"{state_code}{pan_letters}{pan_digits}{pan_check}{entity_code}{z_char}{checksum}"
        return gstin, state_name

    def generate_batch(self, count: int) -> list[dict]:
        """
        Generates a batch of distinct business entities with GSTIN metadata.
        """
        entities = []
        seen_gstins = set()

        while len(entities) < count:
            gstin, state_name = self.generate_gstin()
            if gstin in seen_gstins:
                continue
            seen_gstins.add(gstin)

            state_code = gstin[:2]
            entities.append({
                "gstin": gstin,
                "state_code": state_code,
                "state": state_name,
            })

        return entities
