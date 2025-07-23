"""Utility functions to compute and append extra report sections."""

import pandas as pd
from datetime import timedelta
from formatting_utils import fmt_float, fmt_pct, fmt_int, variation, safe_division, safe_division_pct
from data_processing.metric_calculators import _calcular_metricas_agregadas_y_estabilidad


def _subset(df: pd.DataFrame, start_dt, end_dt):
    mask = (df['date'] >= start_dt) & (df['date'] <= end_dt)
    return df.loc[mask].copy()


def _metrics_for_period(df: pd.DataFrame, days: int):
    if df.empty or 'date' not in df.columns:
        return {}
    end_dt = df['date'].max()
    start_dt = end_dt - timedelta(days=days - 1)
    df_period = _subset(df, start_dt, end_dt)
    return _calcular_metricas_agregadas_y_estabilidad(df_period, days, log_func=None)


def insert_resumen_ejecutivo(df_daily: pd.DataFrame, log_func):
    """Generate an executive summary based on recent metrics."""
    if df_daily is None or df_daily.empty:
        log_func("## Resumen Ejecutivo")
        log_func("- Datos insuficientes para calcular tendencias")
        return

    current = _metrics_for_period(df_daily, 7)
    prev = _metrics_for_period(_subset(df_daily, df_daily['date'].max() - timedelta(days=13), df_daily['date'].max() - timedelta(days=7)), 7)

    roas_trend = variation(current.get('ROAS'), prev.get('ROAS'))

    recent = _subset(df_daily, df_daily['date'].max() - timedelta(days=2), df_daily['date'].max())
    ctr_hist = safe_division_pct(df_daily['clicks'].sum(), df_daily['impr'].sum())
    ad_stats = recent.groupby('Anuncio').agg({'frequency':'mean', 'ctr':'mean'}).reset_index()
    fatigued = ad_stats[(ad_stats['frequency']>6) & (ad_stats['ctr']*100 < ctr_hist)].shape[0]

    log_func("## Resumen Ejecutivo")
    log_func(f"- Tendencia principal: ROAS {roas_trend} vs. semana anterior")
    log_func(f"- Alerta clave: {fatigued} anuncios con frecuencia > 6 y CTR bajo")
    if fatigued:
        log_func("- Recomendación corta: Refrescar creativos fatigados")
    else:
        log_func("- Recomendación corta: Mantener estrategia actual")


def insert_metricas_clave_simplificadas(df_daily: pd.DataFrame, log_func, currency_symbol="$"):
    """Print simplified key metrics table for the last 7 days."""
    if df_daily is None or df_daily.empty:
        log_func("\n## Métricas Clave Simplificadas")
        log_func("No hay datos para mostrar.")
        return

    end_dt = df_daily['date'].max()
    current = _metrics_for_period(df_daily, 7)
    prev1 = _metrics_for_period(_subset(df_daily, end_dt - timedelta(days=13), end_dt - timedelta(days=7)), 7)
    prev2 = _metrics_for_period(_subset(df_daily, end_dt - timedelta(days=20), end_dt - timedelta(days=14)), 7)

    rows = [
        ["Spend", f"{currency_symbol}{fmt_float(current.get('Inversion',0),2)}", variation(current.get('Inversion'), prev1.get('Inversion')), variation(current.get('Inversion'), prev2.get('Inversion'))],
        ["ROAS", f"{fmt_float(current.get('ROAS',0),2)}x", variation(current.get('ROAS'), prev1.get('ROAS')), variation(current.get('ROAS'), prev2.get('ROAS'))],
        ["CTR", fmt_pct(current.get('CTR')), variation(current.get('CTR'), prev1.get('CTR')), variation(current.get('CTR'), prev2.get('CTR'))],
        ["CPA", f"{currency_symbol}{fmt_float(current.get('CPA',0),2)}", variation(current.get('CPA'), prev1.get('CPA')), variation(current.get('CPA'), prev2.get('CPA'))],
        ["Frecuencia", fmt_float(current.get('Frecuencia',0),2), variation(current.get('Frecuencia'), prev1.get('Frecuencia')), variation(current.get('Frecuencia'), prev2.get('Frecuencia'))],
        ["Visitas LP", fmt_int(current.get('Visitas',0)), variation(current.get('Visitas'), prev1.get('Visitas')), variation(current.get('Visitas'), prev2.get('Visitas'))],
    ]

    log_func("\n## Métricas Clave Simplificadas")
    header = "| Métrica | Actual | Δ vs. 1 Semana | Δ vs. 2 Semanas |"
    log_func(header)
    log_func("|---|---|---|---|")
    for r in rows:
        log_func(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} |")


def insert_metricas_avanzadas(df_daily: pd.DataFrame, log_func):
    """Print advanced metrics computed from the last 7 days."""
    if df_daily is None or df_daily.empty:
        log_func("\n## Métricas Avanzadas")
        log_func("No hay datos para mostrar.")
        return

    m = _metrics_for_period(df_daily, 7)

    ctr_decimal = (m.get('CTR') or 0) / 100
    freq = m.get('Frecuencia') or 1
    ctr_first = ctr_decimal / freq if freq else 0
    ctr_rep = ctr_decimal - ctr_first
    tsr = m.get('RV3_%', safe_division_pct(df_daily['rv3'].sum(), df_daily['impr'].sum()))

    last_day = _subset(df_daily, df_daily['date'].max(), df_daily['date'].max())
    roas_last = _calcular_metricas_agregadas_y_estabilidad(last_day, 1, log_func=None).get('ROAS')
    roas_7d = m.get('ROAS')
    delta_roas = variation(roas_last, roas_7d)

    log_func("\n## Métricas Avanzadas")
    log_func("| Métrica | Valor |")
    log_func("|---|---|")
    log_func(f"| CTR 1ª impresión vs. repeticiones | {fmt_pct(ctr_first*100)} / {fmt_pct(ctr_rep*100)} |")
    log_func(f"| Thumb‑Stop Rate (3s Views/Imp.) | {fmt_pct(tsr)} |")
    log_func(f"| Delta diario de ROAS (%) vs. 7d | {delta_roas} |")


def insert_alertas_reglas(df_daily: pd.DataFrame, log_func):
    """Evaluate basic rules and print a checklist."""
    if df_daily is None or df_daily.empty:
        log_func("\n## Alertas & Reglas Aplicadas")
        log_func("Sin datos para evaluar alertas.")
        return

    m7 = _metrics_for_period(df_daily, 7)
    active_days = df_daily['date'].nunique()
    imp_total = df_daily['impr'].sum()
    low_activity = active_days < 5 or imp_total < 1000

    cpa_obj = m7.get('CPA') or 0
    spent = m7.get('Inversion') or 0
    purchases = m7.get('Compras') or 0
    no_conv = purchases == 0 and spent >= 1.5 * cpa_obj if cpa_obj else False

    freq_high = m7.get('Frecuencia', 0) > 6
    prev7 = _metrics_for_period(_subset(df_daily, df_daily['date'].max() - timedelta(days=13), df_daily['date'].max() - timedelta(days=7)), 7)
    ctr_drop = (m7.get('CTR') or 0) < (prev7.get('CTR') or 0)

    log_func("\n## Alertas & Reglas Aplicadas")
    log_func(f"- [{'✔︎' if low_activity else '✖︎'}] Días activos < 5 o impresiones < 1 000")
    log_func(f"- [{'✔︎' if no_conv else '✖︎'}] Sin conversiones tras gasto ≥ 1.5× CPA_objetivo")
    log_func(f"- [{'✔︎' if (freq_high and ctr_drop) else '✖︎'}] Frecuencia > 6 y CTR ↓")


def insert_deteccion_fatiga(df_daily: pd.DataFrame, log_func):
    """Detect possible ad fatigue using last 3 days vs history."""
    if df_daily is None or df_daily.empty or 'Anuncio' not in df_daily.columns:
        log_func("\n## Detección de Fatiga")
        log_func("No hay datos de anuncios para analizar.")
        return

    end_dt = df_daily['date'].max()
    last3 = _subset(df_daily, end_dt - timedelta(days=2), end_dt)
    hist_ctr = df_daily.groupby('Anuncio')['ctr'].mean()
    last3_ctr = last3.groupby('Anuncio')['ctr'].mean()
    last3_freq = last3.groupby('Anuncio')['frequency'].mean()

    df_comb = pd.DataFrame({
        'freq': last3_freq,
        'ctr3': last3_ctr,
        'ctr_hist': hist_ctr
    }).dropna()

    df_comb['fatiga'] = (df_comb['freq'] > 6) & (df_comb['ctr3'] < df_comb['ctr_hist'])
    top = df_comb.sort_values('freq', ascending=False).head(5)

    log_func("\n## Detección de Fatiga")
    log_func("| Anuncio | Frecuencia | CTR 3d | CTR Hist. | Fatiga |")
    log_func("|---|---|---|---|---|")
    for idx, row in top.iterrows():
        log_func(
            f"| {idx} | {fmt_float(row['freq'],2)} | {fmt_pct(row['ctr3'])} | {fmt_pct(row['ctr_hist'])} | {'Sí' if row['fatiga'] else 'No'} |")


def insert_matriz_decision(log_func):
    log_func("\n## Matriz de Decisión")
    log_func("Si (Frecuencia > 6 Y CTR ↓) → Refrescar creativo")
    log_func("Si (CPA > 1.5×CPA_obj Y compras = 0) → Pausar anuncio")
    log_func("Si (TSR < 20 %) → Cambiar hook de video")
