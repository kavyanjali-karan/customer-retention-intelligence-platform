let
    Source = Csv.Document(
        File.Contents("..\data\dim_customer.csv"),
        [
            Delimiter=",",
            Encoding=65001,
            QuoteStyle=QuoteStyle.None
        ]
    ),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true])
in
    Headers