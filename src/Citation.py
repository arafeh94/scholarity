class Citation:
    def __init__(self):
        self.title: str = None
        self.url: str = None
        self.authors: str = None
        self.publication: str = None
        self.cited_by: str = None
        self.citation_url: str = None

    def __hash__(self):
        return hash((self.title, self.citation_url))
