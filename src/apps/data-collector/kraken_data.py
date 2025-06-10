import os
import sys
import json
import time
import boto3
import yaml
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../clients")))
from kraken_python_client import KrakenPythonClient


class KrakenOrderBookCollector:
    def __init__(self, config_path: str, bucket_name: str):
        self.kraken = KrakenPythonClient()
        self.pairs = [
                        "XBTEUR",
                        "XBTUSD",
                        "ETHUSD",
                        "ETHEUR",
                        "USDTUSD",
                        "USDTEUR",
                        "SOLEUR",
                        "SOLUSD",
                        "ADAEUR",
                        "ADAUSD",
                        "XRPEUR",
                        "XRPUSD",
                        "DOTEUR",
                        "DOTUSD",
                        "LTCEUR",
                        "LTCUSD",
                        "BCHEUR",
                        "BCHUSD",
                        "MATICEUR",
                        "MATICUSD",
                        "AVAXEUR",
                        "AVAXUSD",
                        "LINKEUR",
                        "LINKUSD",
                        "ATOMEUR",
                        "ATOMUSD",
                        "DOGEEUR",
                        "DOGEUSD",
                        "TRXEUR",
                        "TRXUSD",
                        "ETCEUR",
                        "ETCUSD",
                        "UNIEUR",
                        "UNIUSD",
                        "XMREUR",
                        "XMRUSD",
                        "ALGOEUR",
                        "ALGOUSD",
                        "EOSEUR",
                        "EOSUSD",
                        "AAVEEUR",
                        "AAVEUSD",
                        "DAIEUR",
                        "DAIUSD",
                        "FILEUR",
                        "FILUSD",
                        "XTZUSD",
                        "XTZEUR",
                        "ZECEUR",
                        "ZECUSD",
                        "SUSHIEUR",
                        "SUSHIUSD",
                        "SNXEUR",
                        "SNXUSD",
                        "COMPEUR",
                        "COMPUSD",
                        "CRVEUR",
                        "CRVUSD",
                        "MKREUR",
                        "MKRUSD",
                        "YFIEUR",
                        "YFIUSD",
                        "GRTEUR",
                        "GRTUSD",
                        "CHZEUR",
                        "CHZUSD",
                        "ENJEUR",
                        "ENJUSD",
                        "BATEUR",
                        "BATUSD",
                        "RENEUR",
                        "RENUSD",
                        "KNCEUR",
                        "KNCUSD",
                        "OMGEUR",
                        "OMGUSD",
                        "1INCHEUR",
                        "1INCHUSD",
                        "ZRVEUR",
                        "ZRXUSD",
                        "ANKREUR",
                        "ANKRUSD",
                        "BALEUR",
                        "BALUSD",
                        "BNTEUR",
                        "BNTUSD",
                        "CELEUR",
                        "CELUSD",
                        "DASHEUR",
                        "DASHUSD",
                        "FETEUR",
                        "FETUSD",
                        "FLOWEUR",
                        "FLOWUSD",
                        "ICXEUR",
                        "ICXUSD",
                        "KAVAEUR",
                        "KAVAUSD",
                        "LRCEUR",
                        "LRCUSD",
                        "NEAREUR",
                        "NEARUSD",
                        "NANOEUR",
                        "NANOUSD",
                        "OCEANEUR",
                        "OCEANUSD",
                        "QTUMEUR",
                        "QTUMUSD",
                        "RLCEUR",
                        "RLCUSD",
                        "SKLEUR",
                        "SKLUSD",
                        "SRMEUR",
                        "SRMUSD",
                        "STORJEUR",
                        "STORJUSD",
                        "STXEUR",
                        "STXUSD",
                        "SXPEUR",
                        "SXPUSD",
                        "THETAEUR",
                        "THETAUSD",
                        "WAVESEUR",
                        "WAVESUSD",
                        "XEMEUR",
                        "XEMUSD",
                        "XLMEUR",
                        "XLMUSD",
                        "YGGEUR",
                        "YGGUSD",
                        "GHSTEUR",
                        "GHSTUSD",
                        "INJEUR",
                        "INJUSD",
                        "KSMEUR",
                        "KSMUSD",
                        "MINAEUR",
                        "MINAUSD",
                        "NUEUR",
                        "NUUSD",
                        "PAXGEUR",
                        "PAXGUSD",
                        "RUNEEUR",
                        "RUNEUSD",
                        "SANDEUR",
                        "SANDUSD",
                        "SCEUR",
                        "SCUSD",
                        "USDCUSD",
                        "USDCEUR",
                        "VETEUR",
                        "VETUSD",
                        "WTCEUR",
                        "WTCUSD",
                        "EURQUSD",
                        "EURQEUR"
                    ]
  
        aws_credentials = self._load_aws_credentials(config_path)
        session = boto3.Session(
            aws_access_key_id=aws_credentials['api_key'],
            aws_secret_access_key=aws_credentials['api_secret']
        )
        self.s3 = session.client('s3')
        self.bucket = bucket_name

    def _load_pairs(self, path):
        with open(path, 'r') as f:
            return json.load(f)

    def _load_aws_credentials(self, config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config['aws']

    def _utc_timestamp(self) -> str:
        return datetime.utcnow().isoformat()

    def _upload_to_s3(self, pair: str, bid: str, ask: str):
        timestamp = self._utc_timestamp()
        key = f"{pair}/{timestamp}.json"
        data = {'time': timestamp, 'bid': bid, 'ask': ask}
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=json.dumps(data))

    def _fetch_snapshot(self, pair: str):
        print(f'starting for {pair}')
        try:
            bid = self.kraken.get_bid(pair)
            ask = self.kraken.get_ask(pair)
            if bid and ask:
                self._upload_to_s3(pair, bid, ask)
            else:
                print(f'Error occured during fetch_snapshot: {bid}, {ask}')
        except Exception as e:
            print(f'Error occured during fetch_snapshot: {e}')

    def collect_once(self):
        for pair in self.pairs:
            self._fetch_snapshot(pair)

    def collect_continuous(self, interval: float = 1.0):
        i = 0
        while True:
            print(f'Saving... iteration: {i}')
            self.collect_once()
            time.sleep(interval)
            i+=1

    def get_data(self, pair: str):
        paginator = self.s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=self.bucket, Prefix=f"{pair}/")
        results = []
        for page in pages:
            for obj in page.get('Contents', []):
                key = obj['Key']
                body = self.s3.get_object(Bucket=self.bucket, Key=key)['Body'].read()
                results.append(json.loads(body.decode()))
        return results
