"""3D katkı grafiğinden dil halkasını çıkarır.

github-profile-3d-contrib, halkayı kodun diline göre değil, commit sayısını reponun
"ana dili" hanesine yazarak çiziyor; HTML ağırlıklı takım repoları yüzünden halka
yanıltıcı oluyor ve aracın bunu kapatan bir ayarı yok.

Çalıştırma:  python scripts/strip_pie.py profile-3d-contrib/*.svg
"""
import sys
import xml.etree.ElementTree as ET

ET.register_namespace("", "http://www.w3.org/2000/svg")


def strip(path):
    tree = ET.parse(path)
    root = tree.getroot()
    # Halka, sol alttaki en üst seviye grup: transform="translate(40, ...)".
    pies = [c for c in root if c.tag.endswith("}g") and c.get("transform", "").startswith("translate(40,")]
    for g in pies:
        root.remove(g)
    tree.write(path, encoding="utf-8", xml_declaration=False)
    return len(pies)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        print(f"{p}: {strip(p)} halka çıkarıldı")
