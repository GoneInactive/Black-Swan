class StartStrategy:
    def __init__(self, strategy: str, exchange: str, *args, **kwargs):
        self.strategy = strategy
        self.exchange = exchange
        self.args = args
        self.kwargs = kwargs

    def start(self):
        print(f'Starting {self.strategy} on {self.exchange}...')


