let
    Source = Csv.Document(
        File.Contents("..\..\data\curated\fact_customer_activity.csv"),
        [
            Delimiter=",",
            Encoding=65001,
            QuoteStyle=QuoteStyle.None
        ]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    Headers