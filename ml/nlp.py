from transformers import pipeline


class SentimentAnalyser:

    __instance = None

    @staticmethod
    def get():
        if SentimentAnalyser.__instance == None:
            SentimentAnalyser()
        return SentimentAnalyser.__instance

    def __init__(self) -> None:

        if SentimentAnalyser.__instance != None:
            raise Exception("This is a singleton")
        else:
            SentimentAnalyser.__instance = self

        self.sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

    def is_positive(self, utterance):
        result = self.sentiment_pipeline(utterance)
        _result = [r for r in result if r["label"]
                   == "POSITIVE" and r["score"] > 0.5]
        if _result:
            return True
        return False
