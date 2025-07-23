import pandas as pd
from report_additions import (
    insert_resumen_ejecutivo,
    insert_metricas_clave_simplificadas,
    insert_metricas_avanzadas,
    insert_alertas_reglas,
    insert_deteccion_fatiga,
)


def _build_sample_df():
    dates = pd.date_range('2024-06-01', periods=14)
    rows = []
    for i, d in enumerate(dates):
        # two ads, a1 and a2
        for ad in ['A1', 'A2']:
            spend = 10 if ad == 'A1' else 5
            value = 20 if d < dates[7] else 15 if ad == 'A1' else 10 if d < dates[7] else 8
            impr = 10 if ad == 'A1' else 5
            reach = 2 if ad == 'A1' else 1
            clicks = 0.2 * impr if d < dates[7] else 0.1 * impr if ad == 'A1' else 0.05 * impr
            visits = clicks
            purchases = 1 if d.day % 3 == 0 else 0
            rv3 = 0.5 * impr
            rows.append({
                'date': d,
                'Anuncio': ad,
                'spend': spend,
                'value': value,
                'impr': impr,
                'reach': reach,
                'clicks': clicks,
                'visits': visits,
                'purchases': purchases,
                'rv3': rv3,
            })
    df = pd.DataFrame(rows)
    df['frequency'] = df['impr'] / df['reach']
    df['ctr'] = df['clicks'] / df['impr'] * 100
    return df


sample_df = _build_sample_df()


def test_resumen_ejecutivo_output():
    logs = []
    insert_resumen_ejecutivo(sample_df, logs.append)
    joined = "\n".join(logs)
    assert "## Resumen Ejecutivo" in joined
    assert "Tendencia principal" in joined
    assert "Alerta clave" in joined


def test_metricas_clave_simplificadas_table():
    logs = []
    insert_metricas_clave_simplificadas(sample_df, logs.append, "$")
    header = next((l for l in logs if l.startswith('| Métrica')), None)
    assert header is not None
    assert any('Spend' in l for l in logs)


def test_metricas_avanzadas_table():
    logs = []
    insert_metricas_avanzadas(sample_df, logs.append)
    lines = [l for l in logs if l.startswith('|')]
    assert len(lines) >= 3


def test_alertas_and_fatiga_sections():
    logs = []
    insert_alertas_reglas(sample_df, logs.append)
    insert_deteccion_fatiga(sample_df, logs.append)
    output = "\n".join(logs)
    assert "Alertas" in output
    assert "Detección" in output
