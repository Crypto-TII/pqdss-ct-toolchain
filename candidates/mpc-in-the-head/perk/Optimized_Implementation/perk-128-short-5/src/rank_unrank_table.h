/**
 * @file rank_unrank_table.h
 * @brief Look-up table used in rank/unrank compression, encoding in base-62
 */

#ifndef SIG_PKP_RANK_UNRANK_TABLE_H
#define SIG_PKP_RANK_UNRANK_TABLE_H

// clang-format off
static char* factorial[] = {
    "1",
    "1",
    "2",
    "6",
    "O",
    "1w",
    "Bc",
    "1JI",
    "AUK",
    "1WOu",
    "FE12",
    "2hUBM",
    "WPqCG",
    "6nPwZM",
    "1X9rDyy",
    "N1NsNkW",
    "5wMA280G",
    "1d04kaC4O",
    "TK1NWVVGy",
    "8z8QCxeaCO",
    "2tiiSBF5fzk",
    "ys93Xo6vDua",
    "LbDDFzmSIw4m",
    "80ntuvuyV1Xlo",
    "36JJe2Q3Q0b4VM",
    "1FXmv8yVNUEwods",
    "WWAVxlN9qgGfEie",
    "EA0Zv1d5HwPFxPRQ",
    "6OWGDkjeO6NPCpUNk",
    "2zT5aQrLtGywn05D6W",
    "1Rk4hczoakDURi2WL9U",
    "is2LoUuIN6kDr1GAZk0",
    "N9tDG3x3TvTr9MeLSRk0",
    "CKGO3Y6QqvatHz3TQ8lU0",
    "6l6zBwhWj1aEJrTu8Ko2S0",
    "3oawXk8ZTPtS5DBsghkFNo0",
    "2DNRzamyb52CJ1etknOqvp20",
    "1JyzhkxEA80JLLzPGvTpaVSC0",
    "oFNoomIgCuBr5TdUNEHcNHHM0",
    "VbfyxwNkY7LSORdq6bz58druq0",
    "KOJ5KffK20jqJlphcGVPJZimfY0",
    "DU4cWfYKFKUJb4dBqIuljwccBTU0",
    "98N8689FiNsXH78Y1QoSL7i9rlyK0",
    "6Ko2cFePtmYp4rwvazazeeLcqIGps0",
    "4UlVr96gNaSiFSHosFiFkqdLZ6xwoK0",
    "3GKU7Zbql7Sq7DWvvNP7R0CYeU3VgWW0",
    "2Q7CLcQ58xXOfM2QyZMdW29Ji2IbVY7k0",
    "1pnSMO7ltn8JhLhqRuo9xHd3wNk6Qurrs0",
    "1Q6HxKg15C2RFYnwbbyphteF3CNgyq1hho0",
    "17cyBtLCr6VvXIVTJj14rgyntWmiy57LXcW0",
    "u9QXad6MpFkOqvNduIrvIf2EmRIGS7vN73o0",
    "kBkpd8AEm9xARXCRpJWM8Lkq9qS1X8WC0o880",
    "cjrHIoqaOOLcl5qRL2N8Z0FHkFzVHn904g2oi0",
    "X7CXn5Sx6qoU8FzpMz1mJvD4AXfZkD0h3zwPLc0",
    "SqGvQklDTxzyFBvqk19Y5LpNdBKD8FKbVTws4p60",
    "PaN0wjTsxaDyRTaJmp1TEkMZxl2veJbHGvZDyHKK0",
    "N6qmr34zdoicaoins65KPJsOTyUe4PhfbHzocReM40",
    "LFIWulpafbd1TqdBqjatlHH0VYcAq3d9FHXpXLQ6Hg0",
    "JsJKn6kGIvCVNvEf5KeWAE9uTWNi8hOceIPeDC2PsXI0",
    "IugOmjQ1W0QtrlSx64eYbjTQk5oZ0HIQmLWPGYSIctg80",
    "IIr1z9xBSyQ241w1BsVFUW0TsbcvsGjpumpMS1LO1dslk0",
    "I0YAxAnEHVRc1xu5AgckF1UTOj1IwOT64s2X5ZK2dcEsyG0",
    "I0YAxAnEHVRc1xu5AgckF1UTOj1IwOT64s2X5ZK2dcEsyG00",
    "IIYj87y1Vmx3dzrzFrJMzGVxs7kKFKrZAwuZcetMgFr7rEG00",
    "It9qaODxYoWxlHrjEN1zjF2znrzotpXIJIoOluD9PcMq6wiW00",
    "JnpK89OdRUyYeZjKQ495iQm8nHboMX1uCEipyDvmrrDwdHYfY00",
    "L52dQg0DzGyStC2FjkPg5IVFMSkFbzA1p1fjK6pW1KeqPoguEC00",
    "MmRqbpOF7DLLDe0R0R9kTizlbH3ys35py8o5yjNfbRK8dtmMlKy00",
    "Oz8XhUMaZudPGxsTcTmgybLkCsiMlHOOzxewYblxd3y5TlB2xuzo00",
    "Ro2VVOn8hy1r7sdcxp9BpRZCQKtNKcM9oxOZAW2NMTPs67VIIgQme00",
    "VOUpZRzTpdm5ytgjzXkNM57k1jaWLHJ15X3jhsAgNNDD4uTKf5uEvA00",
    "Zx3J3b3PA8Y4qjlwfTe6kHrrhzCp2MomFKrHLF2EWla7ycfaf3lP5SS00",
    "fkZq8B1xDlvZdF9g8AQZpkkYN54tGkUy1oDs8fSas3FxGOuIZgN38L2W00",
    "n9qCNczIjDQmxCqObcHIBw2oTAyl4ikSg88KkCofPdpmmJKHs0t8golxg00",
    "wfkImCXALy1yQfKXMtgdiFHMEp6WBdPSEHhwl9ITQbXoDf4DKT3oN6bFE800",
    "18yV0iJA7WZcO6FzqMhMa2WTztvosw4fn9HQA52FLbBPtkWg67l9bvwz3Q5g00",
    "1P0A0sJUPDvf3XfboBp9gB5olsYsNLBjEFNM4MAkoTZzkL23bVVnmV2IqByxU00",
    "1k3CR5SClKIbzOofxKgX1NmE3SlJWzJZAh60PPXM8gjhgY7YTa8UpEXrOoshsG00",
    "2Bw1e4rU3XXPnFDkme1VXjufgMBWZV8cFSDYVy7xqvlUxWvVNDSgmSIbBE0pCG800",
    "2nCw64C9IVjZrkOWbyzvBzVD6yGgVEfyjgxGyjc9GRbWRqxGya9YVk3hNIr3EcYC00",
    "3bUgxpPfzswoHLre50htnTMGuzlWqIwAMxQTuMrDxDcPrwKTuAeKWxQly4KSArk7U00",
    "4hz68AAXrqmpgfZ5MXvLtdM66Sh5uKjzXzdb4drXEMnBnTCl4Nugp3dyfTeioCDFmC00",
    "6EAo6nRwnDoaMQyP5orqxa3E4XwzoVQpOxWN28inx093bQcsFncydWosErDrGO9Wrjs00",
    "8KyT56CPhtUig26ran65tlGJq5Rykc4uoPgKprfyrzC7p6e2d9RBAuw6btFYIwKkzwPI00"};

#endif  // SIG_PKP_RANK_UNRANK_TABLE_H
