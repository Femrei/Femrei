"""Profil README'sindeki proje kartlarını üretir.

Her kart tek dosyadır ve prefers-color-scheme ile koyu/açık temaya kendisi uyar
(GitHub, <a> içindeki <picture> etiketini bozduğu için).

Çalıştırma:  python scripts/build_cards.py
Çıktı:       assets/cards/<slug>.svg  (+ öne çıkan PAYDA kartı: assets/cards/payda.svg)
"""
import re
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets" / "cards"

THEMES = {
    "dark":  {"T": "#e6edf3", "M": "#7d8590", "A": "#f0a23b", "R": "#30363d", "INK": "#0d1117", "BG": "#0d1117"},
    "light": {"T": "#1f2328", "M": "#656d76", "A": "#b45309", "R": "#d0d7de", "INK": "#ffffff", "BG": "#ffffff"},
}
VARS = {k: f"var(--{k.lower()})" for k in THEMES["dark"]}

W, H = 440, 200

# Her illüstrasyon sağdaki 290..420 x 46..160 alanına çizilir.
ART = {
    # sohbet balonları + bağlam hafızası
    "chat": """
      <rect x="296" y="56" width="92" height="30" fill="none" stroke="{M}"/>
      <line x1="304" y1="67" x2="370" y2="67" stroke="{M}" stroke-width="3"/><line x1="304" y1="76" x2="348" y2="76" stroke="{M}" stroke-width="3"/>
      <rect x="326" y="96" width="94" height="30" fill="none" stroke="{A}"/>
      <line x1="334" y1="107" x2="410" y2="107" stroke="{A}" stroke-width="3"/><line x1="334" y1="116" x2="386" y2="116" stroke="{A}" stroke-width="3"/>
      <text x="296" y="150" font-size="10" fill="{M}">memory</text>
      <g fill="{A}"><rect x="342" y="143" width="8" height="8" class="b1"/><rect x="354" y="143" width="8" height="8" class="b2"/><rect x="366" y="143" width="8" height="8" class="b3"/><rect x="378" y="143" width="8" height="8" class="b4"/></g>
    """,
    # taranan belge + operasyon grafiği
    "docs": """
      <rect x="296" y="54" width="70" height="94" fill="none" stroke="{M}"/>
      <g stroke="{M}" stroke-width="3"><line x1="304" y1="68" x2="356" y2="68"/><line x1="304" y1="80" x2="346" y2="80"/><line x1="304" y1="92" x2="356" y2="92"/><line x1="304" y1="104" x2="338" y2="104"/><line x1="304" y1="116" x2="352" y2="116"/></g>
      <line x1="292" y1="60" x2="370" y2="60" stroke="{A}" stroke-width="2" class="scan"/>
      <line x1="378" y1="148" x2="422" y2="148" stroke="{R}"/>
      <rect x="382" y="118" width="9" height="30" fill="{A}" opacity=".45" class="grow"/>
      <rect x="395" y="96" width="9" height="52" fill="{A}" opacity=".7" class="grow"/>
      <rect x="408" y="76" width="9" height="72" fill="{A}" class="grow"/>
    """,
    # deprem merkezi + yayılan halkalar + saha düğümleri
    "quake": """
      <g stroke="{R}" stroke-width="1" stroke-dasharray="3 3">
        <line x1="300" y1="70" x2="345" y2="100"/><line x1="345" y1="100" x2="405" y2="64"/>
        <line x1="345" y1="100" x2="398" y2="146"/><line x1="345" y1="100" x2="306" y2="140"/>
      </g>
      <g fill="{M}"><circle cx="300" cy="70" r="3"/><circle cx="405" cy="64" r="3"/><circle cx="398" cy="146" r="3"/><circle cx="306" cy="140" r="3"/></g>
      <circle cx="345" cy="100" r="8" fill="none" stroke="{A}" class="ring"/>
      <circle cx="345" cy="100" r="8" fill="none" stroke="{A}" class="ring r2"/>
      <circle cx="345" cy="100" r="4" fill="{A}"/>
      <text x="420" y="166" font-size="10" fill="{M}" text-anchor="end">risk · hasar · ihbar</text>
    """,
    # uydu karoları: hasar seviyeleri + yol çizgisi
    "road": "",  # aşağıda programatik üretiliyor
    # perspektif yol + tespit edilen şerit alanı + direksiyon oku
    "lane": """
      <path d="M296 156 L346 60 L364 60 L424 156 Z" fill="{A}" opacity=".18" class="pulse"/>
      <line x1="296" y1="156" x2="346" y2="60" stroke="{A}" stroke-width="2.5"/>
      <line x1="424" y1="156" x2="364" y2="60" stroke="{A}" stroke-width="2.5"/>
      <line x1="355" y1="150" x2="355" y2="64" stroke="{M}" stroke-width="2" stroke-dasharray="8 8" class="dash"/>
      <path d="M355 140 Q357 112 368 92" fill="none" stroke="{T}" stroke-width="1.5"/>
      <path d="M362 90 L371 87 L370 96" fill="none" stroke="{T}" stroke-width="1.5"/>
      <text x="420" y="54" font-size="10" fill="{M}" text-anchor="end">steer</text>
    """,
    # uyarı levhası + tespit kutusu
    "sign": """
      <path d="M355 70 L392 136 L318 136 Z" fill="none" stroke="{T}" stroke-width="5" stroke-linejoin="round"/>
      <text x="355" y="128" font-size="30" font-weight="700" fill="{T}" text-anchor="middle">!</text>
      <rect x="306" y="58" width="98" height="90" fill="none" stroke="{A}" stroke-width="2" class="draw"/>
      <g class="pop"><rect x="306" y="44" width="56" height="14" fill="{A}"/>
      <text x="310" y="54" font-size="10" font-weight="700" fill="{INK}">warning</text></g>
    """,
    # N-katmanlı mimari + katmanları kesen yeni modül
    "tier": """
      <g font-size="10">
        <rect x="296" y="56" width="124" height="20" fill="none" stroke="{R}"/><text x="302" y="70" fill="{M}">presentation</text>
        <rect x="296" y="80" width="124" height="20" fill="none" stroke="{R}"/><text x="302" y="94" fill="{M}">service</text>
        <rect x="296" y="104" width="124" height="20" fill="none" stroke="{R}"/><text x="302" y="118" fill="{M}">data</text>
        <rect x="296" y="128" width="124" height="20" fill="none" stroke="{R}"/><text x="302" y="142" fill="{M}">core</text>
      </g>
      <rect x="384" y="50" width="26" height="104" fill="{A}" opacity=".9" class="pop"/>
      <text x="397" y="102" font-size="10" font-weight="700" fill="{INK}" text-anchor="middle" transform="rotate(-90 397 102)">brand</text>
    """,
    # orkestratör + üç uzman ajan
    "agents": """
      <g stroke="{M}" stroke-width="1.2" stroke-dasharray="4 4" class="dash">
        <line x1="358" y1="80" x2="312" y2="128"/><line x1="358" y1="80" x2="358" y2="128"/><line x1="358" y1="80" x2="404" y2="128"/>
      </g>
      <rect x="330" y="56" width="56" height="24" fill="{A}"/>
      <text x="358" y="72" font-size="10" font-weight="700" fill="{INK}" text-anchor="middle">orkestra</text>
      <g fill="none" stroke="{A}" stroke-width="1.5"><circle cx="312" cy="136" r="8" class="b1"/><circle cx="358" cy="136" r="8" class="b2"/><circle cx="404" cy="136" r="8" class="b3"/></g>
      <g font-size="9" fill="{M}" text-anchor="middle"><text x="312" y="160">takip</text><text x="358" y="160">içgörü</text><text x="404" y="160">koç</text></g>
    """,
}


def road_art():
    # 6x4 karo; değer = hasar seviyesi (0 sağlam .. 3 yıkık)
    grid = [
        [0, 0, 1, 0, 0, 0],
        [0, 1, 2, 1, 0, 0],
        [0, 0, 3, 2, 1, 0],
        [0, 0, 1, 1, 0, 0],
    ]
    op = {1: 0.3, 2: 0.6, 3: 1.0}
    parts = []
    for r, row in enumerate(grid):
        for c, v in enumerate(row):
            x, y = 296 + c * 21, 56 + r * 21
            parts.append(f'<rect x="{x}" y="{y}" width="19" height="19" fill="none" stroke="{{R}}"/>')
            if v:
                parts.append(f'<rect x="{x}" y="{y}" width="19" height="19" fill="{{A}}" opacity="{op[v]}" class="pop"/>')
    parts.append('<polyline points="296,108 338,100 359,108 380,122 422,126" fill="none" stroke="{T}" stroke-width="2"/>')
    parts.append('<text x="296" y="160" font-size="10" fill="{M}">sağlam · kısmi · yıkık</text>')
    return "\n".join(parts)


ART["road"] = road_art()

# Sıra README'deki sıradır.
CARDS = [
    {
        "slug": "doktor-asistani", "no": "01", "name": "DOKTOR ASİSTANI", "tag": "llm · konuşma hafızası", "art": "chat",
        "lines": ["Gemini ve LangChain üzerine kurulu,", "kullanıcısını tanıyan ve konuşma", "hafızasıyla bağlamı koruyan akıllı",
                  "sağlık asistanı; terminalden ve", "FastAPI REST servisinden çalışır."],
        "stack": "gemini · langchain · fastapi · prompt eng.",
    },
    {
        "slug": "digicobig", "no": "02", "name": "DIGICOBIG", "tag": "google yzta · ai saas", "art": "docs",
        "lines": ["KOBİ ve kooperatifler için uzman", "AI ajanları, RAG ve multimodal", "belge ve fatura okumayla stok,",
                  "lojistik ve operasyonu tek yerden", "yöneten akıllı işletme platformu."],
        "stack": "ai agents · rag · gemini · fastapi",
    },
    {
        "slug": "quakemind", "no": "03", "name": "QUAKEMIND", "tag": "tübitak 2209-a", "art": "quake",
        "lines": ["TÜBİTAK 2209-A desteği alan afet", "yönetim platformu: uydudan yol", "hasarı segmentasyonu, YOLO ile bina",
                  "ve çatlak tespiti, BERTurk ile ihbar", "analizi, CatBoost ile risk skoru."],
        "stack": "segformer · yolo · berturk · catboost · fastapi",
    },
    {
        "slug": "road-disaster", "no": "04", "name": "ROAD DISASTER", "tag": "uydu · segmentasyon", "art": "road",
        "lines": ["Deprem sonrası uydu görüntülerinde", "UNet tabanlı derin öğrenmeyle yol", "hasarını piksel düzeyinde çıkarıp",
                  "OSM yol ağıyla birleştiren ve", "harita üstünde gösteren sistem."],
        "stack": "pytorch · unet · hugging face · osm · streamlit",
    },
    {
        "slug": "lane-keeping", "no": "05", "name": "LANE KEEPING", "tag": "teknofest · otonom araç", "art": "lane",
        "lines": ["TEKNOFEST Otonom Araç yarışması", "için geliştirilen; klasik görüntü", "işleme ve geometriyle gerçek",
                  "zamanlı şerit takibi ve direksiyon", "kestirimi yapan modüler sistem."],
        "stack": "python · opencv · numpy · oop",
    },
    {
        "slug": "sign-detection", "no": "06", "name": "SIGN DETECTION", "tag": "deep learning · cv", "art": "sign",
        "lines": ["Trafik levhalarını gerçek zamanlı", "ve yüksek doğrulukla tanıyan;", "YOLOv11, YOLOv8 ve Faster R-CNN",
                  "mimarilerini kıyaslayan, özel veri", "setli ve arayüzlü tespit sistemi."],
        "stack": "pytorch · ultralytics · albumentations",
    },
    {
        "slug": "nopcommerce", "no": "07", "name": "NOPCOMMERCE", "tag": "staj · kurumsal .net", "art": "tier",
        "lines": ["Kurumsal e-ticaret platformu", "nopCommerce'e, çekirdeğe dokunmadan", "N-katmanlı mimarinin tüm",
                  "katmanlarına entegre edilen DI ve", "Repository desenli marka modülü."],
        "stack": "c# · asp.net core mvc · di · sql",
    },
    {
        "slug": "carbon", "no": "08", "name": "CARBON", "tag": "multi-agent · yzta", "art": "agents",
        "lines": ["Orkestratörün yönettiği Takip,", "İçgörü ve Koç ajanlarıyla karbon", "ayak izini hesaplayan, eğilimleri",
                  "analiz eden ve hafızasıyla kişisel", "öneriler üreten çok ajanlı koç."],
        "stack": "multi-agent · llm · gemini · docker",
    },
]

STYLE = """
  :root { {LIGHT}; }
  @media (prefers-color-scheme: dark) { :root { {DARK}; } }
  text { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; }
  .draw { stroke-dasharray: 380; stroke-dashoffset: 380; animation: draw 1s .3s cubic-bezier(.6,0,.2,1) forwards; }
  .pop { opacity: 0; animation: fade .4s 1.1s forwards; }
  .ring { transform-origin: 345px 100px; animation: ring 2s ease-out infinite; }
  .r2 { animation-delay: 1s; }
  .pulse { animation: pulse 2.4s ease-in-out infinite; }
  .dash { animation: dash 1s linear infinite; }
  .scan { animation: scan 2.4s ease-in-out infinite alternate; }
  .grow { transform-box: fill-box; transform-origin: bottom; animation: grow 1s .4s cubic-bezier(.2,.8,.2,1) both; }
  .flow { stroke-dasharray: 4 6; animation: dash 1.2s linear infinite; }
  .b1, .b2, .b3, .b4 { opacity: .25; animation: blink 2s infinite; }
  .b2 { animation-delay: .25s; } .b3 { animation-delay: .5s; } .b4 { animation-delay: .75s; }
  @keyframes draw { to { stroke-dashoffset: 0; } }
  @keyframes fade { to { opacity: 1; } }
  @keyframes ring { from { transform: scale(1); opacity: 1; } to { transform: scale(5); opacity: 0; } }
  @keyframes pulse { 50% { opacity: .32; } }
  @keyframes dash { to { stroke-dashoffset: -20; } }
  @keyframes scan { to { transform: translateY(84px); } }
  @keyframes grow { from { transform: scaleY(0); } }
  @keyframes blink { 0%, 60%, 100% { opacity: .25; } 30% { opacity: 1; } }
  @media (prefers-reduced-motion: reduce) {
    .draw { animation: none; stroke-dashoffset: 0; }
    .pop { animation: none; opacity: 1; }
    .ring, .pulse, .dash, .scan, .grow, .flow, .b1, .b2, .b3, .b4 { animation: none; }
  }
"""


def css_vars(theme):
    return "; ".join(f"--{k.lower()}: {v}" for k, v in THEMES[theme].items())


def style_block():
    return STYLE.replace("{LIGHT}", css_vars("light")).replace("{DARK}", css_vars("dark"))


def vars_to_style(svg):
    # Sunum özniteliklerinde var() geçersiz; fill/stroke'u style'a taşı.
    def fix(m):
        tag = m.group(0)
        decl = re.findall(r'\s(fill|stroke)="(var\([^)]+\))"', tag)
        if not decl:
            return tag
        tag = re.sub(r'\s(fill|stroke)="var\([^)]+\)"', "", tag)
        style = ";".join(f"{k}:{v}" for k, v in decl)
        return re.sub(r"(/?>)$", lambda e: f' style="{style}"{e.group(1)}', tag, count=1)
    return re.sub(r"<[a-z]+\b[^<>]*>", fix, svg)


def frame(w, h, c):
    return (
        f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" fill="{c["BG"]}" stroke="{c["R"]}"/>'
        f'<path d="M0 12 V0 H12 M{w - 12} 0 H{w} V12 M{w} {h - 12} V{h} H{w - 12} M12 {h} H0 V{h - 12}" '
        f'fill="none" stroke="{c["A"]}" stroke-width="2"/>'
    )


def render(card, c):
    lines = "".join(
        f'<text x="20" y="{72 + i * 18}" font-size="12" fill="{c["T"]}">{escape(t)}</text>'
        for i, t in enumerate(card["lines"])
    )
    art = ART[card["art"]].format(**c)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(card['name'])}">
<style>{style_block()}</style>
{frame(W, H, c)}
<text x="20" y="34" font-size="12" font-weight="700" fill="{c['A']}">{card['no']}</text>
<text x="44" y="34" font-size="15" font-weight="700" fill="{c['T']}">{escape(card['name'])}</text>
<text x="{W - 20}" y="34" font-size="10" fill="{c['M']}" text-anchor="end">{escape(card['tag'])}</text>
<line x1="20" y1="46" x2="{W - 20}" y2="46" stroke="{c['R']}"/>
{lines}
{art}
<line x1="20" y1="172" x2="{W - 20}" y2="172" stroke="{c['R']}"/>
<text x="20" y="190" font-size="10" fill="{c['M']}">{escape(card['stack'])}</text>
<text x="{W - 20}" y="190" font-size="10" fill="{c['A']}" text-anchor="end">repo →</text>
</svg>
"""


# ── Öne çıkan proje: PAYDA ────────────────────────────────────────────────
PW, PH = 880, 404

PAYDA_ROWS = [
    ("backend", ".NET · EF Core · PostgreSQL RLS · Redis"),
    ("veri", "ETL/ELT · DuckDB · PySpark · feature store"),
    ("ml", "öneri motoru · segmentasyon · talep tahmini"),
    ("dl", "PyTorch two-tower · Türkçe Transformer"),
    ("llm · rag", "yerel LLM · pgvector RAG · kaynaklı cevap"),
    ("ajanlar", "router · araç çağıran uzman ajan takımı"),
    ("mlops", "model registry · kalite kapısı · eval seti"),
]


def box(x, y, w, h, label, c, accent=False):
    stroke = c["A"] if accent else c["R"]
    fill = c["A"] if accent else "none"
    ink = c["INK"] if accent else c["T"]
    weight = ' font-weight="700"' if accent else ""
    return (
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}"/>'
        f'<text x="{x + w / 2}" y="{y + h / 2 + 4}" font-size="10" fill="{ink}" text-anchor="middle"{weight}>{escape(label)}</text>'
    )


def render_payda(c):
    # Sol: çalışma zamanı mimarisi
    ch = [("kasa", 128), ("web", 158), ("whatsapp", 188), ("panel", 218)]
    parts = [f'<text x="24" y="118" font-size="10" fill="{c["M"]}">kanallar</text>']
    for label, y in ch:
        parts.append(box(24, y, 76, 22, label, c))
        parts.append(f'<path d="M100 {y + 11} C120 {y + 11} 116 186 136 186" fill="none" stroke="{c["M"]}" class="flow"/>')
    parts.append(box(136, 172, 84, 28, "yarp gateway", c))
    svc = [(".net api ×2", 128, False), ("ajan servisi", 172, True), ("ml servisi", 216, False)]
    for label, y, acc in svc:
        parts.append(f'<path d="M220 186 C240 186 236 {y + 14} 256 {y + 14}" fill="none" stroke="{c["A"] if acc else c["M"]}" class="flow"/>')
        parts.append(box(256, y, 108, 28, label, c, acc))
    parts.append(f'<text x="372" y="190" font-size="9" fill="{c["M"]}">llm · rag</text>')
    parts.append(f'<text x="372" y="202" font-size="9" fill="{c["M"]}">ajanlar</text>')
    data = [("postgresql · rls", 24, 112), ("pgvector", 144, 76), ("redis", 228, 56), ("ollama", 292, 64), ("hangfire", 364, 64)]
    for _, x, w in data:
        parts.append(f'<line x1="{x + w / 2}" y1="256" x2="{x + w / 2}" y2="286" stroke="{c["R"]}" class="flow"/>')
    parts.append(f'<line x1="24" y1="256" x2="428" y2="256" stroke="{c["R"]}"/>')
    for label, x, w in data:
        parts.append(box(x, 286, w, 26, label, c))
    parts.append(f'<text x="24" y="334" font-size="10" fill="{c["M"]}">çok kiracılı · kiracı izolasyonu veritabanında (row level security)</text>')

    # Sağ: yetenek tablosu
    parts.append(f'<line x1="452" y1="112" x2="452" y2="340" stroke="{c["R"]}"/>')
    for i, (label, value) in enumerate(PAYDA_ROWS):
        y = 130 + i * 32
        parts.append(f'<g class="row" style="animation-delay:{0.2 + i * 0.12:.2f}s">'
                     f'<text x="470" y="{y}" font-size="11" font-weight="700" fill="{c["A"]}">{escape(label)}</text>'
                     f'<text x="556" y="{y}" font-size="12" fill="{c["T"]}">{escape(value)}</text></g>')

    body = "\n".join(parts)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{PW}" height="{PH}" viewBox="0 0 {PW} {PH}" role="img" aria-label="PAYDA: Perakende Ajanlarıyla Yapay zekâ Destekli Alışveriş">
<style>{style_block()}
  .row {{ opacity: 0; animation: fade .4s forwards; }}
  @media (prefers-reduced-motion: reduce) {{ .row {{ animation: none; opacity: 1; }} }}
</style>
{frame(PW, PH, c)}
<text x="24" y="40" font-size="13" font-weight="700" fill="{c['A']}">00</text>
<text x="52" y="40" font-size="24" font-weight="700" fill="{c['T']}">PAYDA</text>
<text x="146" y="40" font-size="12" fill="{c['M']}">Perakende Ajanlarıyla Yapay zekâ Destekli Alışveriş</text>
<g><rect x="{PW - 134}" y="24" width="110" height="20" fill="none" stroke="{c['A']}"/>
<text x="{PW - 79}" y="38" font-size="10" font-weight="700" fill="{c['A']}" text-anchor="middle">geliştiriliyor</text></g>
<line x1="24" y1="58" x2="{PW - 24}" y2="58" stroke="{c['R']}"/>
<text x="24" y="86" font-size="13" fill="{c['T']}">Zincir marketler ve toptancılar için yapay zekâ ajanlı, çok kiracılı (multi-tenant) SaaS platformu.</text>
{body}
<line x1="24" y1="360" x2="{PW - 24}" y2="360" stroke="{c['R']}"/>
<text x="24" y="382" font-size="10" fill="{c['M']}">asp.net core · fastapi · postgresql · duckdb · pyspark · ollama · langgraph · pytorch · docker · aws</text>
<text x="{PW - 24}" y="382" font-size="10" fill="{c['A']}" text-anchor="end">multi-tenant saas</text>
</svg>
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.svg"):
        old.unlink()
    for card in CARDS:
        (OUT / f"{card['slug']}.svg").write_text(vars_to_style(render(card, VARS)), encoding="utf-8")
    (OUT / "payda.svg").write_text(vars_to_style(render_payda(VARS)), encoding="utf-8")
    print(f"{len(CARDS) + 1} kart yazildi")


if __name__ == "__main__":
    main()
