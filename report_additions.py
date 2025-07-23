"""Utility functions to append extra sections to the text reports."""


def insert_resumen_ejecutivo(log_func):
    """Insert the executive summary block."""
    log_func("## Resumen Ejecutivo")
    log_func("- Tendencia principal (p.\u202Fej. \"ROAS \u2191 25 % vs. semana anterior\")")
    log_func("- Alerta clave (p.\u202Fej. \"3 anuncios con frecuencia >\u202F6 y CTR \u2193\")")
    log_func("- Recomendación corta (p.\u202Fej. \"Refrescar creativos fatigados\")")


def insert_metricas_clave_simplificadas(log_func):
    """Add simplified key metrics table."""
    log_func("\n## Métricas Clave Simplificadas")
    log_func("| Métrica      | Actual | Δ vs. 1\u202FSemana | Δ vs. 2\u202FSemanas |")
    log_func("|--------------|--------|----------------|-----------------|")
    log_func("| Spend        | …      | …              | …               |")
    log_func("| ROAS         | …      | …              | …               |")
    log_func("| CTR          | …      | …              | …               |")
    log_func("| CPA          | …      | …              | …               |")
    log_func("| Frecuencia   | …      | …              | …               |")
    log_func("| Visitas LP   | …      | …              | …               |")


def insert_metricas_avanzadas(log_func):
    """Add advanced metrics table."""
    log_func("\n## Métricas Avanzadas")
    log_func("| Métrica                          | Valor  |")
    log_func("|----------------------------------|--------|")
    log_func("| CTR 1ª impresión vs. repeticiones | … / … |")
    log_func("| Thumb‑Stop Rate (3\u202Fs Views/Imp.)  | … %   |")
    log_func("| Delta diario de ROAS (%) vs. 7\u202Fd  | … %   |")


def insert_alertas_reglas(log_func):
    """Add alerts and applied rules section."""
    log_func("\n## Alertas & Reglas Aplicadas")
    log_func("- [✔︎/✖︎] Días activos <\u202F5 o impresiones <\u202F1\u202F000")
    log_func("- [✔︎/✖︎] Sin conversiones tras gasto ≥\u202F1.5×\u202FCPA_objetivo")
    log_func("- [✔︎/✖︎] Frecuencia >\u202F6 y CTR \u2193")


def insert_deteccion_fatiga(log_func):
    """Add fatigue detection mini-table."""
    log_func("\n## Detección de Fatiga")
    log_func("| Anuncio       | Frecuencia | CTR 3\u202Fd | CTR Hist. | Fatiga |")
    log_func("|---------------|------------|---------|-----------|--------|")
    log_func("| Nombre_Ad_1   | …          | … %     | … %       | Sí/No  |")
    log_func("| Nombre_Ad_2   | …          | … %     | … %       | Sí/No  |")


def insert_matriz_decision(log_func):
    """Add decision matrix at the end of the report."""
    log_func("\n## Matriz de Decisión")
    log_func("Si (Frecuencia > 6 Y CTR \u2193) → Refrescar creativo")
    log_func("Si (CPA > 1.5×CPA_obj Y compras = 0) → Pausar anuncio")
    log_func("Si (TSR < 20\u202F%) → Cambiar hook de video")
