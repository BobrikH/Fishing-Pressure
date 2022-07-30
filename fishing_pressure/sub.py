dcc.Graph(
                    figure={
                        "data": [
                            {
                                "x": abcis,
                                "y": ordinat,
                                "type": "lines",
                            },
                        ],
                        "layout": {"title": "Изменение давления за день"},
                    },
                    style={
                        "width": "500px",
                        "height": "500px"
                    }
                )