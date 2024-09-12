

class BearerToken:
    def __init__(self,token,expiry) -> None:
        self.token = token
        self.expiry = expiry

    def __repr__(self) -> str:
        return f"<BearerToken token={self.token} expiry={self.expiry}>"