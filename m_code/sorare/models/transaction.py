from attrs import define

@define
class Transaction:
    """A representation of a sorare account transaction"""
    payload: dict
    current_user_slug: str

    def process_payload(self):
        print(self.payload.get("entryType"))
        if self.payload.get("entryType") == "PAYMENT":
            print(self.payload)
        return self