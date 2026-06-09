import bcchapi
import requests
import pandas as pd

siete = bcchapi.Siete("simonrubio20@gmail.com","Contr2026")

def obtener_valor_dolar():
    
    df = siete.cuadro(
        series=["F073.TCO.PRE.Z.D"],
        nombres=["dolar"]
    )
    valor_dolar = df["dolar"].dropna().iloc[-1]
    return valor_dolar

